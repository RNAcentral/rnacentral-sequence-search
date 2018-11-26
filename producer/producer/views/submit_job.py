"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import json
import datetime

import logging
import aiohttp
from aiohttp import web

from ..models import Job, JobChunk


def serialize(request, data):
    """Validates and normalizes input data."""
    try:
        query = data['query']
        databases = data['databases']
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(text='Bad input') from e

    # validate query
    for char in data['query']:
        if char not in ['A', 'T', 'G', 'C', 'U']:
            raise web.HTTPBadRequest(
                text="Input query should be a nucleotide sequence"
                     " and contain only {ATGCU} characters, found: '%s'." % data['query']
            )

    # normalize query: convert nucleotides to RNA
    data['query'] = data['query'].replace('T', 'U')

    # validate databases
    for database in data['databases']:
        if database.lower() not in request.app['settings'].RNACENTRAL_DATABASES:
            raise web.HTTPBadRequest(text="Database '%s' not in list of RNAcentral databases" % database)

    # normalize databases: convert them to lower case
    data['databases'] = [datum.lower() for datum in data['databases']]

    return data


async def save(connection, request, data):
    """Save metadata about this job and job_chunks to the database."""
    job_id = await connection.scalar(
        Job.insert().values(query=data['query'], submitted=datetime.datetime.now(), status='started')
    )
    for database in data['databases']:
        job_chunk_id = await connection.scalar(
            JobChunk.insert().values(job_id=job_id, database=database, submitted=datetime.datetime.now(), status='pending')
        )

    return job_id


async def delegate(connection, request, data, job_id):
    """Send job chunks to consumers, if sent successfully - update status of each JobChunk in the database."""
    for database in data["databases"]:
        url = "http://" + request.app['settings'].CONSUMERS[database] + '/' + request.app['settings'].CONSUMER_SUBMIT_JOB_URL
        json_data = json.dumps({"job_id": job_id, "sequence": data['query'], "database": database})
        headers = {'content-type': 'application/json'}

        logging.debug("Queuing JobChunk to consumer: url = {}, json_data = {}, headers = {}".format(url, json_data, headers))

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=json_data, headers=headers) as response:
                    if response.status < 400:
                        await connection.execute(
                            '''
                            UPDATE {job_chunks}
                            SET status = 'started'
                            WHERE job_id={job_id} AND database='{database}';
                            '''.format(job_chunks='job_chunks', job_id=job_id, database=database)
                        )
                    else:
                        text = await response.text()
                        job_chunk_id = await connection.scalar(
                            JobChunk.insert().values(job_id=job_id, database=database, submitted=datetime.datetime.now(), status='error')
                        )
                        raise web.HTTPBadRequest(text=text)
        except Exception as e:
            return web.HTTPBadGateway(text=str(e))


async def submit_job(request):
    """
    Example:
    curl -H "Content-Type:application/json" -d "{\"databases\": [\"miRBase\"], \"query\": \"AGGUCAGGAGUUUGAGACCAGCCUGGCCAA\"}" localhost:8002/api/submit-job

    ---
    tags:
    - jobs
    summary: Accepts a job for execution
    requestBody:
      content:
        application/json:
          schema:
            type: object
            required:
             - query
             - databases
            properties:
              query:
                description: Nucleotide sequence to search for
                type: string
              databases:
                description: List of RNAcentral member databases to search the query sequence against
                type: array
                items:
                  type: string
          examples:
            mirBase:
              summary: Search a miRNA against mirbase
              value:
                databases:
                 - miRBase
                query: 'AGGUCAGGAGUUUGAGACCAGCCUGGCCAA'
    responses:
      '201':
        description: Job accepted.
        content:
          application/json: {}
      '400':
        description: Invalid input (either query is not a nucleotide sequence, or databases not in RNAcentral)
    """

    data = await request.json()
    data = serialize(request, data)

    async with request.app['engine'].acquire() as connection:
        job_id = await save(connection, request, data)
        await delegate(connection, request, data, job_id)

    return web.json_response({"job_id": job_id}, status=201)

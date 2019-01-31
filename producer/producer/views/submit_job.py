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
import sqlalchemy as sa

from ..models import Job, JobChunk
from ..db.consumers import delegate_job_chunk_to_consumer, set_consumer_status, find_available_consumers
from ..db.jobs import save_job
from ..db.job_chunks import save_job_chunk


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


async def save(request, data):
    """Save metadata about this job and job_chunks to the database."""
    job_id = await save_job(request.app['engine'], data['query'])
    if job_id:
        for database in data['databases']:
            job_chunk_id = await save_job_chunk(request.app['engine'], job_id, database)
    return job_id


async def get_job_chunk_by_job_id_and_database(request, job_id, database):
    async with request.app['engine'].acquire() as connection:
        query = sa.text('''  
            SELECT id
            FROM job_chunks
            WHERE job_id={job_id} AND database='{database}'
        ''').format(job_id=job_id, database=database)
        result = await connection.execute(query)

        return result


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

    job_id = await save(request, data)

    consumers = await find_available_consumers(request.app['engine'])
    databases_copy = data['databases']

    async for consumer in consumers:
        try:
            await delegate_job_chunk_to_consumer(
                engine=request.app['engine'],
                consumer_ip=consumer.ip,
                job_id=job_id,
                database=databases_copy.pop(),
                query=data['query']
            )
        except Exception as e:
            return web.HTTPBadGateway(text=str(e))

    return web.json_response({"job_id": job_id}, status=201)

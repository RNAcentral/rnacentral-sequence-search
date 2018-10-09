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
import requests

from aiojobs.aiohttp import spawn
import aiohttp_jinja2
from aiohttp import web, client
from sqlalchemy import and_

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
            raise web.HTTPBadRequest(text="Database '%s' not in list of RNACentral databases" % data['database'])

    # normalize databases: convert them to lower case
    data['databases'] = [datum.lower() for datum in data['databases']]

    return data


async def save(request, data):
    """Save metadata about this job and job_chunks to the database."""
    job_id = await request.app['connection'].scalar(
        Job.insert().values(query=data['query'], submitted=datetime.datetime.now(), status='started')
    )
    for database in data['databases']:
        job_chunk_id = await request.app['connection'].scalar(
            JobChunk.insert().values(job_id=job_id, database=database, submitted=datetime.datetime.now(), status='started')
        )

    return job_id


async def delegate(request, data, job_id):
    """Send job chunks to consumers, if sent successfully - update status of each JobChunk in the database."""
    for database in data["databases"]:
        # TODO: replace requests with async client.request
        requests.post(
            url="http://" + request.app['settings'].CONSUMERS[database] + '/' + request.app['settings'].CONSUMER_SUBMIT_JOB_URL,
            data=json.dumps({"job_id": job_id, "sequence": data['query'], "database": database })
        )

        await request.app['connection'].scalar(
            JobChunk.update().where(and_(job_id == job_id, database == database)).values(status='running')
        )


async def submit_job(request):
    """
    Example:
    curl -H "Content-Type:application/json" -d "{\"databases\": [\"miRBase\"], \"query\": \"AGGCTCGGAGTCGTAGCTAT\"}" localhost:8002/submit-job

    :param request:
    :return:
    """

    data = await request.json()
    data = serialize(request, data)

    job_id = await save(request, data)

    await delegate(request, data, job_id)

    return web.HTTPCreated()

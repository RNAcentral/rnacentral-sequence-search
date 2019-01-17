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

import sqlalchemy as sa
from aiohttp import web
import logging

from ..models import Job, JobChunk, JobChunkResult
from ..db.consumers import set_consumer_status, delegate_job_to_consumer
from ..db.job_chunks import find_highest_priority_job_chunk, set_job_chunk_status, set_job_chunk_results, get_consumer_ip_from_job_chunk
from ..db.jobs import check_job_chunks_status, set_job_status, get_job_query


async def serialize(connection, request, data):
    """Expected data: {"job_id": job_id, "database": database, "result": ""}"""
    try:
        job_id = data['job_id']
        database = data['database']
        result = data['result']
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(text='Bad input') from e

    jobs = await connection.execute('''
        SELECT *
        FROM {job}
        WHERE id={job_id}
    '''.format(job='jobs', job_id=data['job_id']))

    if data['database'].lower() not in request.app['settings'].RNACENTRAL_DATABASES:
        raise web.HTTPBadRequest(text="Database '%s' not in list of RNACentral databases" % data['database'])
    data['database'] = data['database'].lower()

    return data


async def job_done(request):
    """
    Saves a job chunk to the database. If this was the last chunk,
    aggregates the results from all job chunks into job.
    """
    data = await request.json()

    async with request.app['engine'].acquire() as connection:
        data = await serialize(connection, request, data)

        # update job_chunk status, get job_chunk_id
        job_chunk_id = set_job_chunk_status(request.app['engine'], data['job_id'], data['database'], status='success')
        if job_chunk_id is None:
            raise web.HTTPBadRequest(text="Job chunk, you're trying to update, is non-existent")

        # get consumer_ip
        consumer_ip = get_consumer_ip_from_job_chunk(request.app['engine'], job_chunk_id)

        # save job chunk results
        set_job_chunk_results(request.app['engine'], data['job_id'], data['database'], data['result'])

        # if the whole job's done, update its status
        all_job_chunks_success = await check_job_chunks_status(request.app['engine'], data['job_id'])
        if all_job_chunks_success:
            set_job_status(request.app['engine'], data['job_id'], 'success')

        # if there are any pending jobs, try scheduling another job chunk for this consumer
        (job_id, job_chunk_id, database) = find_highest_priority_job_chunk(request.app['engine'])
        query = get_job_query(request.app['engine'], job_id)
        delegate_job_to_consumer(request.app['engine'], consumer_ip, job_id, database, query)

        return web.HTTPOk()

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
from aiohttp import web, client

from ..models import Job, JobChunk, JobChunkResult


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

        # update job_chunks
        query = sa.text('''
            UPDATE job_chunks
            SET status = 'success'
            WHERE job_id=:job_id AND database=:database
            RETURNING *;
        ''')
        result = await connection.execute(
            query,
            job_id=data['job_id'],
            database=data['database']
        )

        # get job_chunk_id from update query response
        for row in result:
            job_chunk_id = row.id
        if 'job_chunk_id' not in locals():
            raise web.HTTPBadRequest(text="Job chunk, you're trying to update, is non-existent")

        # save job chunk results
        for result in data['result']:
            await connection.scalar(
                JobChunkResult.insert().values(job_chunk_id=job_chunk_id, **result)
            )

        # check, if all other job chunks are also done - then the whole job is done
        query = (sa.select([Job.c.id, JobChunk.c.job_id, JobChunk.c.status])
                 .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                 .where(Job.c.id == data['job_id']))  # noqa

        all_job_chunks_success = True
        async for row in connection.execute(query):
            if row.status != 'success':
                all_job_chunks_success = False
                break

        if all_job_chunks_success:
            query = sa.text('''UPDATE jobs SET status = 'success' WHERE id=:job_id''')
            result = await connection.execute(query, job_id=data['job_id'])

        return web.HTTPOk()

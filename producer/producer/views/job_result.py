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

from aiohttp import web
import sqlalchemy as sa

from ..models import Job, JobChunk, JobChunkResult


async def job_result(request):
    job_id = request.match_info['job_id']

    try:
        # query = (sa.select([Job.c.id, JobChunk.c.job_id, JobChunk.c.database, JobChunkResult.c.rnacentral_id])
        #     .select_from(Job)
        #     .where(Job.c.id == job_id)
        #     .join(JobChunk, Job.c.id == JobChunk.c.job_id)  # noqa
        #     .join(JobChunk, JobChunkResult, JobChunk.c.id == JobChunkResult.c.job_chunk_id))  # noqa

        query = '''
            SELECT job.id, job_chunks.job_id, job_chunks.database, job_chunk_results.rnacentral_id
            FROM jobs
            JOIN job_chunks ON jobs.id=jon_chunks.job_id
            JOIN job_chunk_results ON job_chunks.id=job_chunks_results.job_chunk_id
            WHERE jobs.id = :job_id
        '''

        results = []
        async for row in request.app['connection'].execute(query, job_id=job_id):
            import pdb
            pdb.set_trace()
            print(row)
            results.append({
                'rnacentral_id': row[3]
            })

    except Exception as e:
        raise web.HTTPNotFound() from e

    return web.json_response(results)

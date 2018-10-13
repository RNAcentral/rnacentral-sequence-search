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
        query = (sa.select([Job.c.id, JobChunk.c.job_id, JobChunk.c.database, JobChunkResult.c.rnacentral_id])
            .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
            .select_from(sa.join(JobChunk, JobChunkResult, JobChunk.id == JobChunkResult.c.job_chunk_id))  # noqa
            .where(Job.c.id == job_id)
            .apply_labels())  # noqa

        results = []
        async for row in request.app['connection'].execute(query):
            import pdb
            pdb.set_trace()
            print(row)
            results.append({
                'rnacentral_id': row[3]
            })

    except Exception as e:
        raise web.HTTPNotFound() from e

    return web.json_response(results)

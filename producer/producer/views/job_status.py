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


async def job_status(request):
    job_id = request.match_info['job_id']

    try:
        query = '''
            SELECT {job}.id, {job_chunks}.status, {job_chunks}.database
            FROM {job}
            JOIN {job_chunks}
            ON {job_chunks}.job_id = job_id
            WHERE {job}.id={job_id}
        '''.format(job='jobs', job_chunks='job_chunks', job_id=int(job_id))

        chunks = []
        async for row in request.app['connection'].execute(query):
            status = row.status
            chunks.append({"database": row.database, "status": row.status})
    except Exception as e:
        raise web.HTTPNotFound() from e

    if 'status' not in locals():
        raise web.HTTPNotFound(text="Job '%s' not found" % job_id)

    return web.json_response({
        "job_id": job_id,
        "status": status,
        "chunks": chunks
    })

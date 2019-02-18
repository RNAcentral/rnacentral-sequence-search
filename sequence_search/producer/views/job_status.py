"""
Copyright [2009-2019] EMBL-European Bioinformatics Institute
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

from ...db.models import Job, JobChunk


async def job_status(request):
    """
    ---
    tags:
    - jobs
    summary: Shows the status of a job and its chunks
    parameters:
    - name: job_id
      in: path
      description: ID of job to display status for
      required: true
      schema:
        type: integer
    responses:
      '200':
        description: Successfully returns results
        content:
          application/json:
            schema:
              type: object
              properties:
                job_id:
                  type: integer
                status:
                  type: string
                chunks:
                  type: array
            example:
              {job_id: 1, status: "started", chunks: [{'database': 'mirbase', 'status': 'started'}, {'database': 'pombase', 'status': 'started'}]}
      '404':
        description: No status for given job_id (probably, job with this job_id doesn't exist)
    """
    job_id = request.match_info['job_id']

    try:
        async with request.app['engine'].acquire() as connection:
            select_statement = sa.select(
                [
                    Job.c.id.label('id'),
                    Job.c.status.label('job_status'),
                    JobChunk.c.job_id.label('job_id'),
                    JobChunk.c.database.label('database'),
                    JobChunk.c.status.label('job_chunk_status')
                ],
                use_labels=True
            )

            query = (select_statement
                     .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                     .where(Job.c.id == job_id))  # noqa

            chunks = []
            async for row in connection.execute(query):
                status = row.job_status
                chunks.append({
                    "database": row.database,
                    "status": row.job_chunk_status
                })
    except Exception as e:
        raise web.HTTPNotFound(text=str(e)) from e

    if 'status' not in locals():
        raise web.HTTPNotFound(text="Job '%s' not found" % job_id)

    return web.json_response({
        "job_id": job_id,
        "status": status,
        "chunks": chunks
    })

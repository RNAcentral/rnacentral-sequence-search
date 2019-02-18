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

from ...db.jobs import get_job_chunks_status, JobNotFound


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
        chunks = get_job_chunks_status(request.app['engine'], job_id)
    except JobNotFound as e:
        raise web.HTTPNotFound(text="Job '%s' not found" % job_id) from e

    return web.json_response({
        "job_id": job_id,
        "status": chunks[0].status,
        "chunks": chunks
    })

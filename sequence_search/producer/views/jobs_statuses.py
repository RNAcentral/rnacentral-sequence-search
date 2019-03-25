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

from ...db.jobs import get_jobs_statuses, SQLError, DatabaseConnectionError


async def jobs_statuses(request):
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
        type: string
    responses:
      '200':
        description: Successfully returns results
        content:
          application/json:
            schema:
              type: object
              properties:
                job_id:
                  type: string
                status:
                  type: string
                chunks:
                  type: array
            example:
              {
                job_id: "662c258b-04d8-4347-b8f5-3d9df82d769e",
                status: "started",
                chunks: [{'database': 'mirbase', 'status': 'started'}, {'database': 'pombase', 'status': 'started'}]
              }
      '404':
        description: No status for given job_id (probably, job with this job_id doesn't exist)
    """
    statuses = await get_jobs_statuses(request.app['engine'])

    return web.json_response(statuses)

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

import datetime

from aiohttp import web
from aiojobs.aiohttp import atomic

from ...db.jobs import get_job_chunks_status, JobNotFound


@atomic
async def job_status(request):
    """
    Function that returns the status and duration of the job
    :param request: used to get job_id and params to connect to the db
    :return: list of json object

    ---
    tags:
    - Jobs
    summary: Shows the status of a job and its chunks
    parameters:
    - name: job_id
      in: path
      description: Unique job identification
      type: string
      required: true
    responses:
      200:
        description: Ok
      404:
        description: Not found (probably, job with this job_id doesn't exist)
    """
    job_id = request.match_info['job_id']

    try:
        chunks = await get_job_chunks_status(request.app['engine'], job_id)
    except JobNotFound as e:
        raise web.HTTPNotFound(text="Job '%s' not found" % job_id) from e

    now = datetime.datetime.now()

    def elapsed_time(submitted, finished, now):
        if submitted is None:
            return 0
        elif finished is None:
            return (now - submitted).seconds
        else:
            return (finished - submitted).seconds

    data = {
        "job_id": job_id,
        "query": chunks[0]['query'],
        "description": chunks[0]['description'],
        "status": chunks[0]['job_status'],
        "r2dt_id": chunks[0]['r2dt_id'],
        "r2dt_date": (now - chunks[0]['r2dt_date']).total_seconds() if chunks[0]['r2dt_date'] else None,
        "elapsedTime": elapsed_time(chunks[0]['job_submitted'], chunks[0]['job_finished'], now),
        "now": str(datetime.datetime.now()),
        "chunks": [
            {
                'database': chunk['database'],
                'status': chunk['status'],
                'elapsedTime': elapsed_time(chunk['submitted'], chunk['finished'], now)
            } for chunk in chunks
        ]
    }

    return web.json_response(data)

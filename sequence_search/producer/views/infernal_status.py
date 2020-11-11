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

from ...db.jobs import get_infernal_job_status, JobNotFound


@atomic
async def infernal_status(request):
    """
    Function that returns the status and duration of the infernal job
    :param request: used to get job_id and params to connect to the db
    :return: json with job_id, status and elapsedTime of the infernal job

    ---
    tags:
    - Jobs
    summary: Shows the status of the infernal job
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
        infernal = await get_infernal_job_status(request.app['engine'], job_id)
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
        "status": infernal['status'],
        "elapsedTime": elapsed_time(infernal['submitted'], infernal['finished'], now),
        "now": str(datetime.datetime.now())
    }

    return web.json_response(data)

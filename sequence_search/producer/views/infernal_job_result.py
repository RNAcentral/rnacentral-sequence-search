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
from aiojobs.aiohttp import atomic

from ...db.jobs import get_infernal_job_results
from ...db import DatabaseConnectionError


@atomic
async def infernal_job_result(request):
    """
    Function that returns cmscan command results
    :param request: used to get job_id and params to connect to the db
    :return: list of json object

    ---
    tags:
    - Jobs
    summary: Shows the result of the infernal job
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
    engine = request.app['engine']

    try:
        results = await get_infernal_job_results(engine, job_id)
    except DatabaseConnectionError as e:
        raise web.HTTPNotFound() from e

    return web.json_response(results)

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

from ...db.jobs import get_job_results, JobNotFound


async def list_rnacentral_ids(request):
    # TODO: validate job_id and the fact that job finished
    job_id = request.match_info['job_id']

    # get sequence search results from the database, return as plaintext list
    results = await get_job_results(request.app['engine'], job_id)
    ids = [result['rnacentral_id'] for result in results]
    text = "\n".join(ids)
    return web.Response(text=text)

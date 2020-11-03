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

from ...db.jobs import save_r2dt_id


@atomic
async def r2dt(request):
    # Update the r2dt_id for a given search
    job_id = request.match_info['job_id']
    data = await request.json()
    r2dt_id = await save_r2dt_id(request.app['engine'], job_id, data['r2dt_id'], datetime.datetime.now())
    return web.json_response({"r2dt_id": r2dt_id}, status=201)

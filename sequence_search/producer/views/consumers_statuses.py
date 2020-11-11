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

from ...db.consumers import get_consumers_statuses, DatabaseConnectionError


@atomic
async def consumers_statuses(request):
    """
    Function to submit a query.
    :param request: used to get the params to connect to the db
    :return: list of json object

    ---
    tags:
    - Dashboard
    summary: Shows the status of a consumer
    parameters: []
    responses:
      200:
        description: Ok
      404:
        description: Not Found
    """
    try:
        consumers = await get_consumers_statuses(request.app['engine'])
    except DatabaseConnectionError as e:
        raise web.HTTPServerError() from e

    return web.json_response(consumers)

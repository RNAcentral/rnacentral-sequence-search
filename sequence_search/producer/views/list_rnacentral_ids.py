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

from ...db.jobs import get_job_results
from ..text_search_client import rnacentral_ids_file_path


@atomic
async def list_rnacentral_ids(request):
    """
    In order to have a text search, this endpoint has to pass a list of rnacentral_ids to
    EBI search (which will be able to provide facets then).

    In production environment list of rnacentral_ids is constructed from the database data.

    Other environments have to send a request to production machine's post-rnacentral-ids
    endpoint and it would save a list of rnacentral_ids in its cache directory.
    """
    # TODO: validate job_id and the fact that job finished
    job_id = request.match_info['job_id']

    # try getting ids list from cache first
    try:
        file = open(rnacentral_ids_file_path(job_id))
        data = file.read()
        return web.Response(text=data)
    except Exception as e:
        pass

    # try getting sequence search results from the database, return as plaintext list
    try:
        results = await get_job_results(request.app['engine'], job_id)
        ids = [result['rnacentral_id'] for result in results]
        if not ids:
            return web.HTTPNotFound()
        data = "\n".join(ids)
        return web.Response(text=data)
    except Exception as e:
        return web.HTTPNotFound()

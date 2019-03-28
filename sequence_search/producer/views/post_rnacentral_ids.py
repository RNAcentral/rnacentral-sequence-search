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

import os

from aiohttp import web

from ..text_search_client import rnacentral_ids_file_path


async def post_rnacentral_ids(request):
    """
    This is an endpoint used for local debugging of the frontend.

    When local producer is doing text search request, it posts a list of
    rnacentral_ids to the EMBASSY production producer machine, which caches it.

    This is because EBI text search endpoint is configured to get rnacentral_ids
    from EMBASSY floating ip.
    """
    job_id = request.match_info['job_id']

    if os.path.isfile(rnacentral_ids_file_path(job_id)):
        os.remove(rnacentral_ids_file_path(job_id))

    try:
        file = open(rnacentral_ids_file_path(job_id), 'wb')
        data = await request.content.read()
        file.write(data)
        file.flush()
        return web.HTTPCreated()
    except Exception as e:
        return web.HTTPBadRequest(text=str(e))

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

import logging

from aiohttp import web

from ...db.jobs import get_job_results
from ..text_search_client import get_text_search_results, ProxyConnectionError, EBITextSearchConnectionError


logger = logging.getLogger('aiohttp.web')


async def facets_search(request):
    """
    ---
    tags:
    - facets
    summary: Runs EBI text search for the results of sequence search and accompanies them with facets
    parameters:
    - name: job_id
      in: path
      description: ID of job to display results for
      required: true
      schema:
        type: integer
    responses:
      '200':
        description: Successfully returns results
        content:
          'application/json': {entries: [...], facets: [...], hitCount: integer}
      '404':
        description: No results for given job_id
      '502':
        description: Could not connect to EBI search proxy
    """
    job_id = request.match_info['job_id']

    query = request.query['query'] if 'query' in request.query else 'rna'
    page = request.query['page'] if 'page' in request.query else 1
    page_size = request.query['page_size'] if 'page_size' in request.query else 20

    # get sequence search results from the database, sort/aggregate?
    results = await get_job_results(request.app['engine'], job_id)

    # try to get facets from EBI text search, otherwise stub facets
    try:
        text_search_data = await get_text_search_results(results, job_id, query, page, page_size)

        # if this worked, inject text search results into facets json
        for entry in text_search_data['entries']:
            for result in results:
                if result['rnacentral_id'] == entry['id']:
                    entry.update(result)

    except (ProxyConnectionError, EBITextSearchConnectionError) as e:
        # text search is not available, pad output with facets stub, indicate that
        logger.warning(str(e))
        text_search_data = {'entries': [], 'facets': [], 'hitCount': len(results)}

        for result in results:
            # TODO: possibly update results fields, not sure about structure
            text_search_data['entries'].append(result)

    return web.json_response(text_search_data)


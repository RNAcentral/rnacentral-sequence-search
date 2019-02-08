"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
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
import aiohttp
from aiohttp import web
import sqlalchemy as sa

from ..models import Job, JobChunk, JobChunkResult
from ..db.jobs import get_job_results


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
          'application/json': {results: [...], facets: [...]}
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
    results = get_job_results(request.app['engine'], job_id)
    # TODO: sort/aggregate sequence search results?

    # send the list of rnacentral_ids to the proxy, fallback to returning the plain results, if text search unavailable
    rnacentral_ids = "\n".join([result['rnacentral_id'] for result in results])
    url = request.app['settings'].EBI_SEARCH_PROXY_URL + '/' + job_id
    headers = {'content-type': 'text/plain'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=rnacentral_ids, headers=headers) as response:
                if response.status >= 400:
                    raise web.HTTPBadGateway(text="Couldn't connect to text search proxy")
    except Exception as e:
        logging.error(str(e))
        return web.HTTPBadGateway(text=str(e))

    # request facets from ebi text search
    fields = [
        'active',
        'author',
        'common_name',
        'description',
        'expert_db',
        'function',
        'gene',
        'gene_synonym',
        'has_genomic_coordinates',
        'length',
        'locus_tag',
        'organelle',
        'pub_title',
        'product',
        'qc_warning_found',
        'qc_warning',
        'rna_type',
        'standard_name',
        'tax_string'
    ]

    facetfields = [
        'length',
        'rna_type',
        'TAXONOMY',
        'expert_db',
        'qc_warning_found',
        'has_genomic_coordinates',
        'popular_species'
    ]

    url = "http://wwwdev.ebi.ac.uk/ebisearch/ws/rest/rnacentral/seqtoolresults/" \
          "?toolid=rnac_nhmmer" \
          "&jobid={job_id}" \
          "&query={query}" \
          "&format=json&fields={fields}" \
          "&facetcount={facetcount}" \
          "&facetfields={facetfields}" \
          "&size={page_size}" \
          "&start={page}" \
        .format(job_id=job_id, query=query, fields=','.join(fields), facetcount=30, facetfields=','.join(facetfields), page=page, page_size=page_size)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status >= 400:
                    raise web.HTTPBadGateway(text=response.status)
                else:
                    text_search_data = await response.json()

                    # inject sequence search data into text_search_data
                    for entry in text_search_data['entries']:
                        for result in results:
                            if result['rnacentral_id'] == entry['id']:
                                entry.update(result)

                    return web.json_response(text_search_data)
    except Exception as e:
        logging.error(str(e))
        return web.HTTPBadGateway(text=str(e))

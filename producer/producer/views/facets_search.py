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

import aiohttp
from aiohttp import web
import sqlalchemy as sa

from ..models import Job, JobChunk, JobChunkResult


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

    # get sequence search results from the database
    try:
        async with request.app['engine'].acquire() as connection:
            sql = (sa.select([
                    JobChunk.c.job_id,
                    JobChunk.c.database,
                    JobChunkResult.c.rnacentral_id,
                    JobChunkResult.c.description,
                    JobChunkResult.c.score,
                    JobChunkResult.c.bias,
                    JobChunkResult.c.e_value,
                    JobChunkResult.c.target_length,
                    JobChunkResult.c.alignment,
                    JobChunkResult.c.alignment_length,
                    JobChunkResult.c.gap_count,
                    JobChunkResult.c.match_count,
                    JobChunkResult.c.nts_count1,
                    JobChunkResult.c.nts_count2,
                    JobChunkResult.c.identity,
                    JobChunkResult.c.query_coverage,
                    JobChunkResult.c.target_coverage,
                    JobChunkResult.c.gaps,
                    JobChunkResult.c.query_length,
                    JobChunkResult.c.result_id
                ])
                .select_from(sa.join(JobChunk, JobChunkResult, JobChunk.c.id == JobChunkResult.c.job_chunk_id))  # noqa
                .where(JobChunk.c.job_id == job_id))  # noqa

            results = []
            async for row in connection.execute(sql):
                results.append({
                    'rnacentral_id': row[2],
                    'description': row[3],
                    'score': row[4],
                    'bias': row[5],
                    'e_value': row[6],
                    'target_length': row[7],
                    'alignment': row[8],
                    'alignment_length': row[9],
                    'gap_count': row[10],
                    'match_count': row[11],
                    'nts_count1': row[12],
                    'nts_count2': row[13],
                    'identity': row[14],
                    'query_coverage': row[15],
                    'target_coverage': row[16],
                    'gaps': row[17],
                    'query_length': row[18],
                    'result_id': row[19]
                })

    except Exception as e:
        raise web.HTTPNotFound() from e

    # TODO: sort/aggregate sequence search results?

    # send the list of rnacentral_ids to the proxy
    rnacentral_ids = "\n".join([result['rnacentral_id'] for result in results])
    url = request.app['settings'].EBI_SEARCH_PROXY_URL + '/' + job_id
    headers = {'content-type': 'text/plain'}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=rnacentral_ids, headers=headers) as response:
                if response.status >= 400:
                    raise web.HTTPBadGateway(text="Couldn't connect to text search proxy")
    except Exception as e:
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

    url = "http://wp-p3s-f8:9050/ebisearch/ws/rest/rnacentral/seqtoolresults/" \
          "?toolid=nhmmer_dummy" \
          "&jobid={job_id}" \
          "&query={query}" \
          "&format=json&fields={fields}" \
          "&facetcount={facetcount}" \
          "&facetfields={facetfields}" \
          "&size={page_size}" \
          "&start={page}"\
        .format(job_id=job_id, query=query, fields=','.join(fields), facetcount=30, facetfields=','.join(facetfields), page=page, page_size=page_size)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status >= 400:
                    raise web.HTTPBadGateway(text=response.status)
                else:
                    # TODO: merge results with facets data
                    facets = await response.json()
                    return web.json_response({results: results, facets: facets})
    except Exception as e:
        return web.HTTPBadGateway(text=str(e))

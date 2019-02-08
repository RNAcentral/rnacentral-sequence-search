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

from .settings import EBI_SEARCH_PROXY_URL


# if we fail to retrieve facets,
text_search_data_stub = {
    "hitCount": 0,
    "entries": [],  # {id: , source: , highlights: }
    "facets": [],
}


class ProxyConnectionError(Exception):
    """Raised when we failed to write text search results to our proxy"""
    def __str__(self):
        return "Proxy connection error"


class EBITextSearchConnectionError(Exception):
    """Raised when we failed to retrieve text search results from EBI search"""
    def __str__(self):
        return "EBI text search connection error"


async def get_text_search_results(results, job_id, query, page, page_size):
    """
    Post text search results to our proxy, so that EBI_SEARCH could retrieve it and index.
    Request text search facets from EBI_SEARCH, and return those data.
    """
    # send the list of rnacentral_ids to the proxy, fallback to returning the plain results, if text search unavailable
    rnacentral_ids = "\n".join([result['rnacentral_id'] for result in results])
    url = EBI_SEARCH_PROXY_URL + '/' + job_id
    headers = {'content-type': 'text/plain'}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=rnacentral_ids, headers=headers) as response:
                if response.status >= 400:
                    raise ProxyConnectionError()
    except Exception:
        raise ProxyConnectionError()

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
        .format(job_id=job_id, query=query, fields=','.join(fields), facetcount=30, facetfields=','.join(facetfields),
                page=page, page_size=page_size)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status < 400:
                    return await response.json()
    except Exception:
        raise EBITextSearchConnectionError()

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

import aiohttp

from .settings import EBI_SEARCH_PROXY_URL, PROJECT_ROOT


class ProxyConnectionError(Exception):
    """Raised when we failed to write text search results to our proxy"""
    def __str__(self):
        return "Proxy connection error"


class EBITextSearchConnectionError(Exception):
    """Raised when we failed to retrieve text search results from EBI search"""
    def __str__(self):
        return "EBI text search connection error"


def rnacentral_ids_cache_directory_path():
    return PROJECT_ROOT / 'cache'


def rnacentral_ids_file_path(job_id):
    return rnacentral_ids_cache_directory_path() / job_id


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
    'has_go_annotations',
    'has_conserved_structure',
    'has_genomic_coordinates',
    'popular_species'
]


async def get_text_search_results(results, job_id, query, start, size, facetcount, ENVIRONMENT):
    """
    For local development local server has to POST list of RNAcentral ids
    to the EMBASSY cloud machine and retrieve results from there.
    """
    if ENVIRONMENT != "PRODUCTION":
        # send the list of rnacentral_ids to the proxy, fallback to
        # returning the plain results, if text search unavailable
        rnacentral_ids = "\n".join([result['rnacentral_id'] for result in results])
        url = EBI_SEARCH_PROXY_URL + '/' + job_id
        headers = {'content-type': 'text/plain'}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=rnacentral_ids, headers=headers) as response:
                    if response.status >= 400:
                        raise ProxyConnectionError()
        except Exception as e:
            raise ProxyConnectionError() from e

    # request facets from ebi text search
    url = "http://wwwdev.ebi.ac.uk/ebisearch/ws/rest/rnacentral/seqtoolresults/" \
          "?toolid=nhmmer" \
          "&jobid={job_id}" \
          "&query={query}" \
          "&format=json&fields={fields}" \
          "&facetcount={facetcount}" \
          "&facetfields={facetfields}" \
          "&start={start}" \
          "&size={size}" \
        .format(job_id=job_id, query=query, fields=','.join(fields), facetcount=facetcount,
                facetfields=','.join(facetfields), start=start, size=size)

    try:
        # using default timeout. It means that the whole operation should finish in 5 minutes.
        # large timeout prevents facet errors
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout()) as session:
            async with session.get(url) as response:
                if response.status < 400:
                    return await response.json()
                else:
                    raise EBITextSearchConnectionError()
    except Exception as e:
        raise EBITextSearchConnectionError() from e

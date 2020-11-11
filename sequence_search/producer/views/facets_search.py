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
import hashlib

from aiohttp import web
from aiojobs.aiohttp import atomic
from pymemcache.client import base
from pymemcache import serde

from ...db.jobs import get_job_results, get_job, job_exists, set_job_ordering
from ..text_search_client import get_text_search_results, ProxyConnectionError, EBITextSearchConnectionError, \
    facetfields


logger = logging.getLogger('aiohttp.web')


def merge_popular_species_into_taxonomy_facet(text_search_data):
    """
    Prepend entries from popularSpecies facet into TAXONOMY facet,
    eliminating redundancy.
    """
    popular_species = None
    taxonomy = None
    for index, facet in enumerate(text_search_data['facets']):
        if facet['id'] == 'popular_species':
            popular_species_index = index
            popular_species = facet
        elif facet['id'] == 'TAXONOMY':
            taxonomy = facet

    if popular_species is not None and taxonomy is not None:
        popular_species_values_values = [facetValue['value'] for facetValue in popular_species['facetValues']]
        non_popular_species_values = [facetValue for facetValue in taxonomy['facetValues'] if facetValue['value'] not in popular_species_values_values]

        # replace the old taxonomy facet with the new one
        taxonomy['facetValues'] = popular_species['facetValues'] + non_popular_species_values

        # remove the popular species facet
        text_search_data['facets'].pop(popular_species_index)


@atomic
async def facets_search(request):
    """
    Function that runs EBI text search for sequence search results
    :param request: used to get job_id and params to connect to the db
    :return: list of json object

    ---
    tags:
    - Facets
    summary: Runs EBI text search for the results of sequence search and accompanies them with facets
    parameters:
    - name: job_id
      in: path
      description: Unique job identification
      type: string
      required: true
    - name: query
      in: query
      description: Text search query, representing selected facets
      type: string
      required: false
    - name: start
      in: query
      description: Return entries, starting from 'start' (counts from 0).
      type: integer
      required: false
    - name: size
      in: query
      description: Return 'size' entries (or less, if reached the end of list)
      type: integer
      required: false
    - name: facetcount
      in: query
      description: Each facet returns top 'facetcount' elements (e.g. with facetcount=2 taxonomy facet
        will return ['Homo sapiens', 'Mus musculus'])
      type: integer
      required: false
    - name: ordering
      in: query
      description: How to order results - by 'e_value', '-e_value', 'identity', '-identity', 'query_coverage', '-query_coverage', 'target_coverage' or '-target_coverage'.
      type: string
      required: false
    responses:
      200:
        description: Ok
      404:
        description: Not found (probably, job with this job_id doesn't exist)
      502:
        description: Bad gateway (could not connect to EBI search proxy)
    """
    job_id = request.match_info['job_id']

    if not await job_exists(request.app['engine'], job_id):
        return web.HTTPNotFound(text="Job %s does not exist" % job_id)

    # parse query parameters
    query = request.query['query'] if 'query' in request.query else 'rna'
    start = request.query['start'] if 'start' in request.query else 0
    size = request.query['size'] if 'size' in request.query else 20
    facetcount = request.query['facetcount'] if 'facetcount' in request.query else 100
    ordering = request.query['ordering'] if 'ordering' in request.query else 'e_value'

    # set ordering, so that EBI text search returns entries in correct order
    await set_job_ordering(request.app['engine'], job_id, ordering)

    # get sequence search query sequence, status and number of hits
    job = await get_job(request.app['engine'], job_id)
    sequence = job['query']
    status = job['status']
    hits = job['hits']

    # get sequence search results from the database, sort/aggregate?
    results = await get_job_results(request.app['engine'], job_id)

    # try to get facets from EBI text search, otherwise stub facets
    try:
        ENVIRONMENT = request.app['settings'].ENVIRONMENT

        # we want to cache the EBI Search result
        ip_address = '192.168.0.8' if ENVIRONMENT == 'PRODUCTION' else 'localhost'
        client = base.Client((ip_address, 11211),
                             serializer=serde.get_python_memcache_serializer(pickle_version=2),
                             deserializer=serde.python_memcache_deserializer)

        # create a hash with query parameters
        text_search_key = hashlib.md5(
            (job_id + query + str(start) + str(size) + str(facetcount) + ordering).encode('utf-8')
        ).hexdigest()

        # check if the result is cached
        cached_result = client.get(text_search_key)

        if cached_result:
            text_search_data = cached_result
            logging.debug("Using cache. This is the key used: {}".format(text_search_key))
        else:
            text_search_data = await get_text_search_results(
                results, job_id, query, start, size, facetcount, ENVIRONMENT
            )

            # if this worked, inject text search results into facets json
            for entry in text_search_data['entries']:
                for result in results:
                    if result['rnacentral_id'] == entry['id']:
                        try:
                            result['description'] = entry['fields']['description'][0]
                        except (KeyError, IndexError) as e:
                            result['description'] = result['rnacentral_id']
                            logging.debug("Error - description not found for rnacentral_id {}".format(result['rnacentral_id']))
                        entry.update(result)
                        break

            # sort facets in the same order as in text_search_client
            text_search_data['facets'].sort(key=lambda el: facetfields.index(el['id']))

            # merge the contents of the 'popular_species' facet into the 'TAXONOMY' facet
            merge_popular_species_into_taxonomy_facet(text_search_data)

            # add the query sequence to display on the page
            text_search_data['sequence'] = sequence

            # add the total number of hits
            text_search_data['hits'] = hits

            # add status of sequence search to display warnings, if need arises
            text_search_data['sequenceSearchStatus'] = status

            # text search worked successfully, unset text search error flag
            text_search_data['textSearchError'] = False

            # cache the result
            client.set(text_search_key, text_search_data)

    except (ProxyConnectionError, EBITextSearchConnectionError) as e:
        # text search is not available, pad output with facets stub, indicate that we have a text search error
        logger.warning(str(e))

        text_search_data = {
            'entries': [],
            'facets': [],
            'hitCount': len(results),
            'sequence': sequence,
            'sequenceSearchStatus': status,
            'textSearchError': True
        }

        # populate text search entries with sequence search results, paginate
        start = int(start)
        size = int(size)
        for result in results[start:start+size]:
            text_search_data['entries'].append(result)

    return web.json_response(text_search_data)

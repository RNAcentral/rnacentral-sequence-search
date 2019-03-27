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

from ...db.jobs import get_job_results, job_exists
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
        type: string
    - name: query
      in: query
      description: Query string for the sequence we search - either nucleotide sequence or
      required: false
      schema:
        type: string
    - name: start
      in: query
      description: Return entries, starting from 'start' (counts from 0).
      required: false
      schema:
        type: integer
    - name: size
      in: query
      description: Return 'size' entries (or less, if reached the end of list)
      required: false
      schema:
        type: integer
    - name: facetcount
      in: query
      description: Each facet returns top 'facetcount' elements (e.g. with facetcount=2 taxonomy facet
        will return ['Homo sapiens', 'Mus musculus'])
      required: false
      schema:
        type: integer
    responses:
      '200':
        description: Successfully returns results
        content:
          'application/json':
            schema:
              type: object
              properties:
                hitCount:
                  description: >-
                    Total number of entries found by this query. Note that entries array is paginated and
                    thus number of hits in it is less than or equal to hitCount.
                  type: integer
                entries:
                  description: >-
                    Hits found by search. Those are rnacentral sequences with metainformation, collected
                    from both sequence search and text search.
                  type: object
                facets:
                  description: >-
                    Array of facets by which users can filter the entries/hits.
                  type: array
                textSearchError:
                  description: >-
                    Indicates, whether the data from text search facets were successfully retrieved.
            example:
              {
                "hitCount": 134,
                "entries": [
                  {
                    "id": "URS0000137D91_420246",
                    "source": "rnacentral",
                    "fields": {
                      "active": ["Active"],
                      "author": [],
                      "common_name": [],
                      "description": ["Geobacillus thermodenitrificans NG80-2 strain NG80-2 5S ribosomal RNA, rRNA"],
                      "expert_db": ["ENA", "RefSeq", "Rfam"],
                      "function": [],
                      "gene": [],
                      "gene_synonym": [],
                      "has_genomic_coordinates": ["False"],
                      "length": ["117"],
                      "locus_tag": ["GTNG_5s001"],
                      "organelle": [],
                      "pub_title": [
                        "Rfam 11.0: 10 years of RNA families",
                        "Direct Submission",
                        "Genome and proteome of long-chain alkane degrading Geobacillus thermodenitrificans NG80-2 isolated from a deep-subsurface oil reservoir",
                        "Rfam 12.0: updates to the RNA families database",
                        "RefSeq: an update on mammalian reference sequences"
                      ],
                      "product": ["5S ribosomal RNA"],
                      "qc_warning_found": ["False"],
                      "qc_warning": ["none"],
                      "rna_type": ["rRNA"],
                      "standard_name": [],
                      "tax_string": [
                        "Bacteria; Firmicutes; Bacilli; Bacillales; Bacillaceae; Geobacillus; Geobacillus thermodenitrificans NG80-2",
                        "Bacteria; Firmicutes; Bacillales; Bacillaceae; Geobacillus; Geobacillus thermodenitrificans NG80-2"
                      ]
                    },
                    "rnacentral_id": "URS0000137D91_420246",
                    "description": "Geobacillus thermodenitrificans NG80-2 strain NG80-2 5S ribosomal RNA, complete sequence",
                    "score": 35.1,
                    "bias": 3.1,
                    "e_value": 2.4e-08,
                    "target_length": 117,
                    "alignment": "Query   4 CUGGCGGCCGUAGCGCGGUGGUCCCACCUGACCCCAUGCCGAACUCAGAAGUGAAACGCCGUAGCGCCGAUGGUAGUGUGGGGUC-UCC 91 \n          || | ||   |||||  | ||   |||  |  ||||| |||||| | ||||| || | |   |||||||||||||||  |||      |\nSbjct   2 CUAGUGGUGAUAGCGGAGAGGAAACACUCGUUCCCAUCCCGAACACGGAAGUUAAGCUCUCCAGCGCCGAUGGUAGUUGGGGCCAGCGC 90 \n\nQuery  92 CCAUGCGAGAGUAGGGAACUGCCAGG 117\n          || ||| ||||||||   |||| |||\nSbjct  91 CCCUGCAAGAGUAGGUCGCUGCUAGG 116",
                    "alignment_length": 115,
                    "gap_count": 1,
                    "match_count": 77,
                    "nts_count1": 114,
                    "nts_count2": 115,
                    "identity": 66.9565217391304,
                    "query_coverage": 95.0,
                    "target_coverage": 98.2905982905983,
                    "gaps": 0.869565217391304,
                    "query_length": 120,
                    "result_id": 55
                  }
                ],
                "facets": [
                  {
                    "id": "TAXONOMY",
                    "label": "Organisms",
                    "total": 151,
                    "facetValues": [
                      {"label": "Thermus thermophilus", "value": "274", "count": 2},
                      {"label": "Sphaerochaeta pleomorpha str. Grapes", "value": "158190", "count": 2},
                      {"label": "Escherichia coli", "value": "562", "count": 2},
                      {"label": "Desulfatibacillum alkenivorans", "value": "259354", "count": 1},
                      {"label": "Caldicellulosiruptor kristjanssonii", "value": "52765", "count": 1},
                      {"label": "Roseibacterium elongatum", "value": "159346", "count": 1},
                      {"label": "Arcobacter butzleri ED-1", "value": "944546", "count": 1},
                      {"label": "Thermoanaerobacter wiegelii Rt8.B1", "value": "697303", "count": 1},
                      {"label": "Psychrobacter cryohalolentis K5", "value": "335284", "count": 1},
                      {"label": "Mycoplasma hominis ATCC 23114", "value": "347256", "count": 1},
                      {"label": "Rickettsia japonica YH", "value": "652620", "count": 1},
                      {"label": "Anaerococcus prevotii DSM 20548", "value": "525919", "count": 1},
                      {"label": "Dehalococcoides mccartyi VS", "value": "311424", "count": 1},
                      {"label": "Rickettsia slovaca str. D-CWPP", "value": "1105109", "count": 1},
                      {"label": "Candidatus Sulcia muelleri GWSS", "value": "444179", "count": 1},
                      {"label": "Mycoplasma agalactiae PG2", "value": "347257", "count": 1},
                      {"label": "Sulfurovum sp. NBC37-1", "value": "387093", "count": 1},
                      {"label": "Lactobacillus johnsonii NCC 533", "value": "257314", "count": 1},
                      {"label": "Chlamydia pecorum E58", "value": "331635", "count": 1},
                      {"label": "Buchnera aphidicola BCc", "value": "372461", "count": 1},
                      {"label": "Rickettsia rickettsii str. 'Sheila Smith'", "value": "392021", "count": 1},
                      {"label": "Chlamydia psittaci 6BC", "value": "331636", "count": 1},
                      {"label": "Chlamydia felis Fe/C-56", "value": "264202", "count": 1},
                      {"label": "Coriobacterium glomerans PW2", "value": "700015", "count": 1},
                      {"label": "Flavobacterium columnare ATCC 49512", "value": "1041826", "count": 1},
                      {"label": "Lactobacillus gasseri ATCC 33323 = JCM 1131", "value": "324831", "count": 1},
                      {"label": "Simiduia agarivorans SA1 = DSM 21679", "value": "1117647", "count": 1},
                      {"label": "Halothiobacillus neapolitanus c2", "value": "555778", "count": 1},
                      {"label": "Rhodococcus pyridinivorans", "value": "103816", "count": 1},
                      {"label": "Mycoplasma gallisepticum str. R(low)", "value": "710127", "count": 1}
                    ]
                  },
                  {
                    "id": "qc_warning_found",
                    "label": "QC warning found",
                    "total": 1,
                    "facetValues": [
                      {"label": "False", "value": "False", "count": 134}
                    ]
                  },
                  {
                    "id": "has_genomic_coordinates",
                    "label": "Genomic mapping",
                    "total": 2,
                    "facetValues": [
                      {"label": "Not available", "value": "False", "count": 132},
                      {"label": "Available", "value": "True", "count": 2}
                    ]
                  },
                  {
                    "id": "rna_type",
                    "label": "RNA types",
                    "total": 1,
                    "facetValues": [
                      {"label": "rRNA", "value": "rRNA", "count": 134}
                    ]
                  },
                  {
                    "id": "expert_db",
                    "label": "Expert databases",
                    "total": 5,
                    "facetValues": [
                      {"label": "RefSeq", "value": "RefSeq", "count": 127},
                      {"label": "ENA", "value": "ENA", "count": 116},
                      {"label": "Rfam", "value": "Rfam", "count": 52},
                      {"label": "PDBe", "value": "PDBe", "count": 5},
                      {"label": "Ensembl Plants", "value": "Ensembl Plants", "count": 2}
                    ]
                  }
                ]
              }
      '404':
        description: No results for given job_id
      '502':
        description: Could not connect to EBI search proxy
    """
    job_id = request.match_info['job_id']

    if not await job_exists(request.app['engine'], job_id):
        return web.HTTPNotFound(text="Job %s does not exist" % job_id)

    query = request.query['query'] if 'query' in request.query else 'rna'
    start = request.query['start'] if 'start' in request.query else 0
    size = request.query['size'] if 'size' in request.query else 20
    facetcount = request.query['facetcount'] if 'facetcount' in request.query else 10

    # get sequence search results from the database, sort/aggregate?
    results = await get_job_results(request.app['engine'], job_id)

    # try to get facets from EBI text search, otherwise stub facets
    try:
        ENVIRONMENT = request.app['settings'].ENVIRONMENT
        text_search_data = await get_text_search_results(results, job_id, query, start, size, facetcount, ENVIRONMENT)

        # if this worked, inject text search resunlts into facets json
        for entry in text_search_data['entries']:
            for result in results:
                if result['rnacentral_id'] == entry['id']:
                    entry.update(result)

        # text search worked successfully, add a notice about this
        text_search_data['textSearchError'] = False

    except (ProxyConnectionError, EBITextSearchConnectionError) as e:
        # text search is not available, pad output with facets stub, indicate that
        logger.warning(str(e))
        text_search_data = {'entries': [], 'facets': [], 'hitCount': len(results), 'textSearchError': True}

        start = int(start)
        size = int(size)
        for result in results[start:start+size]:
            # TODO: possibly update results fields, not sure about structure
            text_search_data['entries'].append(result)

    return web.json_response(text_search_data)


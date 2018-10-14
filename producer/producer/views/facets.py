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

from aiohttp import web


async def facets(request):
    job_id = request.match_info['job_id']

    data = {
        "facets": [
            {
                "id":"TAXONOMY",
                "label":"Organisms",
                "total":1,
                "facetValues":[
                    {"label":"Homo sapiens","value":"9606","count":1}
                ]
            },
            {
                "id":"qc_warning_found",
                "label":"QC warning found",
                "total":1,
                "facetValues":[{"label":"False","value":"False","count":1}]
            },
            {
                "id":"has_genomic_coordinates",
                "label":"Genomic mapping",
                "total":1,
                "facetValues":[{"label":"Available","value":"True","count":1}]},
            {
                "id":"popular_species",
                "label":"Popular species",
                "total":1,
                "facetValues":[{"label":"Homo sapiens","value":"9606","count":1}]
            },
            {
                "id":"rna_type",
                "label":"RNA types",
                "total":1,
                "facetValues":[{"label":"precursor RNA","value":"precursor RNA","count":1}]
            },
            {
                "id":"expert_db",
                "label":"Expert databases",
                "total":6,
                "facetValues":[
                    {"label":"HGNC","value":"HGNC","count":1},
                    {"label":"RefSeq","value":"RefSeq","count":1},
                    {"label":"miRBase","value":"miRBase","count":1},
                    {"label":"GENCODE","value":"GENCODE","count":1},
                    {"label":"Ensembl","value":"Ensembl","count":1},
                    {"label":"ENA","value":"ENA","count":1}
                ]
            }
        ]
    }

    return web.json_response(data)

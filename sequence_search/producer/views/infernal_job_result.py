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

from ...db.jobs import get_infernal_job_results
from ...db import DatabaseConnectionError


@atomic
async def infernal_job_result(request):
    """
    Function that returns cmscan command results
    :param request: used to get job_id and params to connect to the db
    :return: list of json object

    ---
    tags:
    - Jobs
    summary: Shows the result of the infernal job
    parameters:
    - name: job_id
      in: path
      description: ID of job to display result for
      required: true
      schema:
        type: string
    responses:
      200:
        description: Successfully returns result
        examples:
          application/json:
            [
              {
                "target_name": "U3",
                "accession_rfam": "RF00012",
                "query_name": "query",
                "accession_seq": "-",
                "mdl": "cm",
                "mdl_from": 1,
                "mdl_to": 218,
                "seq_from": 1,
                "seq_to": 217,
                "strand": "+",
                "trunc": "no",
                "pipeline_pass": 1,
                "gc": 0.5,
                "bias": 0.0,
                "score": 179.9,
                "e_value": 1.8e-44,
                "inc": "!",
                "description": "Small nucleolar RNA U3",
                "alignment":
                  "\n
                  v  v    v       v    v   v                           NC\n              <<<<<<<<<<<---<<<<<.____>>>>>->>>>>>->>>>>,,,,,,,<<<.<<______>>>>>----------((((
                  (--------------((((((((((((,,<<<-------<<<<--.<<<<-<<<<<______>>>>>-->>>>-->>>>--------->>>.<<<<<<<<<.______>>>>>>>->>,.))))))))))))-------))))) CS\n  RF00012   1
                  aaGaccauACUUuAcAGGa.UCAUuUCUgUAGUaugUguCuugAgaAaUuuc.ccaaaagUgggaaggcacccaaAaCCaCGAUGAuGAGauguagcGuucucucCuGAgCGUGAAGcuggccau.cggcaguugcUUuuuugcaacuugccguuggccaUUGAUGAUCGc.
                  uccucuccc.UuuuuagggagagugaG.gGgagagaaCgcauUCUGAGuGGu 218\n              :AG:::A:ACUUU :AGG: UCAU:UCU:UAGU:U:U::CU:GAGAA UU:: ::+AA GU::::A GCACC AAAACCACGA GA GAGA
                  GUAGCGUU:UCUCCUGA:CGUGAAGC GGC:+U :GGC GUUGCUU   UGCAAC UGCC:U :GCCAUUGAUGAUCG:  :  :::C  U U    G:::  U: G GGGAGA:AACGC  UCUGAGUGGU\n    query   1
                  AAGACUAUACUUU-CAGGGaUCAUUUCUAUAGUGUGUUACUAGAGAAGUUUCuCUGAACGUGUAGA-GCACCGAAAACCACGAGGAAGAGAGGUAGCGUUUUCUCCUGAGCGUGAAGCCGGCUUUcUGGC-GUUGCUUGGCUGCAAC-UGCCGUCAGCCAUUGAUGAUCGUuCUUCU
                  CUCCgUAU---UGGGGAGUGAGaGGGAGAGAACGCGGUCUGAGUGGU 217\n              *************.****99************************9999888879999999999999.
                  9*********************************************************99999.*****99999******.8**********************74444444442555...455555555556************************ PP\n"
              }
            ]
      '404':
        description: No result for given job_id (probably, job with this job_id doesn't exist)
    """
    job_id = request.match_info['job_id']
    engine = request.app['engine']

    try:
        results = await get_infernal_job_results(engine, job_id)
    except DatabaseConnectionError as e:
        raise web.HTTPNotFound() from e

    return web.json_response(results)

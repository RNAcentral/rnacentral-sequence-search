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
import sqlalchemy as sa

from ..models import Job, JobChunk, JobChunkResult


async def job_result(request):
    """
    ---
    tags:
    - jobs
    summary: Shows the result of a job
    parameters:
    - name: job_id
      in: path
      description: ID of job to display result for
      required: true
      schema:
        type: integer
    responses:
      '200':
        description: Successfully returns result
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  rnacentral_id:
                    type: string
                  description:
                    type: string
                  score:
                    type: float
                  bias:
                    type: float
                  e_value:
                    type: float
                  target_length:
                    type: integer
                  alignment:
                    type: string
                  alignment_length:
                    type: integer
                  gap_count:
                    type: integer
                  match_count:
                    type: integer
                  nts_count1:
                    type: integer
                  nts_count2:
                    type: integer
                  identity:
                    type: float
                  query_coverage:
                    type: float
                  target_coverage:
                    type: float
                  gaps:
                    type: float
                  query_length:
                    type: integer
                  result_id:
                    type: integer
            example:
              [{
                rnacentral_id: 'URS000075D2D2',
                description: 'Mus musculus miR - 1195 stem - loop',
                score: 6.5,
                bias: 0.7,
                e_value: 32,
                target_length: 98,
                alignment: "Query  8 GAGUUUGAGACCAGCCUGGCCA 29\n| | | | | | | | | | | | | | | | | |\nSbjct_10090\n22\nGAGUUCGAGGCCAGCCUGCUCA\n43",
                alignment_length: 22,
                gap_count: 0,
                match_count: 18,
                nts_count1: 22,
                nts_count2: 0,
                identity: 81.81818181818183,
                query_coverage: 73.33333333333333,
                target_coverage: 0,
                gaps: 0,
                query_length: 30,
                result_id: 1
              }]

      '404':
        description: No result for given job_id (probably, job with this job_id doesn't exist)
    """
    job_id = request.match_info['job_id']

    try:
        async with request.app['engine'].acquire() as connection:
            query = (sa.select([
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
            async for row in connection.execute(query):
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

    return web.json_response(results)

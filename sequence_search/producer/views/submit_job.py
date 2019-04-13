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

from ...db.consumers import delegate_job_chunk_to_consumer, find_available_consumers
from ...db.jobs import save_job
from ...db.job_chunks import save_job_chunk
from ...consumer.rnacentral_databases import producer_validator, producer_to_consumers_databases


def serialize(request, data):
    """
    Validates and normalizes input data.

    :param request:
    :param data:
    :return: Normalized data
    :raise: KeyError, TypeError, ValueError
    """
    query = data['query']
    databases = data['databases']

    if not query:
        raise ValueError("Empty query")
    # TODO: validate query
    # for char in query:
    #     if char not in ['A', 'T', 'G', 'C', 'U']:
    #         raise ValueError("Input query should be a nucleotide sequence "
    #                               "and contain only {ATGCU} characters, found: '%s'." % query)

    # TODO: split query into query string and description
    data['description'] = ''

    # normalize query: convert nucleotides to RNA
    data['query'] = query.replace('T', 'U')

    # validate databases
    producer_validator(databases)

    return data


async def save(request, data):
    """Save metadata about this job and job_chunks to the database."""
    job_id = await save_job(request.app['engine'], data['query'])
    if job_id:
        for database in data['databases']:
            job_chunk_id = await save_job_chunk(request.app['engine'], job_id, database)
    return job_id


@atomic
async def submit_job(request):
    """
    Example:
    curl -H "Content-Type:application/json" -d "{\"databases\": [\"miRBase\"], \"query\": \"AGGUCAGGAGUUUGAGACCAGCCUGGCCAA\"}" localhost:8002/api/submit-job

    ---
    tags:
    - jobs
    summary: Accepts a job for execution
    consumes:
     - application/json
    parameters:
     - in: body
       name: query
       description: Nucleotide sequence to search for as a string of nucleotides or a fasta file with a single sequence
       schema:
         type: string
         required: true
         example: "AGGUCAGGAGUUUGAGACCAGCCUGGCCAA"
     - in: body
       name: databases
       description: List of RNAcentral member databases to search the query sequence against. Can be an empty list.
       schema:
         type: array
         items:
           type: string
         required: true
         example: ['mirbase', 'pombase']
    responses:
      201:
        description: Job accepted.
        content:
          application/json: {}
      400:
        description: Invalid input (either query is not a nucleotide sequence, or databases not in RNAcentral)
    """
    data = await request.json()

    try:
        data = serialize(request, data)
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(text=str(e)) from e

    # save metadata about this job and job_chunks to the database
    job_id = await save_job(request.app['engine'], data['query'], data['description'])

    databases = producer_to_consumers_databases(data['databases'])
    for database in databases:
        job_chunk_id = await save_job_chunk(request.app['engine'], job_id, database)

    # TODO: what if Job was saved and JobChunk was not? Need transactions?

    consumers = await find_available_consumers(request.app['engine'])
    for index in range(min(len(consumers), len(databases))):
        try:
            await delegate_job_chunk_to_consumer(
                engine=request.app['engine'],
                consumer_ip=consumers[index].ip,
                job_id=job_id,
                database=databases[index],
                query=data['query']
            )
        except Exception as e:
            return web.HTTPBadGateway(text=str(e))

    return web.json_response({"job_id": job_id}, status=201)

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

import re

from aiohttp import web
from aiojobs.aiohttp import atomic

from sequence_search.db.models import JOB_CHUNK_STATUS_CHOICES
from sequence_search.producer.settings import MIN_QUERY_LENGTH, MAX_QUERY_LENGTH
from ...db.consumers import delegate_job_chunk_to_consumer, find_available_consumers, delegate_infernal_job_to_consumer
from ...db.jobs import find_highest_priority_jobs, save_job, sequence_exists, database_used_in_search
from ...db.job_chunks import save_job_chunk, set_job_chunk_status
from ...db.infernal_job import save_infernal_job
from ...consumer.rnacentral_databases import producer_validator, producer_to_consumers_databases


def serialize(request, data):
    """
    Validates and normalizes input data.

    :param request:
    :param data:
    :return: Normalized data
    :raise: KeyError, TypeError, ValueError
    """
    if not data['query']:
        raise ValueError("Empty query")

    # make sure query contains only reasonable nucleotide codes
    match = re.search('^(>.+?[\n\r])*?[acgtunwsmkrybdhvx\s]+$', data['query'], re.IGNORECASE)
    if not match:
        raise ValueError("Input query is not a valid nucleotide sequence: '%s'\n" % data['query'])

    # possibly split query into query and description
    match = re.search('(^>(.+)[\n\r])?([\s\S]+)', data['query'])
    if match:
        data['query'] = match.group(3)
        data['description'] = match.group(2)
    else:
        data['description'] = ''

    # check the sequence length
    if len(data['query']) < MIN_QUERY_LENGTH:
        raise ValueError("The sequence cannot be shorter than %s nucleotides.\n" % MIN_QUERY_LENGTH)
    elif len(data['query']) > MAX_QUERY_LENGTH:
        raise ValueError("The sequence cannot be longer than %s nucleotides.\n" % MAX_QUERY_LENGTH)

    # normalize query: convert nucleotides to RNA
    data['query'] = data['query'].replace('T', 'U')

    # validate databases
    producer_validator(data['databases'])

    return data


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

    # converts all uppercase characters to lowercase.
    if data['databases']:
        data['databases'] = [db.lower() for db in data['databases']]

    try:
        data = serialize(request, data)
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(text=str(e)) from e

    # database that the user wants to use to perform the search
    databases = producer_to_consumers_databases(data['databases'])

    # check if this query has already been searched
    job_list = await sequence_exists(request.app['engine'], data['query'])

    job_id = None
    if job_list:
        # check the database used in each job_id.
        # set job_id if the database used is the same as in "databases"
        for job in job_list:
            if await database_used_in_search(request.app['engine'], job, databases):
                job_id = job
                break

    # do the search if the data is not in the database
    if not job_id:
        # check for unfinished jobs
        unfinished_job = await find_highest_priority_jobs(request.app['engine'])

        # get URL - for statistical purposes
        try:
            url = data['url']
        except KeyError:
            url = None

        # get priority
        try:
            priority = data['priority']
        except KeyError:
            priority = None

        # save metadata about this job to the database
        job_id = await save_job(request.app['engine'], data['query'], data['description'], url, priority)

        # save metadata about job_chunks to the database
        # TODO: what if Job was saved and JobChunk was not? Need transactions?
        for database in databases:
            # save job_chunk with "created" status. This prevents the check_chunks_and_consumers function,
            # which runs every 5 seconds, from executing the same job_chunk again.
            await save_job_chunk(request.app['engine'], job_id, database)

        # save metadata about infernal_job to the database
        # TODO: what if Job was saved and InfernalJob was not? Need transactions?
        await save_infernal_job(request.app['engine'], job_id, priority)

        # if there are unfinished jobs, change the status of each new job_chunk to pending;
        # otherwise try starting the job
        if unfinished_job:
            for database in databases:
                try:
                    await set_job_chunk_status(
                        request.app['engine'],
                        job_id,
                        database,
                        status=JOB_CHUNK_STATUS_CHOICES.pending
                    )
                except Exception as e:
                    return web.HTTPBadGateway(text=str(e))
        else:
            # check for available consumers
            consumers = await find_available_consumers(request.app['engine'])

            # if consumers are available, delegate to infernal_job first
            if consumers:
                consumer = consumers.pop(0)

                try:
                    await delegate_infernal_job_to_consumer(
                        engine=request.app['engine'],
                        consumer_ip=consumer.ip,
                        consumer_port=consumer.port,
                        job_id=job_id,
                        query=data['query']
                    )
                except Exception as e:
                    return web.HTTPBadGateway(text=str(e))

            # after infernal_job, delegate consumers to job_chunks
            for index in range(min(len(consumers), len(databases))):
                try:
                    await delegate_job_chunk_to_consumer(
                        engine=request.app['engine'],
                        consumer_ip=consumers[index].ip,
                        consumer_port=consumers[index].port,
                        job_id=job_id,
                        database=databases[index],
                        query=data['query']
                    )
                except Exception as e:
                    return web.HTTPBadGateway(text=str(e))

            # if no consumer is available, change the status of the remaining job_chunks to pending
            for index in range(len(consumers), len(databases)):
                try:
                    await set_job_chunk_status(
                        request.app['engine'],
                        job_id,
                        databases[index],
                        status=JOB_CHUNK_STATUS_CHOICES.pending
                    )
                except Exception as e:
                    return web.HTTPBadGateway(text=str(e))

    return web.json_response({"job_id": job_id}, status=201)

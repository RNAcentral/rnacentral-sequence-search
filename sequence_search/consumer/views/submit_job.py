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
import logging
from aiohttp import web
from aiojobs.aiohttp import spawn

from .. import settings
from ..nhmmer_parse import nhmmer_parse
from ..nhmmer_search import nhmmer_search
from ..filenames import query_file_path, result_file_path
from ...db.models import CONSUMER_STATUS_CHOICES, JOB_STATUS_CHOICES
from ...db.job_chunk_results import set_job_chunk_results
from ...db.job_chunks import get_consumer_ip_from_job_chunk, get_job_chunk_from_job_and_database, set_job_chunk_status
from ...db.jobs import check_job_chunks_status, set_job_status
from ...db.consumers import set_consumer_status


class NhmmerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return str(self.text)


async def nhmmer(engine, job_id, sequence, database):
    """
    Function that performs nhmmer search and then reports the result to provider API.

    :param engine:
    :param sequence: string, e.g. AAAAGGTCGGAGCGAGGCAAAATTGGCTTTCAAACTAGGTTCTGGGTTCACATAAGACCT
    :param job_id: id of this job, generated by producer
    :param database: name of the database to search against
    :return:
    """
    logger = logging.Logger('aiohttp.web')

    job_chunk_id = await get_job_chunk_from_job_and_database(engine, job_id, database)

    logger.info('Nhmmer search started for: job_id = %s, database = %s' % (job_id, database))
    try:
        filename = await nhmmer_search(sequence=sequence, job_id=job_id, database=database)
        logger.info('Nhmmer search success for: job_id = %s, database = %s' % (job_id, database))
    except Exception as e:
        # TODO: recoverable errors handling
        # TODO: irrecoverable errors handling
        logger.error('Nhmmer search error for: job_id = %s, database = %s' % (job_id, database))
        raise NhmmerError('Nhmmer search error for: job_id = %s, database = %s' % (job_id, database)) from e

    results = [record for record in nhmmer_parse(filename=filename)]  # parse nhmmer results to python

    # update job_chunk in the database
    await set_job_chunk_status(engine, job_id, database, status=JOB_STATUS_CHOICES.success)
    await set_job_chunk_results(engine, job_id, database, results)

    # update job in the database, if the whole job's done
    if await check_job_chunks_status(engine, job_id):
        await set_job_status(engine, job_id, JOB_STATUS_CHOICES.success)

    # update consumer status
    consumer_ip = await get_consumer_ip_from_job_chunk(engine, job_chunk_id)
    await set_consumer_status(engine, consumer_ip, CONSUMER_STATUS_CHOICES.available)


def serialize(request, data):
    """Ad-hoc validator for input JSON data"""
    job_id = data['job_id']
    sequence = data['sequence']
    database = data['database']

    if os.path.isfile(query_file_path(job_id, database)) or os.path.isfile(result_file_path(job_id, database)):
        raise ValueError("job with id '%s' has already been submitted" % job_id)

    if database not in settings.RNACENTRAL_DATABASES:
        raise ValueError("Database argument is wrong: '%s' is not one of RNAcentral databases." % database)

    for char in sequence:
        if char not in ['A', 'T', 'G', 'C', 'U']:
            raise ValueError("Input sequence should be nucleotide sequence "
                                  "and contain only {ATGCU} characters, found: '%s'." % sequence)

    return data


async def submit_job(request):
    """
    For testing purposes, try the following command:

    curl -H "Content-Type:application/json" -d "{\"job_id\": 1, \"database\": \"miRBase\", \"sequence\": \"AAAAGGTCGGAGCGAGGCAAAATTGGCTTTCAAACTAGGTTCTGGGTTCACATAAGACCT\"}" localhost:8000/submit-job
    """
    data = await request.json()

    try:
        data = serialize(request, data)
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(text=str(e)) from e

    await spawn(request, nhmmer(request.app['engine'], data['job_id'], data['sequence'], data['database']))

    return web.HTTPCreated()

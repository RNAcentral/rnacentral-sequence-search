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

import json
import os
from aiohttp import web, client
from aiojobs.aiohttp import spawn

from .. import settings
from ..nhmmer_parse import nhmmer_parse
from ..nhmmer_search import nhmmer_search


async def nhmmer(job_id, sequence, database):
    """
    Function that performs nhmmer search and then reports the result to provider API.

    :param sequence: string, e.g. AAAAGGTCGGAGCGAGGCAAAATTGGCTTTCAAACTAGGTTCTGGGTTCACATAAGACCT
    :param job_id: id of this job, generated by producer
    :param database: name of the database to search against
    :return:
    """

    # TODO: recoverable errors handling
    # TODO: irrecoverable errors handling

    filename = await nhmmer_search(sequence=sequence, job_id=job_id, database=database)

    data = {"job_id": job_id, "database": database, "result": ""}
    for record in nhmmer_parse(filename=filename):
        data["result"] = data["result"] + str(record)

    response_url = "{protocol}://{host}:{port}/{url}".format(
        protocol=settings.PRODUCER_PROTOCOL,
        host=settings.PRODUCER_HOST,
        port=settings.PRODUCER_PORT,
        url=settings.PRODUCER_JOB_DONE_URL
    )

    async with client.request(
            "post",
            response_url,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
    ) as response:
        if response.status != 200:
            print(response.status)
            text = await response.text()
            print(text)


def validate_job_data(job_id, sequence, database):
    """Ad-hoc validator for input JSON data"""
    if os.path.isfile(settings.QUERY_DIR / (str(job_id) + '.txt')) or \
            os.path.isfile(settings.RESULTS_DIR / (str(job_id) + '.txt')):
        raise web.HTTPBadRequest(text="job with id '%s' has already been submitted" % job_id)

    if database not in settings.RNACENTRAL_DATABASES:
        raise web.HTTPBadRequest(
            text="Database argument is wrong: '%s' is not"
                 " one of RNAcentral databases." % database
        )

    for char in sequence:
        if char not in ['A', 'T', 'G', 'C', 'U']:
            raise web.HTTPBadRequest(
                text="Input sequence should be nucleotide sequence"
                     " and contain only {ATGCU} characters, found: '%s'." % sequence
            )


async def submit_job(request):
    """
    For testing purposes, try the following command:

    curl -H "Content-Type:application/json" -d "{\"job_id\": 1, \"databases\": [\"miRBase\"], \"sequence\": \"AAAAGGTCGGAGCGAGGCAAAATTGGCTTTCAAACTAGGTTCTGGGTTCACATAAGACCT\"}" localhost:8000/job
    """
    data = await request.json()
    try:
        job_id = data['job_id']
        sequence = data['sequence']
        database = data['database']
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(text='Bad input') from e

    validate_job_data(job_id, sequence, database)

    await spawn(request, nhmmer(job_id, sequence, database))

    url = request.app.router['result'].url_for(result_id=str(job_id))
    return web.HTTPFound(location=url)


    # async with request.app['db'].acquire() as conn:
    #     question_id = int(request.match_info['question_id'])
    #     data = await request.post()
    #     try:
    #         choice_id = int(data['choice'])
    #     except (KeyError, TypeError, ValueError) as e:
    #         raise web.HTTPBadRequest(text='You have not specified choice value') from e
    #     try:
    #         await db.vote(conn, question_id, choice_id)
    #     except db.RecordNotFound as e:
    #         raise web.HTTPNotFound(text=str(e))
    #     router = request.app.router
    #     url = router['results'].url_for(question_id=str(question_id))
    #     return web.HTTPFound(location=url)
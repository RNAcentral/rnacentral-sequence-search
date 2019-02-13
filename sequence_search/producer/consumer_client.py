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
import asyncio
import aiohttp
import json
from aiohttp import test_utils, web

from .settings import ENVIRONMENT, CONSUMER_SUBMIT_JOB_URL, CONSUMER_PORT


class ConsumerClient(object):
    async def submit_job(self, consumer_ip, job_id, database, query):
        # prepare the data for request
        url = "http://" + str(consumer_ip) + ':' + str(CONSUMER_PORT) + '/' + str(CONSUMER_SUBMIT_JOB_URL)
        json_data = json.dumps({"job_id": job_id, "sequence": query, "database": database})
        headers = {'content-type': 'application/json'}

        if ENVIRONMENT != 'TEST':
            async with aiohttp.ClientSession() as session:
                logging.debug("Queuing JobChunk to consumer: url = {}, json_data = {}, headers = {}"
                              .format(url, json_data, headers))

                response = await session.post(url, data=json_data, headers=headers)
        else:
            # in TEST environment mock the request
            logging.debug("Queuing JobChunk to consumer: url = {}, json_data = {}, headers = {}"
                          .format(url, json_data, headers))

            request = test_utils.make_mocked_request('POST', url, headers=headers)
            await asyncio.sleep(1)
            response = web.Response(status=200)

        return response

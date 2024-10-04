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

from .settings import ENVIRONMENT, CONSUMER_SUBMIT_JOB_URL, CONSUMER_SUBMIT_INFERNAL_JOB_URL


class ConsumerClient(object):
    def __init__(self):
        self.session = None

    async def init_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def submit_job(self, consumer_ip, consumer_port, job_id, database, query):
        await self.init_session()

        # prepare the data for request
        url = f"http://{consumer_ip}:{consumer_port}/{CONSUMER_SUBMIT_JOB_URL}"
        json_data = json.dumps({"job_id": job_id, "sequence": query, "database": database})
        headers = {"content-type": "application/json"}

        if ENVIRONMENT != "TEST":
            logging.debug(f"Queuing JobChunk to consumer: url = {url}, json_data = {json_data}, headers = {headers}, consumer_ip = {consumer_ip}")

            try:
                response = await self.session.post(url, data=json_data, headers=headers, timeout=10)
            except asyncio.TimeoutError:
                logging.error(f"Request to {url} timed out.")
                raise
        else:
            # Mock request in TEST environment
            logging.debug(f"Queuing JobChunk to consumer: url = {url}, json_data = {json_data}, headers = {headers}, consumer_ip = {consumer_ip}")
            request = test_utils.make_mocked_request("POST", url, headers=headers)
            await asyncio.sleep(1)
            response = web.Response(status=200)

        return response

    async def submit_infernal_job(self, consumer_ip, consumer_port, job_id, query):
        await self.init_session()

        # prepare the data for request
        url = f"http://{consumer_ip}:{consumer_port}/{CONSUMER_SUBMIT_INFERNAL_JOB_URL}"
        json_data = json.dumps({"job_id": job_id, "sequence": query})
        headers = {"content-type": "application/json"}

        if ENVIRONMENT != "TEST":
            logging.debug(f"Queuing InfernalJob to consumer: url = {url}, json_data = {json_data}, headers = {headers}, consumer_ip = {consumer_ip}")

            try:
                response = await self.session.post(url, data=json_data, headers=headers, timeout=10)
            except asyncio.TimeoutError:
                logging.error(f"Request to {url} timed out.")
                raise
        else:
            # Mock request in TEST environment
            logging.debug(f"Queuing InfernalJob to consumer: url = {url}, json_data = {json_data}, headers = {headers}, consumer_ip = {consumer_ip}")
            request = test_utils.make_mocked_request("POST", url, headers=headers)
            await asyncio.sleep(1)
            response = web.Response(status=200)

        return response

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

import json
import logging
import random

from aiohttp.test_utils import unittest_run_loop
from aiohttp.test_utils import AioHTTPTestCase

from sequence_search.producer.__main__ import create_app
from sequence_search.producer.settings import MIN_QUERY_LENGTH, MAX_QUERY_LENGTH

"""
Run these tests with:

ENVIRONMENT=TEST python3 -m unittest sequence_search.producer.tests.test_submit_job
"""


class SubmitJobTestCase(AioHTTPTestCase):
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        self.url = app.router["submit-job"].url_for()
        return app

    @unittest_run_loop
    async def test_submit_job_post_fail_query(self):
        data = json.dumps({"query": "THIS_IS_NOT_A_PROPER_NUCLEOTIDE_SEQUENCE", "databases": ["mirbase"]})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            assert text == "Input query is not a valid nucleotide sequence: " \
                           "'THIS_IS_NOT_A_PROPER_NUCLEOTIDE_SEQUENCE'\n"

    @unittest_run_loop
    async def test_submit_job_post_fail_databases(self):
        data = json.dumps({"query": "ACGCTCGTAGC", "databases": ["foobase"]})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            assert text == "Database foobase is not a valid RNAcentral database"

    @unittest_run_loop
    async def test_submit_job_post_short_sequence(self):
        data = json.dumps({"query": "CU", "databases": ["mirbase"]})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            assert text == "The sequence cannot be shorter than %s nucleotides.\n" % MIN_QUERY_LENGTH

    @unittest_run_loop
    async def test_submit_job_post_long_sequence(self):
        sequence = ''.join(random.choices('ACUG', k=MAX_QUERY_LENGTH+1))
        data = json.dumps({"query": sequence, "databases": ["mirbase"]})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            assert text == "The sequence cannot be longer than %s nucleotides.\n" % MAX_QUERY_LENGTH

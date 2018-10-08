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
import logging
import os

from aiohttp.test_utils import unittest_run_loop

from ..main import create_app
from aiohttp.test_utils import AioHTTPTestCase


"""
Run these tests with:

ENVIRONMENT=TEST python -m unittest producer.tests.test_submit_job
"""


class SubmitJobTestCase(AioHTTPTestCase):
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        self.url = app.router["submit-job"].url_for()
        return app

    @unittest_run_loop
    async def test_submit_job_post_fail_query(self):
        data = json.dumps({"query": "THIS_IS_NOT_A_PROPER_NUCLEOTIDE_SEQUENCE", "databases": "mirbase"})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            assert text == "Input query should be a nucleotide sequence and contain only {ATGCU} characters," \
                           " found: 'THIS_IS_NOT_A_PROPER_NUCLEOTIDE_SEQUENCE'."

    @unittest_run_loop
    async def test_submit_job_post_fail_databases(self):
        data = json.dumps({"query": "ACGCTCGTAGC", "databases": "foobase"})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            assert text == "Database 'foobase' not in list of RNACentral databases"

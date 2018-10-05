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

from aiohttp.test_utils import unittest_run_loop

from ..main import create_app
from .consumer_test_case import ConsumerTestCase


"""
Run these tests with:

ENVIRONMENT=test python -m unittest consumer.tests.test_submit_job
"""


class SubmitJobTestCase(ConsumerTestCase):
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        self.url = app.router["submit-job"].url_for()
        return app

    @unittest_run_loop
    async def test_submit_job_post_success(self):
        data = json.dumps({"job_id": 1, "sequence": "ACGCTCGTAGC", "database": "mirbase"})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 200
            text = await response.text()
            print(text)

    @unittest_run_loop
    async def test_submit_job_post_fail_job_id(self):
        data = json.dumps({"job_id": 2, "sequence": "ACGCTCGTAGC", "database": "mirbase"})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            import pdb
            pdb.set_trace()
            print(text)

    @unittest_run_loop
    async def test_submit_job_post_fail_databases(self):
        data = json.dumps({"job_id": 3, "sequence": "ACGCTCGTAGC", "database": "foobase"})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            assert text == "Database argument is wrong: 'foobase' is not one of RNAcentral databases."

    @unittest_run_loop
    async def test_submit_job_post_fail_sequence(self):
        data = json.dumps({"job_id": 4, "sequence": "THIS_IS_NOT_A_PROPER_NUCLEOTIDE_SEQUENCE", "database": "mirbase"})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            assert text == "Input sequence should be nucleotide sequence and contain only " \
                           "{ATGCU} characters, found: 'THIS_IS_NOT_A_PROPER_NUCLEOTIDE_SEQUENCE'."

    @unittest_run_loop
    async def test_sumbit_job_post_fail_not_enough_arguments(self):
        data = json.dumps({"job_id": 5})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 400
            text = await response.text()
            assert text == 'Bad input'

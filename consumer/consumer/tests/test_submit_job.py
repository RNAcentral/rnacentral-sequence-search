import json
import logging
import os
import shutil

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web

from ..main import create_app
from .consumer_test_case import ConsumerTestCase


"""
Run these tests with:

python -m unittest consumer.tests.test_submit_job
"""


class SubmitJobTestCase(ConsumerTestCase):
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        return create_app()

    @unittest_run_loop
    async def test_submit_job_post_success(self):
        url = self.app.router["submit-job"].url_for()
        data = json.dumps({"job_id": 1, "sequence": "ACGCTCGTAGC", "databases": ["mirbase"]})
        async with self.client.post(path=url, data=data) as response:
            assert response.status == 200
            text = await response.text()
            print(text)

    @unittest_run_loop
    async def test_submit_job_post_fail_job_id(self):
        pass

    @unittest_run_loop
    async def test_submit_job_post_fail_databases(self):
        pass

    @unittest_run_loop
    async def test_submit_job_post_fail_sequence(self):
        pass

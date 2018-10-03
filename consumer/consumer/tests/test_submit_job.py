import json
import logging

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web

from ..main import create_app


"""
Run these tests with:

python -m unittest consumer.tests.test_submit_job
"""


class SubmitJobTestCase(AioHTTPTestCase):
    def setUpAsync(self):
        # TODO: create temporary queries and results directories for testing purposes, modify settings accordingly
        pass

    def tearDown(self):
        pass

    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        return create_app()

    @unittest_run_loop
    async def test_submit_job_post_success(self):
        url = self.app.router["submit-job"].url_for()
        data = json.dumps({"job_id": 1, "sequence": "ACGCTCGTAGC", "databases": ["mirbase"]})
        resp = await self.client.post(path=url, data=data)
        assert resp.status == 200
        text = await resp.text()
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

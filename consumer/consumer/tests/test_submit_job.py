from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web

from ..main import create_app


class SubmitJobTestCase(AioHTTPTestCase):
    async def get_application(self):
        return create_app()

    @unittest_run_loop
    async def test_submit_job_post_success(self):
        resp = await self.client.request("GET", "/")
        assert resp.status == 200
        text = await resp.text()
        assert "Hello, world" in text

    @unittest_run_loop
    async def test_submit_job_post_fail_job_id(self):
        resp = await self.client.post("submit-job", data={"job_id": 1, "sequence": "ACGCTCGTAGC", "databases": ["mirbase"]}, content_type="application/json")
        assert resp.status == 403
        text = await resp.text()
        assert text == ""

    @unittest_run_loop
    async def test_submit_job_post_fail_databases(self):
        pass

    @unittest_run_loop
    async def test_submit_job_post_fail_sequence(self):
        pass

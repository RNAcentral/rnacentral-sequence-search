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
import datetime

from aiohttp.test_utils import unittest_run_loop

from ..main import create_app
from ..models import Job, JobChunk
from aiohttp.test_utils import AioHTTPTestCase


"""
Run these tests with:

ENVIRONMENT=TEST python -m unittest producer.tests.test_job_status
"""


class SubmitJobTestCase(AioHTTPTestCase):
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        return app

    async def setUpAsync(self):
        await super().setUpAsync()

        logging.info("settings = %s" % self.app['settings'].__dict__)

        self.job_id = await self.app['connection'].scalar(
            Job.insert().values(query='', submitted=datetime.datetime.now(), status='started')
        )

        await self.app['connection'].scalar(
            JobChunk.insert().values(
                job_id=self.job_id,
                database='mirbase',
                submitted=datetime.datetime.now(),
                status='started'
            )
        )
        await self.app['connection'].scalar(
            JobChunk.insert().values(
                job_id=self.job_id,
                database='pombase',
                submitted=datetime.datetime.now(),
                status='started'
            )
        )

    async def tearDownAsync(self):
        await self.app['connection'].execute('DELETE FROM job_chunks')
        await self.app['connection'].execute('DELETE FROM jobs')

        await super().tearDownAsync()

    @unittest_run_loop
    async def test_job_status_success(self):
        url = self.app.router["job-status"].url_for(job_id=str(self.job_id))
        async with self.client.get(path=url) as response:
            assert response.status == 200
            data = await response.json()
            assert data == {
                'job_id': str(self.job_id),
                'status': 'started',
                'chunks': [{'database': 'mirbase', 'status': 'started'}, {'database': 'pombase', 'status': 'started'}]
            }

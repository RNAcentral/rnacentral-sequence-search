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

import datetime
import logging
import uuid

from aiohttp.test_utils import unittest_run_loop

from sequence_search.producer.__main__ import create_app
from sequence_search.db.models import Job, JobChunk, JOB_STATUS_CHOICES, JOB_CHUNK_STATUS_CHOICES
from aiohttp.test_utils import AioHTTPTestCase


"""
Run these tests with:

ENVIRONMENT=TEST python3 -m unittest sequence_search.producer.tests.test_job_status
"""


class SubmitJobTestCase(AioHTTPTestCase):
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        return app

    async def setUpAsync(self):
        await super().setUpAsync()

        logging.info("settings = %s" % self.app['settings'].__dict__)

        self.job_id = str(uuid.uuid4())

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

            await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database='mirbase',
                    submitted=datetime.datetime.now(),
                    status=JOB_CHUNK_STATUS_CHOICES.started
                )
            )
            await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database='pombase',
                    submitted=datetime.datetime.now(),
                    status=JOB_CHUNK_STATUS_CHOICES.started
                )
            )

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM job_chunk_results')
            await connection.execute('DELETE FROM job_chunks')
            await connection.execute('DELETE FROM jobs')

        await super().tearDownAsync()

    @unittest_run_loop
    async def test_job_status_success(self):
        url = self.app.router["job-status"].url_for(job_id=str(self.job_id))
        async with self.client.get(path=url) as response:
            assert response.status == 200
            data = await response.json()

            assert data == {
                'job_id': str(self.job_id),
                'query': '',
                'description': None,
                'status': JOB_STATUS_CHOICES.started,
                'r2dt_id': None,
                'r2dt_date': None,
                'elapsedTime': 0,
                'now': data['now'],
                'chunks': [
                    {'database': 'mirbase', 'status': JOB_CHUNK_STATUS_CHOICES.started, 'elapsedTime': 0},
                    {'database': 'pombase', 'status': JOB_CHUNK_STATUS_CHOICES.started, 'elapsedTime': 0}
                ]
            }

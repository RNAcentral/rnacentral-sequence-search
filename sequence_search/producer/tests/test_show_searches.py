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
from sequence_search.db.models import Job, JOB_STATUS_CHOICES
from aiohttp.test_utils import AioHTTPTestCase


"""
Run these tests with:

ENVIRONMENT=TEST python3 -m unittest sequence_search.producer.tests.test_show_searches
"""


class ShowSearchesTestCase(AioHTTPTestCase):
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        return app

    async def setUpAsync(self):
        await super().setUpAsync()

        logging.info("settings = %s" % self.app['settings'].__dict__)

        self.job_id_01 = str(uuid.uuid4())
        self.job_id_02 = str(uuid.uuid4())
        self.job_id_03 = str(uuid.uuid4())

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id_01,
                    query='',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

            await connection.execute(
                Job.insert().values(
                    id=self.job_id_02,
                    query='',
                    submitted=datetime.datetime.now() - datetime.timedelta(days=2),
                    status=JOB_STATUS_CHOICES.started
                )
            )

            await connection.execute(
                Job.insert().values(
                    id=self.job_id_03,
                    query='',
                    submitted=datetime.datetime.now() - datetime.timedelta(days=8),
                    status=JOB_STATUS_CHOICES.started
                )
            )

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM jobs')

        await super().tearDownAsync()

    @unittest_run_loop
    async def test_show_searches_success(self):
        url = self.app.router["show-searches"].url_for()
        async with self.client.get(path=url) as response:
            assert response.status == 200
            data = await response.json()

            assert data == [
                {"count": 3, "avg_time": 0, "search": "all"},
                {"count": 1, "avg_time": 0, "search": "last-24-hours"},
                {"count": 2, "avg_time": 0, "search": "last-week"}
            ]

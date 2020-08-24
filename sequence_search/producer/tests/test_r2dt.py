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
import json
import logging
import uuid

from aiohttp.test_utils import AioHTTPTestCase
from aiohttp.test_utils import unittest_run_loop

from sequence_search.db.models import Job, JOB_STATUS_CHOICES
from sequence_search.db.settings import get_postgres_credentials
from sequence_search.producer.__main__ import create_app


"""
Run these tests with:

ENVIRONMENT=TEST python3 -m unittest sequence_search.producer.tests.test_r2dt
"""


class R2DTTestCase(AioHTTPTestCase):
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        settings = get_postgres_credentials(ENVIRONMENT='TEST')
        app.update(name='test', settings=settings)
        return app

    async def setUpAsync(self):
        await super().setUpAsync()
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

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM jobs')

        await super().tearDownAsync()

    @unittest_run_loop
    async def test_r2dt(self):
        data = json.dumps({"r2dt_id": "r2dt-R20200819-142803-0200-7914324-p1m"})
        url = self.app.router["r2dt"].url_for(job_id=str(self.job_id))
        async with self.client.patch(path=url, data=data) as response:
            data = await response.json()
            assert data['r2dt_id'] == "r2dt-R20200819-142803-0200-7914324-p1m"

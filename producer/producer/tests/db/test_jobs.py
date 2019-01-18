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
import datetime

from aiohttp.test_utils import unittest_run_loop
from aiohttp.test_utils import AioHTTPTestCase
import sqlalchemy as sa

from ...main import create_app
from ...models import Job, JobChunk, JobChunkResult, Consumer
from ...db.jobs import set_job_status, get_job_query


class SetJobStatusTestCase(AioHTTPTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python3 -m unittest producer.tests.db.test_jobs.SetJobStatusTestCase
    """
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        return app

    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.job_id = await connection.scalar(
                Job.insert().values(query='AACAGCATGAGTGCGCTGGATGCTG', submitted=datetime.datetime.now(), status='started')
            )

    @unittest_run_loop
    async def test_set_job_status_error(self):
        await set_job_status(self.app['engine'], self.job_id, 'error')


class GetJobQueryTestCase(AioHTTPTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python3 -m unittest producer.tests.db.test_jobs.GetJobQueryTestCase
    """
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        return app

    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.job_id = await connection.scalar(
                Job.insert().values(query='AACAGCATGAGTGCGCTGGATGCTG', submitted=datetime.datetime.now(), status='started')
            )

    @unittest_run_loop
    async def test_set_job_status_error(self):
        query = await get_job_query(self.app['engine'], self.job_id)
        assert query == 'AACAGCATGAGTGCGCTGGATGCTG'

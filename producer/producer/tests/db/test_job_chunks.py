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
from ...db.job_chunks import find_highest_priority_job_chunk, set_job_chunk_status


class FindHighestPriorityJobChunkTestCase(AioHTTPTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python3 -m unittest producer.tests.db.test_job_chunks.FindHighestPriorityJobChunkTestCase
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

            self.job_id2 = await connection.scalar(
                Job.insert().values(query='CGTGCTGAATAGCTGGAGAGGCTCAT', submitted=datetime.datetime.now(), status='started')
            )

            self.job_chunk_id1 = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database='mirbase',
                    submitted=datetime.datetime.now(),
                    status='started'
                )
            )

            self.job_chunk_id2 = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id2,
                    database='pombase',
                    submitted=datetime.datetime.now(),
                    status='started'
                )
            )

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM job_chunk_results')
            await connection.execute('DELETE FROM job_chunks')
            await connection.execute('DELETE FROM jobs')

            await super().tearDownAsync()

    @unittest_run_loop
    async def test_find_highest_priority_job_chunk(self):
        job_id, job_chunk_id, database = await find_highest_priority_job_chunk(self.app['engine'])

        assert job_id == self.job_id
        assert job_chunk_id == self.job_chunk_id1
        assert database == 'mirbase'


class SetJobChunkStatusTestCase(AioHTTPTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python3 -m unittest producer.tests.db.test_job_chunks.SetJobChunkStatusTestCase
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

            self.job_chunk_id = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database='mirbase',
                    submitted=datetime.datetime.now(),
                    status='pending'
                )
            )

    @unittest_run_loop
    async def test_job_chunk_started(self):
        await set_job_chunk_status(self.app['engine'], self.job_id, 'mirbase', 'started')

    @unittest_run_loop
    async def test_except_error_in_job_chunk(self):
        await set_job_chunk_status(self.app['engine'], self.job_id, 'mirbase', 'error')

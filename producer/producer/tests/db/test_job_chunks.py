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
from ...db.job_chunks import save_job_chunk, find_highest_priority_job_chunk, get_consumer_ip_from_job_chunk, \
    set_job_chunk_status, set_job_chunk_results


class SaveJobChunkTestCase(AioHTTPTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python3 -m unittest producer.tests.db.test_job_chunks.SaveJobChunkTestCase
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

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM job_chunk_results')
            await connection.execute('DELETE FROM job_chunks')
            await connection.execute('DELETE FROM jobs')
            await connection.execute('DELETE FROM consumer')

            await super().tearDownAsync()

    @unittest_run_loop
    async def test_set_job_status_error(self):
        job_chunk_id = await save_job_chunk(self.app['engine'], job_id=self.job_id, database='mirbase')
        assert job_chunk_id is not None


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
            await connection.execute('DELETE FROM consumer')

            await super().tearDownAsync()

    @unittest_run_loop
    async def test_find_highest_priority_job_chunk(self):
        job_id, job_chunk_id, database = await find_highest_priority_job_chunk(self.app['engine'])

        assert job_id == self.job_id
        assert job_chunk_id == self.job_chunk_id1
        assert database == 'mirbase'


class GetConsumerIpFromJobChunkTestCase(AioHTTPTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python3 -m unittest producer.tests.db.test_job_chunks.GetConsumerIpFromJobChunkTestCase
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

            await connection.execute(
                Consumer.insert().values(ip='192.168.0.2', status='busy')
            )

            self.job_chunk_id = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database='mirbase',
                    submitted=datetime.datetime.now(),
                    status='pending',
                    consumer='192.168.0.2'
                )
            )

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM job_chunk_results')
            await connection.execute('DELETE FROM job_chunks')
            await connection.execute('DELETE FROM jobs')
            await connection.execute('DELETE FROM consumer')

        await super().tearDownAsync()

    @unittest_run_loop
    async def test_get_consumer_ip_from_job_chunk(self):
        consumer_ip = await get_consumer_ip_from_job_chunk(self.app['engine'], self.job_chunk_id)
        print(consumer_ip)
        assert consumer_ip == '192.168.0.2'


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

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM job_chunk_results')
            await connection.execute('DELETE FROM job_chunks')
            await connection.execute('DELETE FROM jobs')
            await connection.execute('DELETE FROM consumer')

        await super().tearDownAsync()

    @unittest_run_loop
    async def test_job_chunk_started(self):
        await set_job_chunk_status(self.app['engine'], self.job_id, 'mirbase', 'started')

    @unittest_run_loop
    async def test_except_error_in_job_chunk(self):
        await set_job_chunk_status(self.app['engine'], self.job_id, 'mirbase', 'error')


class SetJobChunkResultsTestCase(AioHTTPTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python3 -m unittest producer.tests.db.test_job_chunks.SetJobChunkResultsTestCase
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

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM job_chunk_results')
            await connection.execute('DELETE FROM job_chunks')
            await connection.execute('DELETE FROM jobs')
            await connection.execute('DELETE FROM consumer')

            await super().tearDownAsync()

    @unittest_run_loop
    async def test_set_job_chunk_results(self):
        results = [{
            "rnacentral_id": 'URS000075D2D2',
            "description": 'Mus musculus miR - 1195 stem - loop',
            "score": 6.5,
            "bias": 0.7,
            "e_value": 32.0,
            "target_length": 98,
            "alignment": "Query  8 GAGUUUGAGACCAGCCUGGCCA 29\n| | | | | | | | | | | | | | | | | |\nSbjct_10090\n22\nGAGUUCGAGGCCAGCCUGCUCA\n43",
            "alignment_length": 22,
            "gap_count": 0,
            "match_count": 18,
            "nts_count1": 22,
            "nts_count2": 0,
            "identity": 81.8181818181818,  # conversion to float in DB trims some digits
            "query_coverage": 73.3333333333333,  # converstion to float in DB trims some digits
            "target_coverage": 0.0,
            "gaps": 0.0,
            "query_length": 30,
            "result_id": 1
        }]

        set_job_chunk_results(self.app['engine'], self.job_id, database='mirbase', results=results)

        async with self.app['engine'].acquire() as connection:
            query = sa.text('''
                SELECT rnacentral_id, description 
                FROM job_chunk_results 
                WHERE job_chunk_id=:job_chunk_id
            ''')

            async for row in await connection.execute(query, job_chunk_id=self.job_chunk_id):
                assert row.rnacentral_id == 'URS000075D2D2'
                assert row.description == 'Mus musculus miR - 1195 stem - loop'

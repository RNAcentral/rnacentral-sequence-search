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
import uuid

from aiohttp.test_utils import unittest_run_loop

from .test_base import DBTestCase
from . import DoesNotExist
from .models import Job, JobChunk, Consumer
from .job_chunks import save_job_chunk, find_highest_priority_job_chunk, get_consumer_ip_from_job_chunk, \
    set_job_chunk_status, get_job_chunk_from_job_and_database


class GetJobChunkFromJobAndDatabase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_job_chunks.GetJobChunkFromJobAndDatabase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.job_id = str(uuid.uuid4())

            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    submitted=datetime.datetime.now(),
                    status='started'
                )
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
    async def test_get_job_chunk_from_job_and_database_success(self):
        job_chunk_id = await get_job_chunk_from_job_and_database(
            self.app['engine'],
            job_id=self.job_id,
            database='mirbase'
        )
        assert job_chunk_id == self.job_chunk_id

    @unittest_run_loop
    async def test_get_job_chunk_from_job_and_database_does_not_exist(self):
        try:
            job_chunk_id = await get_job_chunk_from_job_and_database(
                self.app['engine'],
                job_id=str(uuid.uuid4()),
                database='mirbase'
            )
        except Exception as e:
            assert type(e) == DoesNotExist


class SaveJobChunkTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_job_chunks.SaveJobChunkTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.job_id = await connection.scalar(
                Job.insert().values(query='AACAGCATGAGTGCGCTGGATGCTG', submitted=datetime.datetime.now(), status='started')
            )

    @unittest_run_loop
    async def test_set_job_status_error(self):
        job_chunk_id = await save_job_chunk(self.app['engine'], job_id=self.job_id, database='mirbase')
        assert job_chunk_id is not None


class FindHighestPriorityJobChunkTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_job_chunks.FindHighestPriorityJobChunkTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.job_id = await connection.scalar(
                Job.insert().values(id=uuid.uuid4(), query='AACAGCATGAGTGCGCTGGATGCTG', submitted=datetime.datetime.now(), status='started')
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

    @unittest_run_loop
    async def test_find_highest_priority_job_chunk(self):
        job_id, job_chunk_id, database = await find_highest_priority_job_chunk(self.app['engine'])

        assert job_id == self.job_id
        assert job_chunk_id == self.job_chunk_id1
        assert database == 'mirbase'


class GetConsumerIpFromJobChunkTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_job_chunks.GetConsumerIpFromJobChunkTestCase
    """
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

    @unittest_run_loop
    async def test_get_consumer_ip_from_job_chunk(self):
        consumer_ip = await get_consumer_ip_from_job_chunk(self.app['engine'], self.job_chunk_id)
        print(consumer_ip)
        assert consumer_ip == '192.168.0.2'


class SetJobChunkStatusTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_job_chunks.SetJobChunkStatusTestCase
    """
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

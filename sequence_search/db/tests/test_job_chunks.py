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

from sequence_search.db.tests.test_base import DBTestCase
from sequence_search.db import DoesNotExist
from sequence_search.db.models import Job, JobChunk, Consumer, JOB_STATUS_CHOICES, JOB_CHUNK_STATUS_CHOICES, \
    CONSUMER_STATUS_CHOICES
from sequence_search.db.jobs import find_highest_priority_jobs, database_used_in_search
from sequence_search.db.job_chunks import save_job_chunk, get_consumer_ip_from_job_chunk, set_job_chunk_status, \
    get_job_chunk_from_job_and_database


class GetJobChunkFromJobAndDatabase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_job_chunks.GetJobChunkFromJobAndDatabase
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
                    status=JOB_STATUS_CHOICES.started
                )
            )

            self.job_chunk_id = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database='mirbase',
                    submitted=datetime.datetime.now(),
                    status=JOB_CHUNK_STATUS_CHOICES.pending
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

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_job_chunks.SaveJobChunkTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        self.job_id = str(uuid.uuid4())

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

    @unittest_run_loop
    async def test_set_job_status_error(self):
        job_chunk_id = await save_job_chunk(self.app['engine'], job_id=self.job_id, database='mirbase')
        assert job_chunk_id is not None


class FindHighestPriorityJobChunkTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_job_chunks.FindHighestPriorityJobChunkTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        self.job_id = str(uuid.uuid4())
        self.job_id2 = str(uuid.uuid4())

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    submitted=datetime.datetime.now(),
                    priority='low',
                    status=JOB_STATUS_CHOICES.started
                )
            )

            await connection.execute(
                Job.insert().values(
                    id=self.job_id2,
                    query='CGTGCTGAATAGCTGGAGAGGCTCAT',
                    submitted=datetime.datetime.now(),
                    priority='low',
                    status=JOB_STATUS_CHOICES.started
                )
            )

            self.job_chunk_id1 = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database='mirbase',
                    submitted=datetime.datetime.now(),
                    status=JOB_CHUNK_STATUS_CHOICES.pending
                )
            )

            self.job_chunk_id2 = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id2,
                    database='pombase',
                    submitted=datetime.datetime.now(),
                    status=JOB_CHUNK_STATUS_CHOICES.pending
                )
            )

    @unittest_run_loop
    async def test_find_highest_priority_job_chunks(self):
        chunks = await find_highest_priority_jobs(self.app['engine'])
        assert len(chunks) == 2

        job_id, priority, submitted, database = chunks[0]

        assert job_id == self.job_id
        assert database == 'mirbase'

    @unittest_run_loop
    async def test_job_priority(self):
        job_id3 = str(uuid.uuid4())
        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=job_id3,
                    query='GGACGGAGGCGCGCCCGAGAUGAGUAG',
                    submitted=datetime.datetime.now(),
                    priority='high',
                    status=JOB_STATUS_CHOICES.started
                )
            )

            await connection.scalar(
                JobChunk.insert().values(
                    job_id=job_id3,
                    database='rfam',
                    submitted=datetime.datetime.now(),
                    status=JOB_CHUNK_STATUS_CHOICES.pending
                )
            )

        chunks = await find_highest_priority_jobs(self.app['engine'])
        assert len(chunks) == 3

        job_id, priority, submitted, database = chunks[0]

        assert job_id == job_id3
        assert database == 'rfam'


class GetConsumerIpFromJobChunkTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_job_chunks.GetConsumerIpFromJobChunkTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        self.job_id = str(uuid.uuid4())

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

            await connection.execute(
                Consumer.insert().values(ip='192.168.0.2', status=CONSUMER_STATUS_CHOICES.busy)
            )

            self.job_chunk_id = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database='mirbase',
                    submitted=datetime.datetime.now(),
                    status=JOB_CHUNK_STATUS_CHOICES.pending,
                    consumer='192.168.0.2'
                )
            )

    @unittest_run_loop
    async def test_get_consumer_ip_from_job_chunk(self):
        consumer_ip = await get_consumer_ip_from_job_chunk(self.app['engine'], self.job_chunk_id)
        assert consumer_ip == '192.168.0.2'


class SetJobChunkStatusTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_job_chunks.SetJobChunkStatusTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        self.job_id = str(uuid.uuid4())

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

            self.job_chunk_id = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database='mirbase',
                    submitted=datetime.datetime.now(),
                    status=JOB_CHUNK_STATUS_CHOICES.pending
                )
            )

    @unittest_run_loop
    async def test_job_chunk_started(self):
        job_chunk_id = await set_job_chunk_status(
            self.app['engine'], self.job_id, 'mirbase', JOB_CHUNK_STATUS_CHOICES.started
        )
        assert job_chunk_id == self.job_chunk_id

    @unittest_run_loop
    async def test_except_error_in_job_chunk(self):
        job_chunk_id = await set_job_chunk_status(
            self.app['engine'], self.job_id, 'mirbase', JOB_CHUNK_STATUS_CHOICES.error
        )
        assert job_chunk_id == self.job_chunk_id


class DatabaseUsedInSearch(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_job_chunks.DatabaseUsedInSearch
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        self.job_id = str(uuid.uuid4())
        self.databases = 'mirbase-0.fasta'

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

            self.job_chunk_id = await connection.scalar(
                JobChunk.insert().values(
                    job_id=self.job_id,
                    database=self.databases,
                    submitted=datetime.datetime.now(),
                    status=JOB_CHUNK_STATUS_CHOICES.pending
                )
            )

    @unittest_run_loop
    async def test_database_used_in_search(self):
        databases = ['mirbase-0.fasta']
        result = await database_used_in_search(self.app['engine'], self.job_id, databases)
        assert result

    @unittest_run_loop
    async def test_wrong_database_used_in_search(self):
        databases = ['pdbe-0.fasta']
        result = await database_used_in_search(self.app['engine'], self.job_id, databases)
        assert not result

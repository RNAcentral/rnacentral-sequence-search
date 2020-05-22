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

from sequence_search.db.models import Job, JobChunk, Consumer, CONSUMER_STATUS_CHOICES, JOB_STATUS_CHOICES, \
    JOB_CHUNK_STATUS_CHOICES
from sequence_search.db.consumers import get_consumer_status, set_consumer_status, find_available_consumers, \
    delegate_job_chunk_to_consumer, register_consumer_in_the_database, get_ip, set_consumer_fields
from sequence_search.db.tests.test_base import DBTestCase


class FindAvailableConsumersTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python3 -m unittest sequence_search.db.tests.test_consumers.FindAvailableConsumersTestCase

    """
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Consumer.insert().values(
                    ip='192.168.0.2',
                    status=CONSUMER_STATUS_CHOICES.available
                )
            )

            await connection.execute(
                Consumer.insert().values(
                    ip='192.168.0.3',
                    status=CONSUMER_STATUS_CHOICES.busy
                )
            )

            await connection.execute(
                Consumer.insert().values(
                    ip='192.168.0.4',
                    status=CONSUMER_STATUS_CHOICES.available
                )
            )

    @unittest_run_loop
    async def test_find_available_consumer(self):
        consumers = await find_available_consumers(self.app['engine'])

        for index, row in enumerate(consumers):
            if index == 0:
                assert row.ip == '192.168.0.2'
                assert row.status == CONSUMER_STATUS_CHOICES.available
            elif index == 1:
                assert row.ip == '192.168.0.4'
                assert row.status == CONSUMER_STATUS_CHOICES.available


class GetConsumerStatusTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_consumers.GetConsumerStatusTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.consumer_ip = '192.168.1.1'
            Consumer.insert().values(
                ip=self.consumer_ip,
                status=CONSUMER_STATUS_CHOICES.available
            )

    async def test_get_consumer_status(self):
        consumer_status = await get_consumer_status(self.app['engine'], '192.168.0.2')
        assert consumer_status == CONSUMER_STATUS_CHOICES.available


class SetConsumerStatusTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_consumers.SetConsumerStatusTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.consumer_ip = '192.168.1.1'
            await connection.execute(
                Consumer.insert().values(
                    ip=self.consumer_ip,
                    status=CONSUMER_STATUS_CHOICES.available
                )
            )

    @unittest_run_loop
    async def test_set_consumer_status(self):
        await set_consumer_status(self.app['engine'], self.consumer_ip, CONSUMER_STATUS_CHOICES.busy)

        async with self.app['engine'].acquire() as connection:
            consumer_status = await get_consumer_status(self.app['engine'], self.consumer_ip)
            assert consumer_status == CONSUMER_STATUS_CHOICES.busy


class DelegateJobChunkToConsumerTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_consumers.DelegateJobChunkToConsumerTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.consumer_ip = get_ip(self.app)
            self.consumer_port = '8000'
            await connection.execute(
                Consumer.insert().values(
                    ip=self.consumer_ip,
                    status='avaiable',
                    port=self.consumer_port
                )
            )

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
                    status=JOB_CHUNK_STATUS_CHOICES.started,
                    consumer=self.consumer_ip
                )
            )

    # TODO: fix this test
    @unittest_run_loop
    async def _test_delegate_job_to_consumer(self):
        await delegate_job_chunk_to_consumer(
            self.app['engine'],
            self.consumer_ip,
            self.consumer_port,
            self.job_id,
            'mirbase',
            'AACAGCATGAGTGCGCTGGATGCTG'
        )

        consumer_status = await get_consumer_status(self.app['engine'], self.consumer_ip)
        assert consumer_status == CONSUMER_STATUS_CHOICES.busy


class RegisterConsumerInTheDatabaseTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_consumers.RegisterConsumerInTheDatabaseTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

    @unittest_run_loop
    async def test_register_consumer_in_the_database(self):
        await register_consumer_in_the_database(self.app)
        consumer_ip = get_ip(self.app)

        consumer = await get_consumer_status(self.app['engine'], consumer_ip)
        assert consumer == CONSUMER_STATUS_CHOICES.available


class SetConsumerFieldsTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_consumers.SetConsumerFieldsTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.consumer_ip = '192.168.1.1'
            await connection.execute(
                Consumer.insert().values(
                    ip=self.consumer_ip,
                    status=CONSUMER_STATUS_CHOICES.available
                )
            )

    @unittest_run_loop
    async def test_set_consumer_fields(self):
        await set_consumer_fields(
            self.app['engine'],
            self.consumer_ip,
            CONSUMER_STATUS_CHOICES.busy,
            'infernal-job'
        )

        async with self.app['engine'].acquire() as connection:
            consumer_fields = await get_consumer_status(self.app['engine'], self.consumer_ip)
            assert consumer_fields == CONSUMER_STATUS_CHOICES.busy

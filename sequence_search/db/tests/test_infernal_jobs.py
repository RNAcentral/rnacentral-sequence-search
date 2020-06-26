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
import sqlalchemy as sa

from aiohttp.test_utils import unittest_run_loop

from sequence_search.db.tests.test_base import DBTestCase
from sequence_search.db.models import Job, InfernalJob, Consumer, JOB_CHUNK_STATUS_CHOICES
from sequence_search.db.jobs import JOB_STATUS_CHOICES
from sequence_search.db.consumers import get_ip
from sequence_search.db.infernal_job import save_infernal_job, set_infernal_job_status, set_consumer_to_infernal_job


class InfernalTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_jobs.InfernalTestCase
    """
    job_id = str(uuid.uuid4())

    async def setUpAsync(self):
        await super().setUpAsync()

        consumer_ip = get_ip(self.app)

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    description='CATE_ECOLI',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Consumer.insert().values(
                    ip=consumer_ip,
                    status='avaiable',
                    port='8000'
                )
            )

    @unittest_run_loop
    async def test_save_infernal_job(self):
        await save_infernal_job(self.app['engine'], self.job_id, priority='low')

        async with self.app['engine'].acquire() as connection:
            query = sa.text('''
                SELECT id
                FROM infernal_job
                WHERE job_id=:job_id
            ''')

            async for row in await connection.execute(query, job_id=self.job_id):
                assert row.id is not None
                break

    @unittest_run_loop
    async def test_set_infernal_job_status(self):
        await save_infernal_job(self.app['engine'], self.job_id, priority='low')
        infernal_job = await set_infernal_job_status(self.app['engine'], self.job_id, JOB_CHUNK_STATUS_CHOICES.success)

        async with self.app['engine'].acquire() as connection:
            query = sa.text('''
                SELECT id
                FROM infernal_job
                WHERE job_id=:job_id
            ''')

            async for row in await connection.execute(query, job_id=self.job_id):
                assert row.id == infernal_job
                break

    @unittest_run_loop
    async def test_set_consumer_to_infernal_job(self):
        await save_infernal_job(self.app['engine'], self.job_id, priority='low')
        consumer = get_ip(self.app)
        await set_consumer_to_infernal_job(self.app['engine'], self.job_id, consumer)

        async with self.app['engine'].acquire() as connection:
            query = sa.text('''
                SELECT consumer
                FROM infernal_job
                WHERE job_id=:job_id
            ''')

            async for row in await connection.execute(query, job_id=self.job_id):
                assert row.consumer == consumer
                break

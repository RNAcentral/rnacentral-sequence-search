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
from sequence_search.db.models import Job
from sequence_search.db.jobs import get_job, save_job, set_job_status, sequence_exists, job_exists, get_job_query,\
    JOB_STATUS_CHOICES


class GetJobTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_jobs.GetJobTestCase
    """
    job_id = str(uuid.uuid4())

    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    description='CATE_ECOLI',
                    submitted=datetime.datetime.now(),
                    priority='low',
                    status=JOB_STATUS_CHOICES.started
                )
            )

    @unittest_run_loop
    async def test_get_job(self):
        job = await get_job(self.app['engine'], self.job_id)
        assert job['id'] == self.job_id
        assert job['query'] == 'AACAGCATGAGTGCGCTGGATGCTG'
        assert job['description'] == 'CATE_ECOLI'
        assert job['submitted']
        assert job['finished'] is None
        assert job['status'] == JOB_STATUS_CHOICES.started


class SaveJobTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_jobs.SaveJobTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

    @unittest_run_loop
    async def test_save_job(self):
        job_id = await save_job(
            self.app['engine'],
            query="AACAGCATGAGTGCGCTGGATGCTG",
            description="",
            url='localhost',
            priority='low'
        )
        assert job_id is not None


class SetJobStatusTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_jobs.SetJobStatusTestCase
    """
    job_id = str(uuid.uuid4())

    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    description='',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

    @unittest_run_loop
    async def test_set_job_status_error(self):
        await set_job_status(self.app['engine'], self.job_id, JOB_STATUS_CHOICES.error)


class GetJobQueryTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_jobs.GetJobQueryTestCase
    """
    job_id = str(uuid.uuid4())

    async def setUpAsync(self):
        await super().setUpAsync()

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

    @unittest_run_loop
    async def test_set_job_status_error(self):
        query = await get_job_query(self.app['engine'], self.job_id)
        assert query == 'AACAGCATGAGTGCGCTGGATGCTG'


class JobAndSequenceExistsTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_jobs.JobAndSequenceExistsTestCase
    """
    job_id = str(uuid.uuid4())

    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    description='CATE_ECOLI',
                    submitted=datetime.datetime.now(),
                    result_in_db=True,
                    status=JOB_STATUS_CHOICES.success
                )
            )

    @unittest_run_loop
    async def test_job_exists(self):
        job = await job_exists(self.app['engine'], self.job_id)
        assert job is True

    @unittest_run_loop
    async def test_sequence_exists(self):
        job = await sequence_exists(self.app['engine'], 'AACAGCATGAGTGCGCTGGATGCTG')
        assert self.job_id in job

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

from aiohttp.test_utils import unittest_run_loop

from .test_base import DBTestCase
from .models import Job
from .jobs import save_job, set_job_status, get_job_query, JOB_STATUS_CHOICES


class SaveJobTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_jobs.SaveJobTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

    @unittest_run_loop
    async def test_set_job_status_error(self):
        job_id = await save_job(self.app['engine'], query="AACAGCATGAGTGCGCTGGATGCTG")
        assert job_id is not None


class SetJobStatusTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.test_jobs.SetJobStatusTestCase
    """
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.job_id = await connection.scalar(
                Job.insert().values(
                    query='AACAGCATGAGTGCGCTGGATGCTG',
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
    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            self.job_id = await connection.scalar(
                Job.insert().values(
                    query='AACAGCATGAGTGCGCTGGATGCTG',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

    @unittest_run_loop
    async def test_set_job_status_error(self):
        query = await get_job_query(self.app['engine'], self.job_id)
        assert query == 'AACAGCATGAGTGCGCTGGATGCTG'

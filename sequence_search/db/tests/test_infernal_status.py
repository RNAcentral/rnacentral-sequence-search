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
from sequence_search.db.models import Job, InfernalJob
from sequence_search.db.jobs import get_infernal_job_status, JOB_STATUS_CHOICES, JOB_CHUNK_STATUS_CHOICES


class InfernalStatusTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_infernal_status.InfernalStatusTestCase
    """
    job_id = str(uuid.uuid4())

    async def setUpAsync(self):
        await super().setUpAsync()

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='CACGGUGGGGGCGCGCCGGUCUCCCGGAGCGGGACCGGGUCGGAGGAUGGACGAGAAUCAC',
                    description='testing',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

        self.infernal_job_id = await connection.scalar(
            InfernalJob.insert().values(
                job_id=self.job_id,
                submitted=datetime.datetime.now(),
                status=JOB_CHUNK_STATUS_CHOICES.pending
            )
        )

    @unittest_run_loop
    async def test_get_infernal_job_status_pending(self):
        get_status = await get_infernal_job_status(self.app['engine'], self.job_id)
        assert get_status['status'] == 'pending'

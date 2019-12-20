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
from sequence_search.db.models import Job, InfernalJob
from sequence_search.db.jobs import get_infernal_job_results, JOB_STATUS_CHOICES, JOB_CHUNK_STATUS_CHOICES
from sequence_search.db.infernal_results import set_infernal_job_results


class InfernalResultTestCase(DBTestCase):
    """
    Run this test with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests.test_infernal_results.InfernalResultTestCase
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

        self.results = [
            {
                'target_name': 'SSU_rRNA_eukarya',
                'accession_rfam': 'RF01960',
                'query_name': 'query',
                'accession_seq': '-',
                'mdl': 'cm',
                'mdl_from': 1,
                'mdl_to': 609,
                'seq_from': 1764,
                'seq_to': 2417,
                'strand': '+',
                'trunc': "3'",
                'pipeline_pass': 3,
                'gc': 0.56,
                'bias': 0.0,
                'score': 559.2,
                'e_value': 4.6e-167,
                'inc': '!',
                'description': 'Eukaryotic small subunit ribosomal RNA',
            }
        ]

    @unittest_run_loop
    async def test_set_infernal_job_results(self):
        await set_infernal_job_results(self.app['engine'], self.job_id, results=self.results)

        async with self.app['engine'].acquire() as connection:
            query = sa.text('''
                SELECT id
                FROM infernal_job
                WHERE job_id=:job_id
            ''')

            async for row in await connection.execute(query, job_id=self.job_id):
                infernal_job_id = row.id
                break

        async with self.app['engine'].acquire() as connection:
            query = sa.text('''
                SELECT target_name
                FROM infernal_result
                WHERE infernal_job_id=:infernal_job_id
            ''')

            async for row in await connection.execute(query, infernal_job_id=infernal_job_id):
                assert row.target_name == 'SSU_rRNA_eukarya'
                break

    @unittest_run_loop
    async def test_get_infernal_job_results(self):
        await set_infernal_job_results(self.app['engine'], self.job_id, results=self.results)
        result = await get_infernal_job_results(self.app['engine'], self.job_id)
        assert result == [{key: value for key, value in d.items() if key != 'infernal_job_id'} for d in self.results]

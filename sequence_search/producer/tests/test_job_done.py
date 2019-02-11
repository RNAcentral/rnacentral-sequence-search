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

from ..main import create_app
from ..models import Job, JobChunk


"""
Run these tests with:

ENVIRONMENT=TEST python -m unittest producer.tests.test_job_done
"""


class JobDoneTestCase(AioHTTPTestCase):
    async def get_application(self):
        logging.basicConfig(level=logging.INFO)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        self.url = app.router["job-done"].url_for()
        return app

    async def setUpAsync(self):
        await super().setUpAsync()

        logging.info("settings = %s" % self.app['settings'].__dict__)

        async with self.app['engine'].acquire() as connection:
            self.job_id = await connection.scalar(
                Job.insert().values(query='', submitted=datetime.datetime.now(), status='started')
            )
            self.job_chunk_id = await connection.scalar(
                JobChunk.insert().values(job_id=self.job_id, database='mirbase', submitted=datetime.datetime.now(), status='started')
            )

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM job_chunk_results')
            await connection.execute('DELETE FROM job_chunks')
            await connection.execute('DELETE FROM jobs')

        await super().tearDownAsync()

    @unittest_run_loop
    async def test_submit_job_post_success(self):
        data = json.dumps({
            "job_id": self.job_id,
            "database": 'mirbase',
            "result": [
                {
                    'rnacentral_id': 'URS000075D2D2',
                    'description': '_10090  Mus musculus miR-1195 stem-loop',
                    'score': 6.5,
                    'bias': 0.7,
                    'e_value': 32.0,
                    'target_length': 98,
                    'alignment': 'Query  8 GAGUUUGAGACCAGCCUGGCCA 29\\n         ||||| ||| ||||||||  ||\\nSbjct_10090 22 GAGUUCGAGGCCAGCCUGCUCA 43',
                    'alignment_length': 22,
                    'gap_count': 0,
                    'match_count': 18,
                    'nts_count1': 22,
                    'nts_count2': 0,
                    'identity': 81.81818181818183,
                    'query_coverage': 73.33333333333333,
                    'target_coverage': 0.0,
                    'gaps': 0.0,
                    'query_length': 30,
                    'result_id': 1
                },
                {
                    'rnacentral_id': 'URS000075D2D2',
                    'description': '_10090  Mus musculus miR-1195 stem-loop',
                    'score': 0.9,
                    'bias': 0.7,
                    'e_value': 3400.0,
                    'target_length': 98,
                    'alignment': 'Query  7 GGAGUUUGAGACCAGCCUGG 26\\n          |||||  ||  ||||| ||\\nSbjct_10090 50 UGAGUUCUAGGGCAGCCAGG 69',
                    'alignment_length': 20,
                    'gap_count': 0,
                    'match_count': 14,
                    'nts_count1': 20,
                    'nts_count2': 0,
                    'identity': 70.0,
                    'query_coverage': 66.66666666666666,
                    'target_coverage': 0.0,
                    'gaps': 0.0,
                    'query_length': 30,
                    'result_id': 2
                 }
        ]
        })

        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 200

            async with self.app['engine'].acquire() as connection:
                # job_chunks = connection.execute('''
                #   SELECT *
                #   FROM {job_chunks}
                #   WHERE id={job_id}
                # '''.format(job_chunks='job_chunks', job_id=self.job_id))
                # print(job_chunks)

                query = (sa.select([JobChunk.c.job_id, JobChunk.c.database, JobChunk.c.result])
                         .where(JobChunk.c.job_id == self.job_id)  # noqa
                        )
                job_chunks = await connection.execute(query)

                for row in job_chunks:
                    print("job_id = %s, database = %s" % (row.job_id, row.database))


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
import json
import logging
import sqlalchemy as sa
import uuid

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from sequence_search.consumer.__main__ import create_app
from sequence_search.db.consumers import get_ip
from sequence_search.db.models import Job, InfernalJob
from sequence_search.db.jobs import JOB_STATUS_CHOICES


class SubmitInfernalTestCase(AioHTTPTestCase):

    job_id = str(uuid.uuid4())

    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = create_app()
        self.url = app.router["submit-infernal-job"].url_for()
        return app

    async def setUpAsync(self):
        await super().setUpAsync()

        self.consumer_ip = get_ip(self.app)

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                Job.insert().values(
                    id=self.job_id,
                    query='AGUUACGGCCAUACCUCAGAGAAUAUACCGUAUCCCGUUCGAUCUGCGAAGUUAAGCUCUGAAGGGCGUCGUCAGUACUAUAGUGGGUGACCAUAUGGGAAUACGACGUGCUGUAGCUU',
                    submitted=datetime.datetime.now(),
                    status=JOB_STATUS_CHOICES.started
                )
            )

        async with self.app['engine'].acquire() as connection:
            await connection.execute(
                InfernalJob.insert().values(
                    job_id=self.job_id,
                )
            )

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM job_chunk_results')
            await connection.execute('DELETE FROM job_chunks')
            await connection.execute('DELETE FROM infernal_result')
            await connection.execute('DELETE FROM infernal_job')
            await connection.execute('DELETE FROM jobs')
            await connection.execute('DELETE FROM consumer')
        await super().tearDownAsync()

    @unittest_run_loop
    async def test_submit_infernal_job(self):
        query = 'AGUUACGGCCAUACCUCAGAGAAUAUACCGUAUCCCGUUCGAUCUGCGAAGUUAAGCUCUGAAGGGCGUCGUCAGUACUAUAGUGGGUGACCAUAUGGGAAUACGACGUGCUGUAGCUU'
        json_data = json.dumps({"job_id": self.job_id, "sequence": query})
        headers = {'content-type': 'application/json'}

        async with self.client.post(path=self.url, data=json_data, headers=headers) as response:
            assert response.status == 201

        async with self.app['engine'].acquire() as connection:
            query = sa.text('''
                SELECT status, consumer
                FROM infernal_job
                WHERE job_id=:job_id
            ''')

            async for row in await connection.execute(query, job_id=self.job_id):
                assert row.status == JOB_STATUS_CHOICES.started
                assert row.consumer == self.consumer_ip
                break

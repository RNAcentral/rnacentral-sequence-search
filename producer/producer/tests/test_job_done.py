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

        self.job_id = await self.app['connection'].scalar(
            Job.insert().values(query='', submitted=datetime.datetime.now(), status='started')
        )
        self.job_chunk_id = await self.app['connection'].scalar(
            JobChunk.insert().values(job_id=self.job_id, database='mirbase', submitted=datetime.datetime.now(), status='started')
        )

    async def tearDownAsync(self):
        await self.app['connection'].execute('DELETE FROM job_chunks')
        await self.app['connection'].execute('DELETE FROM jobs')

        await super().tearDownAsync()

    @unittest_run_loop
    async def test_submit_job_post_success(self):
        data = json.dumps({"job_id": self.job_id, "database": 'miRBase', "result": "Scary blob with nhmmer data"})
        async with self.client.post(path=self.url, data=data) as response:
            assert response.status == 200

            # job_chunks = self.app['connection'].execute('''
            #   SELECT *
            #   FROM {job_chunks}
            #   WHERE id={job_id}
            # '''.format(job_chunks='job_chunks', job_id=self.job_id))
            # print(job_chunks)

            query = (sa.select([JobChunk.c.job_id, JobChunk.c.database, JobChunk.c.result])
                     .where(JobChunk.c.job_id == self.job_id)  # noqa
                    )
            job_chunks = await self.app['connection'].execute(query)
            for row in job_chunks:
                print("job_id = %s, database = %s, result = %s" % (row.job_id, row.database, row.result))


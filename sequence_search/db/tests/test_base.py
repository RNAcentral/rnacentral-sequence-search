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

import logging

from aiohttp import web, web_middlewares
from aiohttp.test_utils import AioHTTPTestCase

from sequence_search.db.models import init_pg
from sequence_search.db.settings import get_postgres_credentials


class DBTestCase(AioHTTPTestCase):
    """
    Base unit-test for all the tests in db. Run all tests with the following command:

    ENVIRONMENT=TEST python -m unittest sequence_search.db.tests
    """
    async def get_application(self):
        logging.basicConfig(level=logging.ERROR)  # subdue messages like 'DEBUG:asyncio:Using selector: KqueueSelector'
        app = web.Application(middlewares=[web_middlewares.normalize_path_middleware(append_slash=True)])
        settings = get_postgres_credentials(ENVIRONMENT='TEST')
        app.update(name='test', settings=settings)
        app.on_startup.append(init_pg)
        return app

    async def tearDownAsync(self):
        async with self.app['engine'].acquire() as connection:
            await connection.execute('DELETE FROM job_chunk_results')
            await connection.execute('DELETE FROM job_chunks')
            await connection.execute('DELETE FROM infernal_result')
            await connection.execute('DELETE FROM infernal_job')
            await connection.execute('DELETE FROM jobs')
            await connection.execute('DELETE FROM consumer')

            await super().tearDownAsync()

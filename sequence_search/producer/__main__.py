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

import argparse
import logging
import asyncio

import aiohttp_jinja2
import jinja2
from aiojobs.aiohttp import setup as setup_aiojobs
from aiohttp import web, web_middlewares

from . import settings
from ..db.models import init_pg, migrate
from ..db.job_chunks import find_highest_priority_job_chunk
from ..db.jobs import get_job_query
from ..db.consumers import delegate_job_chunk_to_consumer, find_available_consumers
from ..db.settings import get_postgres_credentials
from .urls import setup_routes

"""
Run either of the following commands from the parent of current directory:

adev runserver producer --livereload

python3 -m sequence_search.producer
"""


async def on_startup(app):
    # initialize database connection
    await init_pg(app)

    if app['settings'].MIGRATE:
        # create initial migrations in the database
        await migrate(app['settings'].ENVIRONMENT)

    # initialize scheduling tasks to consumers in background
    await create_consumer_scheduler(app)


async def create_consumer_scheduler(app):
    """
    Periodically runs a task that checks the status of consumers in the database and
     - schedules job_chunks to run on consumers
     - TODO: restart crashed consumers

    Stolen from:
    https://stackoverflow.com/questions/37512182/how-can-i-periodically-execute-a-function-with-asyncio
    """
    async def periodic():
        while True:
            # if there are any pending jobs and free consumers, schedule their execution
            (job_id, job_chunk_id, database) = await find_highest_priority_job_chunk(app['engine'])
            consumers = await find_available_consumers(app['engine'])

            # TODO: we're starting just 1 job_chunk at a time, but nothing prevents us from starting them all
            if job_id is not None and len(consumers) > 0:
                query = await get_job_query(app['engine'], job_id)
                await delegate_job_chunk_to_consumer(
                    engine=app['engine'],
                    consumer_ip=consumers[0].ip,
                    job_id=job_id,
                    database=database,
                    query=query
                )

            await asyncio.sleep(5)

    loop = asyncio.get_event_loop()
    task = loop.create_task(periodic())


def create_app():
    logging.basicConfig(level=logging.DEBUG)

    app = web.Application(middlewares=[
        web_middlewares.normalize_path_middleware(append_slash=True),
    ], client_max_size=4096**2)

    app.update(name='producer', settings=settings)

    # setup Jinja2 template renderer; jinja2 contains various loaders, can also try PackageLoader etc.
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(settings.PROJECT_ROOT / 'static')))

    # create db connection on startup, shutdown on exit
    for key, value in get_postgres_credentials(settings.ENVIRONMENT)._asdict().items():
        setattr(app['settings'], key, value)

    # create db connection on startup, shutdown on exit
    app.on_startup.append(on_startup)
    # app.on_cleanup.append(close_pg)

    # setup views and routes
    setup_routes(app)

    # setup middlewares
    # setup_middlewares(app)

    # setup aiojobs scheduler
    setup_aiojobs(app)

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--migrate',
        dest='MIGRATE',
        default=False,
        action='store_true',
        help='Should migrations (that clean the database) be applied on producer startup'
    )
    args = parser.parse_args()

    # update settings with args
    for key, value in vars(args).items():
        setattr(settings, key, value)

    app = create_app()
    web.run_app(app, host=app['settings'].HOST, port=app['settings'].PORT)


# Why using thread pool at all? Because there can be blocking calls: https://pymotw.com/3/asyncio/executors.html
# pool = ThreadPoolExecutor(max_workers=1)
# loop.run_in_executor(self.pool, get_request, url)
# data = deque([])

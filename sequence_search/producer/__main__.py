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

import aiohttp_jinja2
import jinja2
from aiojobs.aiohttp import setup as setup_aiojobs
from aiohttp import web, web_middlewares

from . import settings
from ..db.models import init_pg
from ..db.settings import get_postgres_credentials
from .urls import setup_routes

"""
Run either of the following commands from the parent of current directory:

adev runserver producer --livereload

python3 -m sequence_search.producer
"""


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
    app.on_startup.append(init_pg)
    # app.on_cleanup.append(close_pg)

    # setup views and routes
    setup_routes(app)

    # setup middlewares
    # setup_middlewares(app)

    # setup aiojobs scheduler
    setup_aiojobs(app)

    return app


app = create_app()


if __name__ == '__main__':
    web.run_app(app, host=app['settings'].HOST, port=app['settings'].PORT)

# Why using thread pool at all? Because there can be blocking calls: https://pymotw.com/3/asyncio/executors.html
# pool = ThreadPoolExecutor(max_workers=1)
# loop.run_in_executor(self.pool, get_request, url)
# data = deque([])

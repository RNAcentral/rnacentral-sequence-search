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

import logging

import aiohttp_jinja2
import jinja2
from aiojobs.aiohttp import setup as setup_aiojobs
from aiohttp_swagger import setup_swagger
from aiohttp import web, web_middlewares

from . import settings
from .models import init_pg
from .urls import setup_routes

"""
Run either of the following commands from the parent of current directory:

adev runserver producer --livereload

python3 -m producer.main
"""


def create_app():
    logging.basicConfig(level=logging.DEBUG)

    app = web.Application(middlewares=[
        web_middlewares.normalize_path_middleware(append_slash=True),
    ], client_max_size=2048**2)

    app.update(name='producer', settings=settings)

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('producer', 'templates'))

    # create db connection on startup, shutdown on exit
    app.on_startup.append(init_pg)
    # app.on_cleanup.append(close_pg)

    # setup views and routes
    setup_routes(app)

    # setup middlewares
    # setup_middlewares(app)

    # setup aiojobs scheduler
    setup_aiojobs(app)

    # setup swagger documentation
    setup_swagger(app, swagger_url="api/doc")

    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host=app['settings'].HOST, port=app['settings'].PORT)

# Why using thread pool at all? Because there can be blocking calls: https://pymotw.com/3/asyncio/executors.html
# pool = ThreadPoolExecutor(max_workers=1)
# loop.run_in_executor(self.pool, get_request, url)
# data = deque([])

import asyncio
import logging

import aiohttp_jinja2
import jinja2
from aiojobs.aiohttp import setup as setup_aiojobs
from aiohttp import web, web_middlewares

# from consumer.db import close_pg, init_pg
# from consumer.middlewares import setup_middlewares
from .urls import setup_routes
from .settings import settings

"""
Run either of the following commands from the parent of current directory:

adev runserver consumer --livereload

python3 -m consumer.main
"""


def create_app():
    logging.basicConfig(level=logging.DEBUG)

    app = web.Application(middlewares=[
        web_middlewares.normalize_path_middleware(append_slash=True),
    ])

    app.update(name='consumer', settings=settings)

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('consumer', 'templates'))

    # create db connection on startup, shutdown on exit
    # app.on_startup.append(init_pg)
    # app.on_cleanup.append(close_pg)

    # setup views and routes
    setup_routes(app)

    # setup middlewares
    # setup_middlewares(app)

    # setup aiojobs scheduler
    setup_aiojobs(app)

    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = create_app()

    web.run_app(app, host=settings.HOST, port=settings.PORT)

    # Why using thread pool at all? Because there can be blocking calls: https://pymotw.com/3/asyncio/executors.html
    # pool = ThreadPoolExecutor(max_workers=1)
    # loop.run_in_executor(self.pool, get_request, url)
    # data = deque([])

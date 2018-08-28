import os
import asyncio
import logging
# import sys
# from collections import deque
# from concurrent.futures import ThreadPoolExecutor

import aiohttp_jinja2
import jinja2
from aiohttp import web

# from consumer.db import close_pg, init_pg
# from consumer.middlewares import setup_middlewares
from .urls import setup_routes
from .settings import settings

"""
Run either of the following commands from the parent of current directory:

adev runserver consumer --livereload

python3 -m consumer.main
"""


def create_app(loop):
    logging.basicConfig(level=logging.DEBUG)

    app = web.Application()

    app.update(
        name='consumer',
        settings=settings
    )

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('consumer', 'templates'))

    # create db connection on startup, shutdown on exit
    # app.on_startup.append(init_pg)
    # app.on_cleanup.append(close_pg)

    # setup views and routes
    setup_routes(app)

    # setup middlewares
    # setup_middlewares(app)

    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = create_app(loop)

    web.run_app(app, host=settings.HOST, port=settings.PORT)

    # Why using thread pool at all? Because there can be blocking calls: https://pymotw.com/3/asyncio/executors.html
    # pool = ThreadPoolExecutor(max_workers=1)
    # loop.run_in_executor(self.pool, get_request, url)
    # data = deque([])

import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections import deque

import aiohttp_jinja2
import jinja2
from aiohttp import web

# from consumer.db import close_pg, init_pg
# from consumer.middlewares import setup_middlewares
from .urls import setup_routes


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        # Why using thread pool at all? Because there can be blocking calls: https://pymotw.com/3/asyncio/executors.html
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.loop = asyncio.get_event_loop()
        self.data = deque([])

    def run(self):
        app = web.Application()

        # setup Jinja2 template renderer
        aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('aiohttpdemo_polls', 'templates'))

        # create db connection on startup, shutdown on exit
        # app.on_startup.append(init_pg)
        # app.on_cleanup.append(close_pg)

        # setup views and routes
        setup_routes(app)

        # setup middlewares
        # setup_middlewares(app)

        web.run_app(app, host=self.host, port=self.port)

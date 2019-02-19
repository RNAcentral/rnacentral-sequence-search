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

from .urls import setup_routes

"""
Run either of the following commands from the parent of current directory:

python3 -m sequence_search.ebi_search_proxy.main
"""


def create_app():
    logging.basicConfig(level=logging.DEBUG)

    app = web.Application(middlewares=[
        web_middlewares.normalize_path_middleware(append_slash=True),
    ], client_max_size=2048**2)

    app.update(name='proxy')

    # setup views and routes
    setup_routes(app)

    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port='8003')

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

import aiohttp_jinja2
import os
from aiohttp import web

from .. import settings


async def result(request):
    result_id = request.match_info['result_id']
    filename = settings.RESULTS_DIR / (result_id + ".txt")
    if os.path.isfile(filename) and os.access(filename, os.R_OK):
        return web.FileResponse(filename)
    else:
        return aiohttp_jinja2.render_template('404.html', request, {})
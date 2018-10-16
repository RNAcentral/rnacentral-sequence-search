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

import os

from aiohttp import web


def file_path(job_id):
    return os.path.join('cache', job_id)


async def get(request):
    job_id = request.match_info['job_id']

    try:
        return web.Response(open(file_path(job_id)).read())
    except Exception as e:
        return web.HTTPNotFound(text=str(e))


async def post(request):
    job_id = request.match_info['job_id']

    if os.path.isfile(file_path(job_id)):
        os.remove(file_path(job_id))

    try:
        file = open(file_path(job_id), 'wb')
        file.write(request.content)
        return web.HTTPCreated()
    except Exception as e:
        return web.HTTPBadRequest(text=str(e))

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
from aiohttp import web

from ...db.models import Job


async def show_searches(request):
    async with request.app['engine'].acquire() as conn:
        cursor = await conn.execute(Job.select())
        records = await cursor.fetchall()
        jobs = []
        for row in records:
            item = dict(row.items())
            item['submitted'] = str(item['submitted'])
            item['finished'] = str(item['finished'])
            jobs.append(item)

        return web.json_response(jobs)
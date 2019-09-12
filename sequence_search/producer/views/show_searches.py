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
import datetime
from aiohttp import web

YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)
LAST_WEEK = datetime.datetime.now() - datetime.timedelta(days=7)


def get_results(records):
    jobs = []
    for row in records:
        item = dict(row.items())
        item['avg_time'] = str(datetime.timedelta(seconds=int(item['avg_time'].seconds))) if item['avg_time'] else 0
        jobs.append(item)
    return web.json_response(jobs)


async def show_searches(request):
    async with request.app['engine'].acquire() as conn:
        cursor = await conn.execute("SELECT count(*), avg(finished - submitted) as avg_time FROM jobs")
        records = await cursor.fetchall()
        return get_results(records)


async def searches_today(request):
    async with request.app['engine'].acquire() as conn:
        cursor = await conn.execute(
            "SELECT count(*), avg(finished - submitted) as avg_time FROM jobs WHERE submitted > %s", (YESTERDAY,)
        )
        records = await cursor.fetchall()
        return get_results(records)


async def searches_last_week(request):
    async with request.app['engine'].acquire() as conn:
        cursor = await conn.execute(
            "SELECT count(*), avg(finished - submitted) as avg_time FROM jobs WHERE submitted > %s", (LAST_WEEK,)
        )
        records = await cursor.fetchall()
        return get_results(records)

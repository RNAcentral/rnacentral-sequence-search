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
import json
import datetime

import aiohttp_jinja2
from aiohttp import web, client

from ..models import Job, JobChunk


async def serialize(request, data):
    """Expected data: {"job_id": job_id, "database": database, "result": ""}"""
    try:
        job_id = data['job_id']
        database = data['database']
        result = data['result']
    except (KeyError, TypeError, ValueError) as e:
        raise web.HTTPBadRequest(text='Bad input') from e

    jobs = await request.app['connection'].execute('''
        SELECT *
        FROM {job}
        WHERE id={job_id}
    '''.format(job='jobs', job_id=data['job_id']))
    print(jobs)

    if data['database'].lower() not in request.app['settings'].RNACENTRAL_DATABASES:
        raise web.HTTPBadRequest(text="Database '%s' not in list of RNACentral databases" % data['database'])
    data['database'] = data['database'].lower()

    return data


async def job_done(request):
    """
    Saves a job chunk to the database. If this was the last chunk,
    aggregates the results from all job chunks into job.
    """
    data = await request.json()
    data = await serialize(request, data)

    await request.app['connection'].execute(
        '''
        UPDATE {job_chunks}
        SET status = 'success', result='{result}'
        WHERE job_id={job_id} AND database='{database}';
        '''.format(job_chunks='job_chunks', job_id=data['job_id'], database=data['database'], result=data['result'])
    )

    return web.HTTPOk()


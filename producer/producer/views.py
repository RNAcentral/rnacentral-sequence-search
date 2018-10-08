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
import requests

from aiojobs.aiohttp import spawn
import aiohttp_jinja2
from aiohttp import web, client

from .models import Job, JobChunk


@aiohttp_jinja2.template('index.html')
async def index(request):
    return {}


async def submit_job(request):
    def validate(data):
        try:
            query = data['query']
            databases = data['databases']
        except (KeyError, TypeError, ValueError) as e:
            raise web.HTTPBadRequest(text='Bad input') from e

        # validate query
        for char in query:
            if char not in ['A', 'T', 'G', 'C', 'U']:
                raise web.HTTPBadRequest(
                    text="Input query should be a nucleotide sequence"
                         " and contain only {ATGCU} characters, found: '%s'." % query
                )

        # validate databases
        #for database in databases:
        if databases.lower() not in request.app['settings'].RNACENTRAL_DATABASES:
            raise web.HTTPBadRequest(text="Database '%s' not in list of RNACentral databases" % databases)

    data = await request.json()
    validate(data)

    job_id = await request.app['connection'].scalar(
        Job.insert().values(query=data['query'], databases=data['databases'], submitted=datetime.datetime.now(), status='started')
    )

    # for database in data["databases"]:
    requests.post(
        url="http://" + request.app['settings'].CONSUMERS[data['databases'].lower()] + '/' + request.app['settings'].CONSUMER_SUBMIT_JOB_URL,
        data=json.dumps({"job_id": job_id, "sequence": data['query'], "database": data['databases']})
    )

    return web.HTTPCreated()


async def job_status(request):
    pass


async def job_done(request):
    pass

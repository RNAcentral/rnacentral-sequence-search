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
import asyncio

from aiohttp import web
from aiojobs.aiohttp import spawn

from ..infernal_search import infernal_search
from ..settings import MAX_RUN_TIME
from ...db import DatabaseConnectionError, SQLError
from ...db.consumers import set_consumer_status, get_ip
from ...db.models import CONSUMER_STATUS_CHOICES, JOB_CHUNK_STATUS_CHOICES
from ...db.infernal_job import set_infernal_job_status, set_consumer_to_infernal_job

logger = logging.Logger('aiohttp.web')


class InfernalError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return str(self.text)


async def infernal(engine, job_id, sequence, consumer_ip):
    logger.info('Infernal search started for: job_id = %s' % job_id)
    process, filename = await infernal_search(sequence=sequence, job_id=job_id)

    try:
        task = asyncio.ensure_future(process.communicate())
        await asyncio.wait_for(task, MAX_RUN_TIME)
        return_code = process.returncode
        if return_code != 0:
            raise InfernalError("Infernal process returned non-zero status code")
    except asyncio.TimeoutError as e:
        logger.warning('Infernal timeout for: job_id = %s' % job_id)
        process.kill()
        # TODO: what do we do in case we lost the database connection here?
        await set_infernal_job_status(engine, job_id, status=JOB_CHUNK_STATUS_CHOICES.timeout)
    except Exception as e:
        logger.error('Infernal error for: job_id = %s' % job_id)
        # TODO: what do we do in case we lost the database connection here?
        await set_infernal_job_status(engine, job_id, status=JOB_CHUNK_STATUS_CHOICES.error)
    else:
        logger.info('Infernal search success for: job_id = %s' % job_id)

        # save results of the infernal job to the database
        # ...

        # update infernal status
        await set_infernal_job_status(engine, job_id, status=JOB_CHUNK_STATUS_CHOICES.success)

        # update consumer status
        await set_consumer_status(engine, consumer_ip, CONSUMER_STATUS_CHOICES.available)


async def submit_infernal_job(request):
    # validate the data
    data = await request.json()
    try:
        engine = request.app['engine']
        job_id = data['job_id']
        sequence = data['sequence']
    except (KeyError, TypeError, ValueError) as e:
        logger.error(e)
        raise web.HTTPBadRequest(text=str(e)) from e

    consumer_ip = get_ip(request.app)

    # if request was successful, save the consumer state and infernal_job state to the database
    if engine and job_id and sequence:
        try:
            await set_consumer_status(engine, consumer_ip, CONSUMER_STATUS_CHOICES.busy)
            await set_infernal_job_status(engine, job_id, status=JOB_CHUNK_STATUS_CHOICES.started)
            await set_consumer_to_infernal_job(engine, job_id, consumer_ip)
        except (DatabaseConnectionError, SQLError) as e:
            logger.error(e)
            raise web.HTTPBadRequest(text=str(e)) from e

        # spawn cmscan job in the background and return 201
        await spawn(request, infernal(engine, job_id, sequence, consumer_ip))
        return web.HTTPCreated()
    else:
        raise web.HTTPBadRequest(text='Invalid data. Engine, job_id and sequence not found.')

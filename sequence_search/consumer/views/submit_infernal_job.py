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
import asyncio
import logging

from aiohttp import web
from aiojobs.aiohttp import spawn

from ..infernal_parse import infernal_parse, alignment
from ..infernal_search import infernal_search
from ..infernal_deoverlap import infernal_deoverlap
from ..settings import MAX_RUN_TIME
from ...db import DatabaseConnectionError, SQLError
from ...db.consumers import get_ip, set_consumer_fields
from ...db.models import CONSUMER_STATUS_CHOICES, JOB_CHUNK_STATUS_CHOICES
from ...db.infernal_job import set_infernal_job_status, set_consumer_to_infernal_job
from ...db.infernal_results import set_infernal_job_results, get_infernal_result_id, save_alignment

logger = logging.Logger('aiohttp.web')


class InfernalError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return str(self.text)


async def infernal(engine, job_id, sequence, consumer_ip):
    process, filename = await infernal_search(sequence=sequence, job_id=job_id)

    try:
        task = asyncio.ensure_future(process.communicate())
        await asyncio.wait_for(task, MAX_RUN_TIME)
        if process.returncode != 0:
            raise InfernalError("Infernal process returned non-zero status code")
    except asyncio.TimeoutError:
        logger.warning('Infernal timeout for: job_id = %s' % job_id)
        process.kill()
        # TODO: what do we do in case we lost the database connection here?
        await set_infernal_job_status(engine, job_id, status=JOB_CHUNK_STATUS_CHOICES.timeout)
        await set_consumer_fields(engine, consumer_ip, CONSUMER_STATUS_CHOICES.available, job_chunk_id=None)
        return
    except Exception as e:
        logger.error('Infernal error for job_id: %s - Message: %s' % (job_id, e))
        # TODO: what do we do in case we lost the database connection here?
        await set_infernal_job_status(engine, job_id, status=JOB_CHUNK_STATUS_CHOICES.error)
        await set_consumer_fields(engine, consumer_ip, CONSUMER_STATUS_CHOICES.available, job_chunk_id=None)
        return
    else:
        logger.debug('Infernal search success for: job_id = %s' % job_id)

    process_deoverlap, file_deoverlap = await infernal_deoverlap(job_id=job_id)

    try:
        task_deoverlap = asyncio.ensure_future(process_deoverlap.communicate())
        await asyncio.wait_for(task_deoverlap, MAX_RUN_TIME)
        if process_deoverlap.returncode != 0:
            raise InfernalError("Deoverlap process returned non-zero status code")
    except asyncio.TimeoutError:
        logging.debug('Deoverlap timeout for: job_id = %s' % job_id)
        process_deoverlap.kill()
        await set_infernal_job_status(engine, job_id, status=JOB_CHUNK_STATUS_CHOICES.timeout)
        await set_consumer_fields(engine, consumer_ip, CONSUMER_STATUS_CHOICES.available, job_chunk_id=None)
    except Exception as e:
        logging.debug('Deoverlap error for job_id: %s - Message: %s' % (job_id, e))
        await set_infernal_job_status(engine, job_id, status=JOB_CHUNK_STATUS_CHOICES.error)
        await set_consumer_fields(engine, consumer_ip, CONSUMER_STATUS_CHOICES.available, job_chunk_id=None)
    else:
        logging.debug('Deoverlap success for: job_id = %s' % job_id)

        # save results of the infernal job to the database
        infernal_job_id = None
        results = infernal_parse(file_deoverlap)
        if results:
            infernal_job_id = await set_infernal_job_results(engine, job_id, results)

        # save the alignment
        output = alignment(filename)
        if output and infernal_job_id:
            for item in output:
                infernal_result_id = await get_infernal_result_id(engine, infernal_job_id, item)
                if infernal_result_id:
                    await save_alignment(engine, infernal_result_id, item['alignment'])

        # update infernal status
        await set_infernal_job_status(engine, job_id, status=JOB_CHUNK_STATUS_CHOICES.success)

        # update consumer fields
        await set_consumer_fields(engine, consumer_ip, CONSUMER_STATUS_CHOICES.available, job_chunk_id=None)


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
            await set_consumer_fields(engine, consumer_ip, CONSUMER_STATUS_CHOICES.busy, job_chunk_id='infernal-job')
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

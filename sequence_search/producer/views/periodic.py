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

from ...db.job_chunks import get_job_chunk
from ...db.jobs import get_job_query, find_highest_priority_jobs
from ...db.consumers import delegate_job_chunk_to_consumer, find_available_consumers, find_busy_consumers, \
    set_consumer_status, set_consumer_job_chunk_id, CONSUMER_STATUS_CHOICES, delegate_infernal_job_to_consumer


async def check_chunks_and_consumers(app):
    # if there are any pending jobs and free consumers, schedule their execution
    unfinished_job = await find_highest_priority_jobs(app['engine'])
    available_consumers = await find_available_consumers(app['engine'])

    for consumer in available_consumers:
        if len(unfinished_job) > 0:
            job = unfinished_job.pop(0)
            query = await get_job_query(app['engine'], job[0])
            if len(job) == 3:
                await delegate_job_chunk_to_consumer(
                    engine=app['engine'],
                    consumer_ip=consumer.ip,
                    consumer_port=consumer.port,
                    job_id=job[0],
                    database=job[2],
                    query=query
                )
            else:
                await delegate_infernal_job_to_consumer(
                    engine=app['engine'],
                    consumer_ip=consumer.ip,
                    consumer_port=consumer.port,
                    job_id=job[0],
                    query=query
                )

    busy_consumers = await find_busy_consumers(app['engine'])
    for consumer in busy_consumers:
        if consumer.job_chunk_id is None:
            await set_consumer_status(app['engine'], consumer.ip, CONSUMER_STATUS_CHOICES.available)
        elif consumer.job_chunk_id != 'infernal-job':
            job_chunk = await get_job_chunk(app['engine'], consumer.job_chunk_id)
            if job_chunk.finished is not None:
                await set_consumer_job_chunk_id(app['engine'], consumer.ip, None)
                await set_consumer_status(app['engine'], consumer.ip, CONSUMER_STATUS_CHOICES.available)


async def create_consumer_scheduler(app):
    """
    Periodically runs a task that checks the status of consumers in the database and
     - schedules job_chunks to run on consumers
     - restarts stuck consumers

    Stolen from:
    https://stackoverflow.com/questions/37512182/how-can-i-periodically-execute-a-function-with-asyncio
    """
    async def periodic():
        while True:
            loop.create_task(check_chunks_and_consumers(app))
            await asyncio.sleep(5)
            unfinished_job = await find_highest_priority_jobs(app['engine'])
            if len(unfinished_job) == 0:
                break

    loop = asyncio.get_event_loop()
    loop.create_task(periodic())

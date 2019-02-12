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

from collections import namedtuple

import sqlalchemy as sa
from aiohttp import web
import logging

from ..db.job_chunks import set_job_chunk_status, set_job_chunk_consumer
from ..db.jobs import set_job_status
from ..producer.consumer_client import ConsumerClient
import psycopg2


async def find_available_consumers(engine):
    """Returns a list of available consumers that can be used to run."""
    Consumer = namedtuple('Consumer', ['ip', 'status'])

    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                SELECT ip, status
                FROM consumer
                WHERE status='available'
            ''')
            result = await connection.execute(query)

        result = []
        async for row in connection.execute(query):
            result.append(Consumer(row[0], row[1]))

        return result

    except psycopg2.Error as e:
        logging.error(str(e))
        return  # TODO: this should raise domain-level exception instead of returning None


async def get_consumer_status(engine, consumer_ip):
    """Get consumer status from the database."""
    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                SELECT status
                FROM consumer
                WHERE ip=:consumer_ip
            ''')
            async for row in connection.execute(query, consumer_ip=consumer_ip):
                return row.status
    except psycopg2.Error as e:
        logging.error(str(e))


async def set_consumer_status(engine, consumer_ip, status):
    """Write consumer status in the database to status."""
    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                UPDATE consumer
                SET status = :status
                WHERE ip=:consumer_ip
                RETURNING consumer.*;
            ''')
            result = await connection.execute(query, consumer_ip=consumer_ip, status=status)

    except psycopg2.Error as e:
        logging.error(str(e))


async def delegate_job_chunk_to_consumer(engine, consumer_ip, job_id, database, query):
    """When a consumer returns result, set its state in the database to 'available'."""
    try:
        async with engine.acquire() as connection:
            response = await ConsumerClient().submit_job(consumer_ip, job_id, database, query)

            if response.status < 400:
                await set_consumer_status(engine, consumer_ip, 'busy')
                await set_job_chunk_status(engine, job_id, database, status="started")
                await set_job_chunk_consumer(engine, job_id, database, consumer_ip)
            else:  # TODO: attempt retry upon a failed delivery?
                await set_job_chunk_status(engine, job_id, database, status="error")
                await set_job_status(engine, job_id, status="error")

                raise web.HTTPBadRequest(text=await response.text())
    except psycopg2.Error as e:
        logging.error(str(e))

        async with engine.acquire() as connection:
            await set_job_chunk_status(engine, job_id, database, status="error")

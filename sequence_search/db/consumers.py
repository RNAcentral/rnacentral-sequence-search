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
import logging

import sqlalchemy as sa
import psycopg2
from netifaces import interfaces, ifaddresses, AF_INET

from . import DatabaseConnectionError
from .job_chunks import get_job_chunk_from_job_and_database
from ..consumer.settings import PORT
from ..producer.consumer_client import ConsumerClient
from .models import CONSUMER_STATUS_CHOICES


class ConsumerConnectionError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


async def find_available_consumers(engine):
    """Returns a list of available consumers that can be used to run."""
    Consumer = namedtuple('Consumer', ['ip', 'status', 'port', 'job_chunk_id'])

    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                SELECT ip, status, port, job_chunk_id
                FROM consumer
                WHERE status=:status
            ''')

        result = []
        async for row in connection.execute(query, status=CONSUMER_STATUS_CHOICES.available):
            result.append(Consumer(row[0], row[1], row[2], row[3]))

        return result

    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def find_busy_consumers(engine):
    """Returns a list of busy consumers that can be used to run."""
    Consumer = namedtuple('Consumer', ['ip', 'status', 'port', 'job_chunk_id'])

    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                SELECT ip, status, port, job_chunk_id
                FROM consumer
                WHERE status=:status
            ''')

        result = []
        async for row in connection.execute(query, status=CONSUMER_STATUS_CHOICES.busy):
            result.append(Consumer(row[0], row[1], row[2], row[3]))

        return result

    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def get_consumers_statuses(engine):
    """Lists statuses of all the consumers in the database."""
    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                SELECT ip, status
                FROM consumer
            ''')

            result = []
            async for row in connection.execute(query):
                result.append({"ip": row.ip, "status": row.status})
            return result
    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


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
        raise DatabaseConnectionError(str(e)) from e


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
        raise DatabaseConnectionError(str(e)) from e


async def set_consumer_job_chunk_id(engine, consumer_ip, job_id=None, database=None):
    try:
        async with engine.acquire() as connection:
            if job_id is not None:
                job_chunk_id = await get_job_chunk_from_job_and_database(engine, job_id, database)
            else:
                job_chunk_id = None

            query = sa.text('''
                UPDATE consumer
                SET job_chunk_id=:job_chunk_id
                WHERE ip=:consumer_ip
                RETURNING consumer.*;
            ''')
            result = await connection.execute(query, consumer_ip=consumer_ip, job_chunk_id=job_chunk_id)

    except psycopg2.Error as e:
        logging.error(str(e))


async def delegate_job_chunk_to_consumer(engine, consumer_ip, consumer_port, job_id, database, query):
    """When a consumer returns result, set its state in the database to 'available'."""
    try:
        async with engine.acquire() as connection:
            response = await ConsumerClient().submit_job(consumer_ip, consumer_port, job_id, database, query)

            if response.status >= 400:
                text = await response.text()
                raise ConsumerConnectionError(text)
    except psycopg2.Error as e:
        logging.error(str(e))


async def delegate_infernal_job_to_consumer(engine, consumer_ip, consumer_port, job_id, query):
    try:
        async with engine.acquire() as connection:
            response = await ConsumerClient().submit_infernal_job(consumer_ip, consumer_port, job_id, query)

            if response.status >= 400:
                text = await response.text()
                raise ConsumerConnectionError(text)
    except psycopg2.Error as e:
        logging.error(str(e))


def get_ip(app):
    """
    Stolen from:
    https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib?page=1&tab=active#tab-top
    """
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # try:
    #     # doesn't even have to be reachable
    #     s.connect(('10.255.255.255', 1))
    #     IP = s.getsockname()[0]
    # except Exception:
    #     IP = '127.0.0.1'
    # finally:
    #     s.close()
    # return IP

    addresses = []
    for ifaceName in interfaces():
        for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr': 'No IP addr'}]):
            addresses.append(i['addr'])

    # print(ifaceName, i['addr'])
    #
    # Example output:
    #
    # lo0 127.0.0.1
    # gif0 No IP addr
    # stf0 No IP addr
    # en0 10.255.6.100
    # en1 No IP addr
    # en2 No IP addr
    # bridge0 No IP addr
    # p2p0 No IP addr
    # awdl0 No IP addr
    # utun0 No IP addr
    # en4 172.22.70.60

    addresses = [address for address in addresses if address != 'No IP addr']

    # return first non-localhost IP, if available
    if app['settings'].ENVIRONMENT == 'LOCAL':
        return addresses[0]
    else:
        return addresses[1]


async def register_consumer_in_the_database(app):
    """Utility for consumer to register itself in the database."""
    try:
        async with app['engine'].acquire() as connection:
            sql_query = sa.text('''
                INSERT INTO consumer(ip, status, port)
                VALUES (:consumer_ip, :status, :port)
            ''')
            await connection.execute(
                sql_query,
                consumer_ip=get_ip(app), # 'host.docker.internal',
                status=CONSUMER_STATUS_CHOICES.available,
                port=PORT
            )
    except psycopg2.IntegrityError as e:
        pass  # this is usually a duplicate key error - which is acceptable
    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def set_consumer_fields(engine, consumer_ip, status, job_chunk_id):
    """Write consumer status and job_chunk_id as infernal-job in the database."""
    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                UPDATE consumer
                SET status = :status, job_chunk_id = :job_chunk_id
                WHERE ip=:consumer_ip
                RETURNING consumer.*;
            ''')
            await connection.execute(query, consumer_ip=consumer_ip, status=status, job_chunk_id=job_chunk_id)

    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e

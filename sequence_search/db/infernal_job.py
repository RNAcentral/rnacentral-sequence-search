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
import sqlalchemy as sa
import psycopg2

from . import DatabaseConnectionError, SQLError

from .models import InfernalJob, JOB_CHUNK_STATUS_CHOICES


async def save_infernal_job(engine, job_id, priority):
    """
    Create infernal job
    :param engine: params to connect to the db
    :param job_id: id of the job
    :param priority: priority of the job, high or low
    """
    try:
        async with engine.acquire() as connection:
            try:
                await connection.scalar(
                    InfernalJob.insert().values(
                        job_id=job_id,
                        submitted=datetime.datetime.now(),
                        priority=priority,
                        status=JOB_CHUNK_STATUS_CHOICES.pending)
                )
            except Exception as e:
                raise SQLError("Failed to save_infernal_job for job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open database connection in save_infernal_job for "
                                      "job_id = %s" % job_id) from e


async def set_infernal_job_status(engine, job_id, status):
    """
    Update the status of the infernal job
    :param engine: params to connect to the db
    :param job_id: id of the job
    :param status: an option from consumer.JOB_CHUNK_STATUS
    :return: None
    """
    finished = None
    if status == JOB_CHUNK_STATUS_CHOICES.success or \
       status == JOB_CHUNK_STATUS_CHOICES.error or \
       status == JOB_CHUNK_STATUS_CHOICES.timeout:
        finished = datetime.datetime.now()

    submitted = None
    if status == JOB_CHUNK_STATUS_CHOICES.started:
        submitted = datetime.datetime.now()

    try:
        async with engine.acquire() as connection:
            try:
                if submitted:
                    query = sa.text('''
                        UPDATE infernal_job
                        SET status = :status, submitted = :submitted
                        WHERE job_id = :job_id
                        RETURNING *;
                    ''')

                    infernal_job = None  # if connection didn't return any rows, return None
                    async for row in await connection.execute(query, job_id=job_id, status=status, submitted=submitted):
                        infernal_job = row.id
                        break
                    return infernal_job
                elif finished:
                    query = sa.text('''
                        UPDATE infernal_job
                        SET status = :status, finished = :finished
                        WHERE job_id = :job_id
                        RETURNING *;
                    ''')

                    infernal_job = None  # if connection didn't return any rows, return None
                    async for row in await connection.execute(query, job_id=job_id, status=status, finished=finished):
                        infernal_job = row.id
                        break
                    return infernal_job
                else:
                    query = sa.text('''
                        UPDATE infernal_job
                        SET status = :status
                        WHERE job_id = :job_id
                        RETURNING *;
                    ''')

                    infernal_job = None  # if connection didn't return any rows, return None
                    async for row in await connection.execute(query, job_id=job_id, status=status):
                        infernal_job = row.id
                        break
                    return infernal_job
            except Exception as e:
                raise SQLError("Failed to set_job_chunk_status in the database,"
                               " job_id = %s, status = %s" % (job_id, status)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in set_job_chunk_status, "
                                      "job_id = %s" % job_id) from e


async def set_consumer_to_infernal_job(engine, job_id, consumer_ip):
    """
    Update the infernal_job table to register the consumer who will run the job
    :param engine: params to connect to the db
    :param job_id: id of the job
    :param consumer_ip: ip address of the consumer
    :return: id or none
    """
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''
                    UPDATE infernal_job
                    SET consumer = :consumer_ip
                    WHERE job_id=:job_id
                    RETURNING *;
                ''')
                infernal_job = None  # if connection didn't return any rows, return None
                async for row in await connection.execute(query, job_id=job_id, consumer_ip=consumer_ip):
                    infernal_job = row.id
                    break
                return infernal_job
            except Exception as e:
                raise SQLError("Failed to set_consumer_to_infernal_job in the database, job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in set_consumer_to_infernal_job, "
                                      "job_id = %s" % job_id) from e

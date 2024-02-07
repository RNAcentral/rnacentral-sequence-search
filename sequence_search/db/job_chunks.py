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

from . import DatabaseConnectionError, SQLError, DoesNotExist
from .models import JobChunk, JOB_CHUNK_STATUS_CHOICES


async def get_job_chunk(engine, job_chunk_id):
    try:
        async with engine.acquire() as connection:
            query = (
                sa.select([JobChunk.c.id, JobChunk.c.job_id, JobChunk.c.database, JobChunk.c.submitted,
                           JobChunk.c.finished, JobChunk.c.consumer, JobChunk.c.status])
                .select_from(JobChunk)
                .where(JobChunk.c.id == job_chunk_id)
            )

            async for row in await connection.execute(query):
                return row

            raise DoesNotExist("JobChunk", "job_chunk_id = %s" % job_chunk_id)

    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open database connection in get_job_chunk "
                                      "for job_id = %s" % job_chunk_id) from e


async def get_job_chunk_from_job_and_database(engine, job_id, database):
    try:
        async with engine.acquire() as connection:
            query = (
                sa.select([JobChunk.c.id, JobChunk.c.job_id, JobChunk.c.database])
                .select_from(JobChunk)
                .where(sa.and_(JobChunk.c.job_id == job_id, JobChunk.c.database == database))
            )

            async for row in await connection.execute(query):
                return row.id

            raise DoesNotExist("JobChunk", "job_id = %s, database = %s" % (job_id, database))

    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open database connection in get_job_chunk_from_job_and_database "
                                      "for job_id = %s, database = %s" % (job_id, database)) from e


async def save_job_chunk(engine, job_id, database):
    """
    Jobs are divided into chunks and each chunk searches for sequences in a piece of the database.
    Here we are saving a job chunk for a specific fasta file.
    :param engine: params to connect to the db
    :param job_id: id of the job
    :param database: fasta file with RNAcentral data
    :return: id of the job chunk
    """
    try:
        async with engine.acquire() as connection:
            try:
                job_chunk_id = await connection.scalar(
                    JobChunk.insert().values(
                        job_id=job_id,
                        database=database,
                        status=JOB_CHUNK_STATUS_CHOICES.created
                    )
                )
                return job_chunk_id
            except Exception as e:
                raise SQLError("Failed to save job_chunk for job_id = %s, database = %s" % (job_id, database)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open database connection in save_job_chunk "
                                      "for job_id = %s, database = %s" % (job_id, database)) from e


async def get_consumer_ip_from_job_chunk(engine, job_chunk_id):
    try:
        async with engine.acquire() as connection:
            query = (sa.select([JobChunk.c.consumer])
                     .select_from(JobChunk)
                     .where(JobChunk.c.id == job_chunk_id)
                     .apply_labels())
            async for row in await connection.execute(query):
                return row[0]

            raise DoesNotExist("JobChunk", "job_chunk_id = %s" % job_chunk_id)
    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def set_job_chunk_status(engine, job_id, database, status, hits=None):
    """
    :param hits: total number of hits
    :param engine: params to connect to the db
    :param job_id: id of the job
    :param database: Consumer-side database (actual file name stored in the database)
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
                        UPDATE job_chunks
                        SET status = :status, submitted = :submitted
                        WHERE job_id = :job_id AND database = :database
                        RETURNING *;
                    ''')

                    id = None  # if connection didn't return any rows, return None
                    async for row in await connection.execute(query, job_id=job_id, database=database, status=status,
                                                              submitted=submitted):
                        id = row.id
                    return id
                elif finished:
                    query = sa.text('''
                        UPDATE job_chunks
                        SET status = :status, finished = :finished, hits = :hits
                        WHERE job_id = :job_id AND database = :database
                        RETURNING *;
                    ''')

                    id = None  # if connection didn't return any rows, return None
                    async for row in await connection.execute(query, job_id=job_id, database=database, status=status,
                                                              finished=finished, hits=hits):
                        id = row.id
                    return id
                else:
                    query = sa.text('''
                        UPDATE job_chunks
                        SET status = :status
                        WHERE job_id = :job_id AND database = :database
                        RETURNING *;
                    ''')

                    id = None  # if connection didn't return any rows, return None
                    async for row in await connection.execute(query, job_id=job_id, database=database, status=status):
                        id = row.id
                    return id
            except Exception as e:
                raise SQLError("Failed to set_job_chunk_status in the database,"
                               " job_id = %s, database = %s, status = %s" % (job_id, database, status)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                      "set_job_chunk_status, job_id = %s, database = %s" % (job_id, database)) from e


async def set_job_chunk_consumer(engine, job_id, database, consumer_ip):
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''
                    UPDATE job_chunks
                    SET consumer = :consumer_ip
                    WHERE job_id=:job_id AND database=:database
                    RETURNING *;
                ''')
                id = None  # if connection didn't return any rows, return None
                async for row in await connection.execute(query, job_id=job_id, database=database, consumer_ip=consumer_ip):
                    id = row.id

                return id
            except Exception as e:
                raise SQLError("Failed to set_job_chunk_consumer in the database,"
                               " job_id = %s, database = %s" % (job_id, database)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                      "set_job_chunk_status, job_id = %s, database = %s" % (job_id, database)) from e

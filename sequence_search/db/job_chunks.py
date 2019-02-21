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
from .models import Job, JobChunk


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
    try:
        async with engine.acquire() as connection:
            try:
                job_chunk_id = await connection.scalar(
                    JobChunk.insert().values(
                        job_id=job_id,
                        database=database,
                        submitted=datetime.datetime.now(),
                        status='pending'
                    )
                )
                return job_chunk_id
            except Exception as e:
                raise SQLError("Failed to save job_chunk for "
                                              "job_id = %s, database = %s", (job_id, database)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open database connection in save_job_chunk "
                                      "for job_id = %s, database = %s" % (job_id, database)) from e


async def find_highest_priority_job_chunk(engine):
    """
    Find the next job chunk to give consumers for processing.

    Returns: (job_id, job_chunk_id, database)
    """
    # among the running jobs, find the one, submitted first
    try:
        async with engine.acquire() as connection:
            try:
                select_statement = sa.select(
                    [
                        Job.c.id.label('id'),
                        Job.c.status.label('job_status'),
                        Job.c.submitted.label('submitted'),
                        JobChunk.c.job_id.label('job_id'),
                        JobChunk.c.id.label('job_chunk_id'),
                        JobChunk.c.database.label('database'),
                        JobChunk.c.status.label('status')
                    ],
                    use_labels=True
                )

                query = (select_statement
                         .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                         .where(Job.c.status == 'started')
                         .order_by(Job.c.submitted))  # noqa

                # if there are started jobs and job_chunks, pick one from the earliest submitted job
                async for row in connection.execute(query):  # select a job chunk to submit
                    return row.id, row.job_chunk_id, row.database

                # if there are no running job_chunks, return None
                return None, None, None
            except Exception as e:
                raise SQLError("Failed to find highest priority job chunks") from e

    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def get_consumer_ip_from_job_chunk(engine, job_chunk_id):
    try:
        async with engine.acquire() as connection:
            try:
                query = (sa.select([JobChunk.c.consumer])
                         .select_from(JobChunk)
                         .where(JobChunk.c.id == job_chunk_id)
                         .apply_labels())
                async for row in connection.execute(query):
                    return row[0]
            except Exception as e:
                raise SQLError("Failed to get consumer ip from job_chunk, job_chunk_id = %s" % job_chunk_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def set_job_chunk_status(engine, job_id, database, status):
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''
                    UPDATE job_chunks
                    SET status = :status
                    WHERE job_id=:job_id AND database=:database
                    RETURNING *;
                ''')

                id = None  # if connection didn't return any rows, return None
                async for row in connection.execute(query, job_id=job_id, database=database, status=status):
                    id = row.id

                return id

                # if this doesn't work, here is an alternative implementation of SQL:
                #
                # await connection.execute('''
                #     UPDATE {job_chunks}
                #     SET status = 'status'
                #     WHERE job_id={job_id} AND database='{database}'
                #     RETURNING *;
                #     '''.format(job_chunks='job_chunks', job_id=job_id, database=database, status=status)
                # )
            except Exception as e:
                raise SQLError("Failed to set_job_chunk_status in the database,"
                               " job_id = %s, database = %s" % (job_id, database)) from e
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
                async for row in connection.execute(query, job_id=job_id, database=database, consumer_ip=consumer_ip):
                    id = row.id

                return id
            except Exception as e:
                raise SQLError("Failed to set_job_chunk_status in the database,"
                               " job_id = %s, database = %s" % (job_id, database)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                      "set_job_chunk_status, job_id = %s, database = %s" % (job_id, database)) from e

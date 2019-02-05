import logging
import datetime

import sqlalchemy as sa
import psycopg2

from ..models import Job, JobChunk


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
                logging.error("Failed to save job_chunk for job_id = %s, database = %s", (job_id, database))
    except psycopg2.Error as e:
        logging.error("Failed to open database connection in save_job_chunk for job_id = %s, database = %s" % (job_id, database))
        return


async def find_highest_priority_job_chunk(engine):
    """
    Find the next job chunk to give consumers for processing.

    Returns: (job_id, job_chunk_id, database)
    """
    # among the running jobs, find the one, submitted first
    try:
        async with engine.acquire() as connection:
            try:
                query = (sa.select([Job.c.id, Job.c.status, Job.c.submitted, JobChunk.c.job_id, JobChunk.c.id, JobChunk.c.database, JobChunk.c.status])
                         .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                         .where(Job.c.status == 'started')
                         .order_by(Job.c.submitted)
                         .apply_labels())  # noqa

                # if there are started jobs and job_chunks, pick one from the earliest submitted job
                async for row in connection.execute(query):  # select a job chunk to submit
                    return row[0], row[4], row[5]

                # if there are no running job_chunks, return None
                return None
            except Exception as e:
                logging.error("Failed to find highest priority job chunks")

    except psycopg2.Error as e:
        logging.error(str(e))
        return


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
                logging.error("Failed to get consumer ip from job_chunk, job_chunk_id = %s" % job_chunk_id)
    except psycopg2.Error as e:
        logging.error(str(e))
        return


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

                result = await connection.execute(
                    query,
                    job_id=job_id,
                    database=database,
                    status=status
                )

                async for row in connection.execute(query, job_id=job_id, database=database, status=status):
                    return row.id

                # if connection didn't return any rows, return None
                return None

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
                logging.error("Failed to set_job_chunk_status in the database, job_id = %s, database = %s" % (job_id, database))
    except psycopg2.Error as e:
        logging.error("Failed to open connection to the database in "
                      "set_job_chunk_status, job_id = %s, database = %s" % (job_id, database))

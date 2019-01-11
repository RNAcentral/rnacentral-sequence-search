import sqlalchemy as sa
import aiohttp
from aiohttp import web
import logging
import json

from .models import Job, JobChunk, JobChunkResult
from .settings import CONSUMER_SUBMIT_JOB_URL


async def find_available_consumers(engine):
    """
    Returns a list of available consumers that can be used to run.
    :param engine:
    :return:
    """
    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                SELECT ip, status
                FROM consumer
                WHERE status == 'available'
            ''')
            result = await connection.execute(query)

        for row in result:
            print(row)

        return []

    except Exception as e:
        logging.error(str(e))
        return


async def free_consumer(engine, consumer_ip):
    """When a consumer returns result, set its state in the database to 'available'."""
    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                UPDATE consumer
                SET status = 'available'
                WHERE ip=:consumer_ip
                RETURNING consumer.*;
            ''')
            result = await connection.execute(query, consumer_ip=consumer_ip)

        for row in result:
            print(row)

    except Exception as e:
        logging.error(str(e))


async def find_highest_priority_job_chunk(engine):
    """Find the next job chunk to give consumers for processing."""
    # among the running jobs, find the one, submitted first
    try:
        async with engine.acquire() as connection:
            query = (sa.select([Job.c.id, Job.c.status, Job.c.submitted, JobChunk.c.job_id, JobChunk.c.id, JobChunk.c.database, JobChunk.c.status])
                     .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                     .where(Job.c.status == 'started')
                     .order_by(Job.c.submitted)
                     .apply_labels())  # noqa

            # if there are started jobs and job_chunks, pick one from the earliest submitted job
            async for row in connection.execute(query):  # select a job chunk to submit
                return row[4]

            # if there are no running job_chunks, return None
            return None

    except Exception as e:
        logging.error(str(e))
        return


async def save_job_chunk_started(engine, job_id, database, consumer_ip):
    """
    When a job was successfully submitted to consumer,
    save the job status and consumer status to the database.
    """
    try:
        async with engine.acquire() as connection:
            try:
                await connection.execute('''
                    UPDATE 'consumer'
                    SET status = 'busy'
                    WHERE id={consumer_id}
                    '''.format(consumer_ip))
            except Exception as e:
                logging.error("Failed to set the consumer status to 'busy'")

            try:
                await connection.execute('''
                    UPDATE {job_chunks}
                    SET status = 'started'
                    WHERE job_id={job_id} AND database='{database}';
                    '''.format(job_chunks='job_chunks', job_id=job_id, database=database)
                )
            except Exception as e:
                logging.error("Failed to save successfully submitted job_chunks to the database, job_id = %s" % job_id)
    except Exception as e:
        logging.error("Failed to open connection to the database in save_job_chunk_started, job_id = %s" % job_id)


async def save_job_chunk_error(engine, job_id, database, reason):
    """When a job_chunk fails, record error to the database and free the consumer."""
    try:
        async with engine.acquire() as connection:
            # set status of job_chunk and whole job to error
            job_chunks = await connection.execute(
                '''
                UPDATE {job_chunks}
                SET status = 'error'
                WHERE job_id={job_id} AND database='{database}'
                RETURNING *;
                '''.format(job_chunks='job_chunks', job_id=job_id, database=database)
            )
    except Exception as e:
        logging.error("Failed to save job_chunks to the database about a failed job with job_id = %s, reason = %s" % (job_id, reason))

    try:
        query = sa.text('''UPDATE jobs SET status = 'error' WHERE id=:job_id''')
        await connection.execute(query, job_id=job_id)
    except Exception as e:
        logging.error("Failed to save job to the database about failed job, job_id = %s, reason = %s" % (job_id, reason))

    for row in job_chunks:
        free_consumer(engine, row.consumer_ip)


async def delegate_job_to_consumer(engine, consumer_ip, job_id, job_chunk_id, database, query):
    """When a consumer returns result, set its state in the database to 'available'."""
    # if job chunks available, use the same consumer to run them
    if job_chunk_id:
        try:
            async with engine.acquire() as connection:
                url = "http://" + consumer_ip + '/' + CONSUMER_SUBMIT_JOB_URL
                json_data = json.dumps({"job_id": job_id, "sequence": query, "database": database})
                headers = {'content-type': 'application/json'}

                async with aiohttp.ClientSession() as session:
                    logging.debug("Queuing JobChunk to consumer: url = {}, json_data = {}, headers = {}"
                                  .format(url, json_data, headers))

                    # What if we run into a race condition? How to lock?
                    async with session.post(url, data=json_data, headers=headers) as response:
                        if response.status < 400:
                            await save_job_chunk_started(engine, job_id, database, consumer_ip)
                        else:  # TODO: attempt retry upon a failed delivery?
                            await save_job_chunk_error(engine, job_id, database, reason="error response status")

                            # log and report error
                            text = await response.text()
                            logging.error("%s" % text)

                            raise web.HTTPBadRequest(text=text)
        except Exception as e:
            logging.error(str(e))

            async with engine.acquire() as connection:
                await save_job_chunk_error(connection, job_id, database, reason="failed to connect")

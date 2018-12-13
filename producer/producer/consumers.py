import sqlalchemy as sa
import aiohttp
from aiohttp import web
import logging
import json

from .models import Job, JobChunk, JobChunkResult
from .settings import CONSUMER_SUBMIT_JOB_URL


async def free_consumer(engine, consumer_ip):
    """When a consumer returns result, set its state in the database to 'available'."""
    try:
        async with engine.acquire() as connection:
            query = sa.text('''
                UPDATE consumer
                SET status = 'available'
                WHERE ip=:consumer_ip
            ''')
            result = connection.execute(query, consumer_ip=consumer_ip)

    except Exception as e:
        logging.error(str(e))


async def find_highest_priority_job_chunk(engine):
    """Find the next job chunk to give consumers for processing."""
    # among the running jobs, find the one, submitted first
    try:
        async with engine.acquire() as connection:
            query = (sa.select([Job.c.id, Job.c.status, Job.c.submitted, JobChunk.c.job_id, JobChunk.c.database, JobChunk.c.status])
                     .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                     .where(Job.c.status == 'started')
                     .order_by(Job.c.submitted)
                     .apply_labels())  # noqa
            result = connection.execute(query)

            for row in result:  # select a job chunk to submit
                return row.job_chunk.id
            return

    except Exception as e:
        logging.error(str(e))
        return


async def except_error_in_job_chunk(engine, job_id, database, reason):
    """When a job_chunk fails, record error to the database and free the consumer."""
    try:
        async with engine.acquire() as connection:
            # set status of job_chunk and whole job to error
            await connection.execute(
                '''
                UPDATE {job_chunks}
                SET status = 'error'
                WHERE job_id={job_id} AND database='{database}';
                '''.format(job_chunks='job_chunks', job_id=job_id, database=database)
            )
    except Exception as e:
        logging.error("Failed to save job_chunks to the database about a failed job with job_id = %s, reason = %s" % (job_id, reason))

    try:
        query = sa.text('''UPDATE jobs SET status = 'error' WHERE id=:job_id''')
        await connection.execute(query, job_id=job_id)
    except Exception as e:
        logging.error("Failed to save job to the database about failed job, job_id = %s, reason = %s" % (job_id, reason))

    free_consumer(engine, consumer_ip)


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
                                    '''.format(job_chunks='job_chunks', job_id=job_id, database=database))

                            except Exception as e:
                                logging.error("Failed to save successfully submitted job_chunks to the database, job_id = %s" % job_id)
                        else:
                            # TODO: attempt retry upon a failed delivery?
                            await except_error_in_job_chunk(connection, job_id, database, reason="error response status")

                            # log and report error
                            text = await response.text()
                            logging.error("%s" % text)

                            raise web.HTTPBadRequest(text=text)
        except Exception as e:
            logging.error(str(e))

            async with engine.acquire() as connection:
                await except_error_in_job_chunk(connection, job_id, database, reason="failed to connect")

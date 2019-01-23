import sqlalchemy as sa
import aiohttp
from aiohttp import web
import logging
import json

from ..db.job_chunks import set_job_chunk_status
from ..db.jobs import set_job_status
from ..settings import CONSUMER_SUBMIT_JOB_URL


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
                WHERE status='available'
            ''')
            result = await connection.execute(query)

        return result

    except Exception as e:
        logging.error(str(e))
        return


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

    except Exception as e:
        logging.error(str(e))


async def delegate_job_to_consumer(engine, consumer_ip, job_id, database, query):
    """When a consumer returns result, set its state in the database to 'available'."""
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
                        await set_consumer_status(engine, consumer_ip, 'busy')
                        await set_job_chunk_status(engine, job_id, database, consumer_ip, status="started")
                    else:  # TODO: attempt retry upon a failed delivery?
                        await set_job_chunk_status(engine, job_id, database, consumer_ip, status="error")
                        await set_job_status(engine, job_id, status="error")

                        # log and report error
                        text = await response.text()
                        logging.error("%s" % text)

                        raise web.HTTPBadRequest(text=text)
    except Exception as e:
        logging.error(str(e))

        async with engine.acquire() as connection:
            await set_job_chunk_status(engine, job_id, database, consumer_ip, status="error")

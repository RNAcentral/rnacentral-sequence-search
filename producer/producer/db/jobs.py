import logging

import sqlalchemy as sa

from ..models import Job, JobChunk


async def set_job_status(engine, job_id, reason):
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''UPDATE jobs SET status = 'error' WHERE id=:job_id''')
                await connection.execute(query, job_id=job_id)
            except Exception as e:
                logging.error("Failed to save job to the database about failed job, job_id = %s, reason = %s" % (job_id, reason))
    except Exception as e:
        logging.error("Failed to open connection to the database in save_job_status() for job with job_id = %s" % job_id)


async def check_job_chunks_status(engine, job_id):
    try:
        async with engine.acquire() as connection:
            # check, if all other job chunks are also done - then the whole job is done
            query = (sa.select([Job.c.id, JobChunk.c.job_id, JobChunk.c.status])
                     .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                     .where(Job.c.id == job_id))  # noqa

            all_job_chunks_success = True
            async for row in connection.execute(query):
                if row.status != 'success':
                    all_job_chunks_success = False
                    break

            return
    except Exception as e:
        logging.error("Failed to open connection to the database in check_job_chunks_status() for job with job_id = %s" % job_id)

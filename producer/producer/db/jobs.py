import logging

import sqlalchemy as sa


async def set_job_status(engine, job_id, reason):
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''UPDATE jobs SET status = 'error' WHERE id=:job_id''')
                await connection.execute(query, job_id=job_id)
            except Exception as e:
                logging.error("Failed to save job to the database about failed job, job_id = %s, reason = %s" % (job_id, reason))
    except Exception as e:
        logging.error("Failed to open connection to the database in save_job_status to the database for job with job_id = %s" % job_id)
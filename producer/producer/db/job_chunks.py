import logging

import sqlalchemy as sa

from ..models import Job, JobChunk


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


async def set_job_chunk_status(engine, job_id, database, status):
    try:
        async with engine.acquire() as connection:
            try:
                # await connection.execute('''
                #     UPDATE {job_chunks}
                #     SET status = 'status'
                #     WHERE job_id={job_id} AND database='{database}'
                #     RETURNING *;
                #     '''.format(job_chunks='job_chunks', job_id=job_id, database=database, status=status)
                # )
                query = sa.text('''
                    UPDATE job_chunks
                    SET status = ':status'
                    WHERE job_id=:job_id AND database=':database'
                    RETURNING *;
                ''')
                result = await connection.execute(
                    query,
                    job_id=job_id,
                    database=database,
                    status=status
                )
                return result
            except Exception as e:
                logging.error("Failed to update_job_chunk_status in the database, job_id = %s, database = %s" % (job_id, database))
    except Exception as e:
        logging.error("Failed to open connection to the database in "
                      "update_job_chunk_status, job_id = %s, database = %s" % (job_id, database))

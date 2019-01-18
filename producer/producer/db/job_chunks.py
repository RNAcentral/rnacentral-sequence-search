import logging

import sqlalchemy as sa

from ..models import Job, JobChunk, JobChunkResult


async def find_highest_priority_job_chunk(engine):
    """
    Find the next job chunk to give consumers for processing.

    Returns: (job_id, job_chunk_id, database)
    """
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
                return row[0], row[4], row[5]

            # if there are no running job_chunks, return None
            return None

    except Exception as e:
        logging.error(str(e))
        return


async def get_consumer_ip_from_job_chunk(engine, job_chunk_id):
    try:
        async with engine.acquire() as connection:
            query = (sa.select([JobChunk.c.consumer])
                     .select_from(JobChunk)
                     .where(JobChunk.c.id)
                     .apply_labels())
            async for row in connection.execute(query):
                return row[0]
    except Exception as e:
        logging.error(str(e))
        return


async def set_job_chunk_status(engine, job_id, database, status):
    try:
        async with engine.acquire() as connection:
            try:
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

                return result[0].id if len(result) else None

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
    except Exception as e:
        logging.error("Failed to open connection to the database in "
                      "set_job_chunk_status, job_id = %s, database = %s" % (job_id, database))


async def set_job_chunk_results(engine, job_id, database, results):
    try:
        async with engine.acquire() as connection:
            try:
                async for row in await connection.execute('''
                    SELECT job_chunk_id 
                    FROM :job_chunks 
                    WHERE job_id=:job_id AND database=':database'
                    RETURNING *
                ''', job_chunks='job_chunks', job_id=job_id, database=database):
                    job_chunk_id = row.job_chunk_id
                    break

                for result in results:
                    await connection.scalar(JobChunkResult.insert().values(job_chunk_id=job_chunk_id, **result))
            except Exception as e:
                logging.error("Failed to udpate")
    except Exception as e:
        logging.error("")

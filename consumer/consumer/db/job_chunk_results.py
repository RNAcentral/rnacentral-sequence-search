import logging

import sqlalchemy as sa
import psycopg2

from ..models import JobChunkResult


async def set_job_chunk_results(engine, job_id, database, results):
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''
                    SELECT id
                    FROM job_chunks
                    WHERE job_id=:job_id AND database=:database
                ''')
                async for row in await connection.execute(query, job_id=job_id, database=database):
                    job_chunk_id = row.id
                    break

                for result in results:
                    await connection.scalar(JobChunkResult.insert().values(job_chunk_id=job_chunk_id, **result))
            except Exception as e:
                logging.error("Failed to set_job_chunk_results in the database, job_id = %s, database = %s" % (job_id, database))
    except psycopg2.Error as e:
        logging.error("Failed to open connection to the database in "
                      "set_job_chunk_results, job_id = %s, database = %s" % (job_id, database))

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
import uuid

import sqlalchemy as sa
import psycopg2

from . import DatabaseConnectionError, SQLError
from .models import Job, JobChunk, JobChunkResult, JOB_STATUS_CHOICES


class JobNotFound(Exception):
    def __init__(self, job_id):
        self.job_id = job_id

    def __str__(self):
        return "Job '%s' not found" % self.job_id


async def save_job(engine, query):
    try:
        async with engine.acquire() as connection:
            try:
                job_id = str(uuid.uuid4())

                await connection.execute(
                    Job.insert().values(
                        id=job_id,
                        query=query,
                        submitted=datetime.datetime.now(),
                        status=JOB_STATUS_CHOICES.started
                    )
                )

                return job_id
            except Exception as e:
                raise SQLError("Failed to save job for query = %s to the database" % query) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                                "save_job() for job with job_id = %s" % job_id) from e


async def set_job_status(engine, job_id, status):
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''UPDATE jobs SET status =:status WHERE id=:job_id''')
                await connection.execute(query, job_id=job_id, status=status)
            except Exception as e:
                raise SQLError("Failed to save job to the database about failed job, "
                                              "job_id = %s, status = %s" % (job_id, status)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in set_job_status() "
                                      "for job with job_id = %s" % job_id) from e


async def get_job_chunks_status(engine, job_id):
    """Returns the status of the job and its job_chunks as a namedtuple"""
    try:
        async with engine.acquire() as connection:
            try:
                # ambiguity in column names forces us to manually assign column labels
                select_statement = sa.select(
                    [
                        Job.c.id.label('id'),
                        Job.c.status.label('job_status'),
                        JobChunk.c.job_id.label('job_id'),
                        JobChunk.c.database.label('database'),
                        JobChunk.c.status.label('status')
                    ],
                    use_labels=True
                )

                query = (select_statement
                         .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                         .where(Job.c.id == job_id))  # noqa

                output = []
                async for row in connection.execute(query):
                    output.append({
                        'job_id': row.job_id,
                        'job_status': row.job_status,
                        'database': row.database,
                        'status': row.status
                    })

                if output == []:
                    raise JobNotFound(job_id)
                else:
                    return output

            except JobNotFound as e:
                raise e
            except Exception as e:
                raise SQLError("Failed to get job_chunk status, job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def check_job_chunks_status(engine, job_id):
    try:
        async with engine.acquire() as connection:
            try:
                # check, if all other job chunks are also done - then the whole job is done
                query = (sa.select([Job.c.id, JobChunk.c.job_id, JobChunk.c.status])
                         .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                         .where(Job.c.id == job_id))  # noqa

                all_job_chunks_success = True
                async for row in connection.execute(query):
                    if row.status != 'success':
                        all_job_chunks_success = False
                        break

                return all_job_chunks_success

            except Exception as e:
                raise SQLError("Failed to check job_chunk status, job_id = %s" % job_id) from e

    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                                      "check_job_chunks_status() for job with job_id = %s" % job_id) from e


async def job_exists(engine, job_id):
    try:
        async with engine.acquire() as connection:
            try:
                exists = False
                async for row in connection.execute(sa.text('''SELECT * FROM jobs WHERE id=:job_id'''), job_id=job_id):
                    exists = True
                    break
                return exists

            except Exception as e:
                raise SQLError("Failed to check if job exists for job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                                      "job_exists() for job with job_id = %s" % job_id) from e


async def get_job_query(engine, job_id):
    try:
        async with engine.acquire() as connection:
            try:
                sql_query = sa.select([Job.c.query]).select_from(Job).where(Job.c.id == job_id)

                async for row in connection.execute(sql_query):
                    return row.query
            except Exception as e:
                raise SQLError("Failed to get job query, job_id = %s" % job_id) from e

    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                                      "get_job_query() for job with job_id = %s" % job_id) from e


async def get_job_results(engine, job_id):
    try:
        async with engine.acquire() as connection:
            sql = (sa.select([
                    JobChunk.c.job_id,
                    JobChunk.c.database,
                    JobChunkResult.c.rnacentral_id,
                    JobChunkResult.c.description,
                    JobChunkResult.c.score,
                    JobChunkResult.c.bias,
                    JobChunkResult.c.e_value,
                    JobChunkResult.c.target_length,
                    JobChunkResult.c.alignment,
                    JobChunkResult.c.alignment_length,
                    JobChunkResult.c.gap_count,
                    JobChunkResult.c.match_count,
                    JobChunkResult.c.nts_count1,
                    JobChunkResult.c.nts_count2,
                    JobChunkResult.c.identity,
                    JobChunkResult.c.query_coverage,
                    JobChunkResult.c.target_coverage,
                    JobChunkResult.c.gaps,
                    JobChunkResult.c.query_length,
                    JobChunkResult.c.result_id
                ])
                .select_from(sa.join(JobChunk, JobChunkResult, JobChunk.c.id == JobChunkResult.c.job_chunk_id))  # noqa
                .where(JobChunk.c.job_id == job_id))  # noqa

            results = []
            async for row in connection.execute(sql):
                results.append({
                    'rnacentral_id': row[2],
                    'description': row[3],
                    'score': row[4],
                    'bias': row[5],
                    'e_value': row[6],
                    'target_length': row[7],
                    'alignment': row[8],
                    'alignment_length': row[9],
                    'gap_count': row[10],
                    'match_count': row[11],
                    'nts_count1': row[12],
                    'nts_count2': row[13],
                    'identity': row[14],
                    'query_coverage': row[15],
                    'target_coverage': row[16],
                    'gaps': row[17],
                    'query_length': row[18],
                    'result_id': row[19]
                })

            # sort results by e_value
            results.sort(key=lambda result: result['e_value'])

            return results

    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e

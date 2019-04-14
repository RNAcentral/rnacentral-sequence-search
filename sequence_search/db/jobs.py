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
from .models import Job, JobChunk, JobChunkResult, JOB_STATUS_CHOICES, JOB_CHUNK_STATUS_CHOICES


class JobNotFound(Exception):
    def __init__(self, job_id):
        self.job_id = job_id

    def __str__(self):
        return "Job '%s' not found" % self.job_id


async def save_job(engine, query, description):
    try:
        async with engine.acquire() as connection:
            try:
                job_id = str(uuid.uuid4())

                await connection.execute(
                    Job.insert().values(
                        id=job_id,
                        query=query,
                        description=description,
                        ordering='e_value',
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
    if status == JOB_CHUNK_STATUS_CHOICES.success or \
       status == JOB_CHUNK_STATUS_CHOICES.error or \
       status == JOB_CHUNK_STATUS_CHOICES.timeout:
        finished = datetime.datetime.now()
    else:
        finished = None

    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''UPDATE jobs SET status = :status, finished = :finished WHERE id = :job_id''')
                await connection.execute(query, job_id=job_id, status=status, finished=finished)
            except Exception as e:
                raise SQLError("Failed to save job to the database about failed job, "
                                              "job_id = %s, status = %s" % (job_id, status)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in set_job_status() "
                                      "for job with job_id = %s" % job_id) from e


async def get_jobs_statuses(engine):
    """Returns the dict of jobs with statuses of their job_chunks"""
    try:
        async with engine.acquire() as connection:
            try:
                # ambiguity in column names forces us to manually assign column labels
                query = (sa.select([
                    Job.c.id.label('id'),
                    Job.c.status.label('job_status'),
                    Job.c.submitted.label('submitted'),
                    JobChunk.c.job_id.label('job_id'),
                    JobChunk.c.database.label('database'),
                    JobChunk.c.status.label('status'),
                    JobChunk.c.consumer.label('consumer')
                ], use_labels=True).select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id)))  # noqa

                jobs_dict = {}
                async for row in connection.execute(query):
                    if row.job_id not in jobs_dict:
                       jobs_dict[row.job_id] = {
                           'id': row.job_id,
                           'status': row.job_status,
                           'submitted': str(row.submitted),
                           'chunks': [
                               {
                                   'database': row.database,
                                   'status': row.status,
                                   'consumer': row.consumer
                               }
                           ]
                       }
                    else:
                        jobs_dict[row.job_id]['chunks'].append({
                            'database': row.database,
                            'status': row.status,
                            'consumer': row.consumer
                        })

                jobs = list(jobs_dict.values())
                jobs.sort(key=lambda job: job['submitted'])
                jobs.reverse()
                return jobs

            except Exception as e:
                raise SQLError("Failed to get jobs_statuses") from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def get_job_chunks_status(engine, job_id):
    """Returns the status of the job and its job_chunks as a namedtuple"""
    try:
        async with engine.acquire() as connection:
            try:
                # ambiguity in column names forces us to manually assign column labels
                select_statement = sa.select(
                    [
                        Job.c.id.label('id'),
                        Job.c.query.label('query'),
                        Job.c.description.label('description'),
                        Job.c.status.label('job_status'),
                        Job.c.submitted.label('job_submitted'),
                        Job.c.finished.label('job_finished'),
                        JobChunk.c.job_id.label('job_id'),
                        JobChunk.c.database.label('database'),
                        JobChunk.c.status.label('status'),
                        JobChunk.c.submitted.label('submitted'),
                        JobChunk.c.finished.label('finished')
                    ],
                    use_labels=True
                )

                query = (select_statement
                         .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                         .where(Job.c.id == job_id)
                         .order_by(JobChunk.c.database))  # noqa

                output = []
                async for row in connection.execute(query):
                    output.append({
                        'job_id': row.job_id,
                        'query': row.query,
                        'description': row.description,
                        'job_status': row.job_status,
                        'job_submitted': row.job_submitted,
                        'job_finished': row.job_finished,
                        'database': row.database,
                        'status': row.status,
                        'submitted': row.submitted,
                        'finished': row.finished
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


async def update_job_status_from_job_chunks_status(engine, job_id):
    """Infer job status for the statuses of all chunks that constitute it"""
    try:
        async with engine.acquire() as connection:
            try:
                query = (sa.select([Job.c.id, JobChunk.c.job_id, JobChunk.c.status])
                         .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                         .where(Job.c.id == job_id))  # noqa

                unfinished_chunks_found = False
                errors_found = False
                async for row in connection.execute(query):
                    if row.status == JOB_CHUNK_STATUS_CHOICES.pending or row.status == JOB_CHUNK_STATUS_CHOICES.started:
                        unfinished_chunks_found = True
                        break
                    elif row.status == JOB_CHUNK_STATUS_CHOICES.error or row.status == JOB_CHUNK_STATUS_CHOICES.timeout:
                        errors_found = True

                if unfinished_chunks_found is False and errors_found is False:
                    await set_job_status(engine, job_id, status=JOB_STATUS_CHOICES.success)
                elif unfinished_chunks_found is False and errors_found is True:
                    await set_job_status(engine, job_id, status=JOB_STATUS_CHOICES.partial_success)

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


async def get_job_ordering(engine, job_id):
    try:
        async with engine.acquire() as connection:
            try:
                sql_query = sa.select([Job.c.ordering]).select_from(Job).where(Job.c.id == job_id)

                async for row in connection.execute(sql_query):
                    return row.ordering
            except Exception as e:
                raise SQLError("Failed to get job ordering, job_id = %s" % job_id) from e

    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                                      "get_job_ordering() for job with job_id = %s" % job_id) from e


async def set_job_ordering(engine, job_id, ordering):
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''UPDATE jobs SET ordering=:ordering WHERE id = :job_id''')
                await connection.execute(query, job_id=job_id, ordering=ordering)
            except Exception as e:
                raise SQLError("Failed to set job ordering, job_id = %s" % job_id) from e

    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                                      "set_job_ordering() for job with job_id = %s" % job_id) from e


async def get_job_results(engine, job_id, limit=10000):
    """
    Aggregates results from multiple job_chunks and returns them.

    By default, we're using a limit of 10000 on the number of hits due to
    recommendation from text search team. You can increase it up to infinity,
    shall the need arise.
    """
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
                .limit(limit)
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

            # sort results by ordering, ordering is stored in the database
            ordering = await get_job_ordering(engine, job_id)

            if ordering == 'e_value':
                results.sort(key=lambda result: result['e_value'])
            elif ordering == '-e_value':
                results.sort(key=lambda result: result['e_value'])
                results.reverse()
            elif ordering == 'identity':
                results.sort(key=lambda result: result['identity'])
            elif ordering == '-identity':
                results.sort(key=lambda result: result['identity'])
                results.reverse()
            elif ordering == 'query_coverage':
                results.sort(key=lambda result: result['query_coverage'])
            elif ordering == '-query_coverage':
                results.sort(key=lambda result: result['query_coverage'])
                results.reverse()
            elif ordering == 'target_coverage':
                results.sort(key=lambda result: result['target_coverage'])
            elif ordering == '-target_coverage':
                results.sort(key=lambda result: result['target_coverage'])
                results.reverse()

            return results

    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e

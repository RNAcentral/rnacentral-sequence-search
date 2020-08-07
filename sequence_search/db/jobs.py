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
from collections import Counter
from operator import itemgetter

from . import DatabaseConnectionError, SQLError
from .models import Job, InfernalJob, InfernalResult, JobChunk, JobChunkResult, JOB_STATUS_CHOICES, \
    JOB_CHUNK_STATUS_CHOICES


class JobNotFound(Exception):
    def __init__(self, job_id):
        self.job_id = job_id

    def __str__(self):
        return "Job '%s' not found" % self.job_id


async def sequence_exists(engine, query):
    """
    Check if this query has already been searched
    :param engine: params to connect to the db
    :param query: the sequence that the user wants to search
    :return: list of job_ids
    """
    try:
        async with engine.acquire() as connection:
            try:
                sql_query = sa.select([Job.c.id]).select_from(Job).where(
                    (Job.c.query == query) & Job.c.result_in_db
                )
                job_list = []
                async for row in connection.execute(sql_query):
                    job_list.append(row[0])
                return job_list
            except Exception as e:
                raise SQLError("Failed to check if query exists for query = %s" % query) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in sequence_exists() for "
                                      "sequence with query = %s" % query) from e


async def database_used_in_search(engine, job_id, databases):
    """
    Check the database used. If the database used in "job_id" is the same as in "databases",
    we don't want to search again.
    :param engine: params to connect to the db
    :param job_id: id of the job
    :param databases: database that the user wants to use to perform the search
    :return: "true" if the database used in "job_id" is the same as in "databases", otherwise "false".
    """
    try:
        async with engine.acquire() as connection:
            try:
                sql_query = sa.select([JobChunk.c.database]).select_from(JobChunk).where(JobChunk.c.job_id == job_id)
                result = []
                async for row in connection.execute(sql_query):
                    result.append(row[0])
                return True if Counter(result) == Counter(databases) else False
            except Exception as e:
                raise SQLError("Failed to check the database used for job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in database_used_in_search() for "
                                      "job_id = %s" % job_id) from e


async def get_job(engine, job_id):
    try:
        async with engine.acquire() as connection:
            try:
                sql_query = sa.select([
                    Job.c.id,
                    Job.c.query,
                    Job.c.description,
                    Job.c.ordering,
                    Job.c.submitted,
                    Job.c.finished,
                    Job.c.hits,
                    Job.c.status
                ]).select_from(Job).where(Job.c.id == job_id)
                async for row in connection.execute(sql_query):
                    return {
                        'id': row.id,
                        'query': row.query,
                        'description': row.description,
                        'ordering': row.ordering,
                        'submitted': row.submitted,
                        'finished': row.finished,
                        'hits': row.hits,
                        'status': row.status
                    }
            except Exception as e:
                raise SQLError("Failed to get job for job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in "
                                      "get_job() for job with job_id = %s" % job_id) from e


async def save_job(engine, query, description, url, priority):
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
                        status=JOB_STATUS_CHOICES.started,
                        url=url,
                        priority=priority
                    )
                )

                return job_id
            except Exception as e:
                raise SQLError("Failed to save job for query = %s, "
                               "description = %s to the database" % (query, description)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in save_job() for job with "
                                      "job_id = %s" % job_id) from e


async def set_job_status(engine, job_id, status, hits=None):
    if status == JOB_CHUNK_STATUS_CHOICES.success or \
       status == JOB_CHUNK_STATUS_CHOICES.error or \
       status == JOB_CHUNK_STATUS_CHOICES.timeout:
        finished = datetime.datetime.now()
    else:
        finished = None

    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''UPDATE jobs SET status = :status, finished = :finished, hits = :hits, 
                result_in_db = :result_in_db WHERE id = :job_id''')
                await connection.execute(query, job_id=job_id, status=status, finished=finished, hits=hits,
                                         result_in_db=True)
            except Exception as e:
                raise SQLError("Failed to save job to the database about failed job, job_id = %s, "
                               "status = %s" % (job_id, status)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in set_job_status() "
                                      "for job with job_id = %s" % job_id) from e


async def get_jobs_statuses(engine):
    """Returns all jobs from the last 15 days with job_chunks status"""
    try:
        async with engine.acquire() as connection:
            try:
                # ambiguity in column names forces us to manually assign column labels
                select_statement = sa.select([
                    Job.c.id.label('id'),
                    Job.c.query.label('query'),
                    Job.c.status.label('job_status'),
                    Job.c.submitted.label('submitted'),
                    JobChunk.c.job_id.label('job_id'),
                    JobChunk.c.database.label('database'),
                    JobChunk.c.status.label('status'),
                    JobChunk.c.consumer.label('consumer')
                ], use_labels=True)

                query = (
                    select_statement.select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))
                    .where(Job.c.submitted > datetime.datetime.now() - datetime.timedelta(days=15))  # noqa
                )

                jobs_dict = {}
                async for row in connection.execute(query):
                    if row.job_id not in jobs_dict:
                        jobs_dict[row.job_id] = {
                            'id': row.job_id,
                            'query': row.query,
                            'status': row.job_status,
                            'submitted': str(row.submitted),
                            'chunks': [
                                {'database': row.database, 'status': row.status, 'consumer': row.consumer}
                            ]
                        }
                    else:
                        jobs_dict[row.job_id]['chunks'].append({
                            'database': row.database,
                            'status': row.status,
                            'consumer': row.consumer
                        })

                jobs = list(jobs_dict.values())
                jobs.sort(key=itemgetter('submitted'), reverse=True)
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
                        Job.c.r2dt_id.label('r2dt_id'),
                        Job.c.r2dt_date.label('r2dt_date'),
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
                        'r2dt_id': row.r2dt_id,
                        'r2dt_date': row.r2dt_date,
                        'database': row.database,
                        'status': row.status,
                        'submitted': row.submitted,
                        'finished': row.finished
                    })

                if output:
                    return output
                else:
                    raise JobNotFound(job_id)

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
                query = (sa.select([Job.c.id, JobChunk.c.job_id, JobChunk.c.status, JobChunk.c.hits])
                         .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                         .where(Job.c.id == job_id))  # noqa

                unfinished_chunks_found = False
                errors_found = False
                hits = 0
                async for row in connection.execute(query):
                    if row.status == JOB_CHUNK_STATUS_CHOICES.pending or row.status == JOB_CHUNK_STATUS_CHOICES.started:
                        unfinished_chunks_found = True
                        break
                    elif row.status == JOB_CHUNK_STATUS_CHOICES.error or row.status == JOB_CHUNK_STATUS_CHOICES.timeout:
                        errors_found = True
                    if row.hits:
                        hits += row.hits

                if unfinished_chunks_found is False and errors_found is False:
                    await set_job_status(engine, job_id, status=JOB_STATUS_CHOICES.success, hits=hits)
                elif unfinished_chunks_found is False and errors_found is True:
                    await set_job_status(engine, job_id, status=JOB_STATUS_CHOICES.partial_success, hits=hits)

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


async def get_job_results(engine, job_id, limit=1000):
    """
    Aggregates results from multiple job_chunks and returns them.

    By default, we're using a limit of 10000 on the number of hits due to
    recommendation from text search team. You can increase it up to infinity,
    shall the need arise.
    """
    try:
        async with engine.acquire() as connection:
            sql = (sa.select([
                    JobChunkResult.c.rnacentral_id.distinct(),
                    JobChunk.c.job_id,
                    JobChunk.c.database,
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
                .order_by(JobChunkResult.c.score.desc())
                .limit(limit)
                .where(JobChunk.c.job_id == job_id))  # noqa

            # popular species: zebrafish, arabidopsis thaliana, caenorhabditis elegans, drosophila melanogaster,
            # saccharomyces cerevisiae S288c, schizosaccharomyces pombe, escherichia coli str. K-12 substr. MG1655
            # and bacillus subtilis subsp. subtilis str. 168, respectively.
            popular_species = {7955, 3702, 6239, 7227, 559292, 4896, 511145, 224308}

            results = []
            async for row in connection.execute(sql):
                # check species priority.
                # priority order = human (9606), mouse (10090), popular species, others
                try:
                    taxid = row[0].split('_')[1]
                    if taxid == '9606':
                        species_priority = 'a'  # Very high priority
                    elif taxid == '10090':
                        species_priority = 'b'  # High priority
                    elif int(taxid) in popular_species:
                        species_priority = 'c'  # Medium priority
                    else:
                        species_priority = 'd'  # Low priority
                except Exception:
                    pass

                # add result
                results.append({
                    'rnacentral_id': row[0],
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
                    'result_id': row[19],
                    'species_priority': species_priority if species_priority else 'd'
                })

            # sort results by ordering, ordering is stored in the database
            ordering = await get_job_ordering(engine, job_id)

            if ordering == 'e_value':
                results.sort(key=itemgetter('e_value', 'species_priority'))
            elif ordering == '-e_value':
                results.sort(key=itemgetter('e_value'), reverse=True)
                results.sort(key=itemgetter('species_priority'))
            elif ordering == 'identity':
                results.sort(key=itemgetter('identity', 'species_priority'))
            elif ordering == '-identity':
                results.sort(key=itemgetter('identity'), reverse=True)
                results.sort(key=itemgetter('species_priority'))
            elif ordering == 'query_coverage':
                results.sort(key=itemgetter('query_coverage', 'species_priority'))
            elif ordering == '-query_coverage':
                results.sort(key=itemgetter('query_coverage'), reverse=True)
                results.sort(key=itemgetter('species_priority'))
            elif ordering == 'target_coverage':
                results.sort(key=itemgetter('target_coverage', 'species_priority'))
            elif ordering == '-target_coverage':
                results.sort(key=itemgetter('target_coverage'), reverse=True)
                results.sort(key=itemgetter('species_priority'))

            return results

    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def find_highest_priority_jobs(engine):
    """
    Find unfinished jobs to give consumers for processing.

    :param engine: params to connect to the db
    :return: sorted list of job chunks and infernal jobs
    """
    # among the running jobs, find the one with high priority, submitted first
    try:
        async with engine.acquire() as connection:
            try:
                output = []
                select_statement = sa.select(
                    [
                        Job.c.id.label('id'),
                        Job.c.status.label('job_status'),
                        Job.c.submitted.label('submitted'),
                        Job.c.priority.label('priority'),
                        JobChunk.c.job_id.label('job_id'),
                        JobChunk.c.id.label('job_chunk_id'),
                        JobChunk.c.database.label('database'),
                        JobChunk.c.status.label('status')
                    ],
                    use_labels=True
                )

                query = (select_statement
                         .select_from(sa.join(Job, JobChunk, Job.c.id == JobChunk.c.job_id))  # noqa
                         .where(sa.and_(Job.c.status == JOB_STATUS_CHOICES.started, JobChunk.c.status == JOB_CHUNK_STATUS_CHOICES.pending))
                         .order_by(Job.c.priority, Job.c.submitted))  # noqa

                # get job chunks
                async for row in connection.execute(query):
                    output.append((row.id, row.priority, row.submitted, row.database))

                query = (sa.select([InfernalJob.c.job_id, InfernalJob.c.submitted, InfernalJob.c.priority])
                         .select_from(InfernalJob)
                         .where(InfernalJob.c.status == JOB_CHUNK_STATUS_CHOICES.pending)
                         .order_by(InfernalJob.c.priority, InfernalJob.c.submitted)  # noqa
                         )

                # get infernal jobs
                async for row in connection.execute(query):
                    output.append((row.job_id, row.priority, row.submitted))

                return sorted(output, key=itemgetter(1, 2))  # sort by priority first, then by date

            except Exception as e:
                raise SQLError("Failed to find highest priority jobs") from e

    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def get_infernal_job_results(engine, job_id):
    """
    Function to get cmscan command results
    :param engine: params to connect to the db
    :param job_id: id of the job
    :return: list of dicts with cmscan command results
    """
    try:
        async with engine.acquire() as connection:
            sql = (sa.select([
                    InfernalJob.c.job_id,
                    InfernalResult.c.target_name,
                    InfernalResult.c.accession_rfam,
                    InfernalResult.c.query_name,
                    InfernalResult.c.accession_seq,
                    InfernalResult.c.mdl,
                    InfernalResult.c.mdl_from,
                    InfernalResult.c.mdl_to,
                    InfernalResult.c.seq_from,
                    InfernalResult.c.seq_to,
                    InfernalResult.c.strand,
                    InfernalResult.c.trunc,
                    InfernalResult.c.pipeline_pass,
                    InfernalResult.c.gc,
                    InfernalResult.c.bias,
                    InfernalResult.c.score,
                    InfernalResult.c.e_value,
                    InfernalResult.c.inc,
                    InfernalResult.c.description,
                    InfernalResult.c.alignment,
                ])
                .select_from(sa.join(InfernalJob, InfernalResult, InfernalJob.c.id == InfernalResult.c.infernal_job_id))  # noqa
                .where(InfernalJob.c.job_id == job_id))  # noqa

            results = []
            async for row in connection.execute(sql):
                results.append({
                    'target_name': row[1],
                    'accession_rfam': row[2],
                    'query_name': row[3],
                    'accession_seq': row[4],
                    'mdl': row[5],
                    'mdl_from': row[6],
                    'mdl_to': row[7],
                    'seq_from': row[8],
                    'seq_to': row[9],
                    'strand': row[10],
                    'trunc': row[11],
                    'pipeline_pass': row[12],
                    'gc': row[13],
                    'bias': row[14],
                    'score': row[15],
                    'e_value': row[16],
                    'inc': row[17],
                    'description': row[18],
                    'alignment': row[19]
                })

            return results

    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def get_infernal_job_status(engine, job_id):
    """
    Function to get the status of the infernal job
    :param engine: params to connect to the db
    :param job_id: id of the job
    :return: data about infernal job as a namedtuple
    """
    try:
        async with engine.acquire() as connection:
            try:
                select_statement = sa.select(
                    [
                        InfernalJob.c.job_id,
                        InfernalJob.c.submitted,
                        InfernalJob.c.finished,
                        InfernalJob.c.status,
                    ],
                )

                query = (select_statement.select_from(InfernalJob).where(InfernalJob.c.job_id == job_id))  # noqa

                result = False
                async for row in connection.execute(query):
                    result = ({
                        'job_id': row.job_id,
                        'submitted': row.submitted,
                        'finished': row.finished,
                        'status': row.status,
                    })

                if result:
                    return result
                else:
                    raise JobNotFound(job_id)

            except JobNotFound as e:
                raise e
            except Exception as e:
                raise SQLError("Failed to get infernal_job status, job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError(str(e)) from e


async def save_r2dt_id(engine, job_id, r2dt_id, r2dt_date):
    """
    Update the r2dt_id for a given search
    :param engine: params to connect to the db
    :param job_id: id of the job
    :param r2dt_id: id of the R2DT
    :param r2dt_date: date of the last update of r2dt_id
    :return: r2dt_id
    """
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''UPDATE jobs SET r2dt_id = :r2dt_id, r2dt_date = :r2dt_date WHERE id = :job_id''')
                await connection.execute(query, r2dt_id=r2dt_id, r2dt_date=r2dt_date, job_id=job_id)
                return r2dt_id
            except Exception as e:
                raise SQLError("Failed to save r2dt_id to the database for the job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in save_r2dt_id() "
                                      "for job with job_id = %s" % job_id) from e

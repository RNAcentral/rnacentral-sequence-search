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

import logging
import sqlalchemy as sa
from aiopg.sa import create_engine

from .settings import get_postgres_credentials


# Connection initialization code
# ------------------------------

async def init_pg(app):
    logger = logging.getLogger('aiohttp.web')
    logger.debug("POSTGRES_USER = %s" % app['settings'].POSTGRES_USER)
    logger.debug("POSTGRES_DATABASE = %s" % app['settings'].POSTGRES_DATABASE)
    logger.debug("POSTGRES_HOST = %s" % app['settings'].POSTGRES_HOST)
    logger.debug("POSTGRES_PASSWORD = %s" % app['settings'].POSTGRES_PASSWORD)

    app['engine'] = await create_engine(
        user=app['settings'].POSTGRES_USER,
        database=app['settings'].POSTGRES_DATABASE,
        host=app['settings'].POSTGRES_HOST,
        password=app['settings'].POSTGRES_PASSWORD
    )


# Graceful shutdown
# -----------------

async def close_pg(app):
    app['engine'].close()
    await app['engine'].wait_closed()


# Models schema
# -------------

class JOB_STATUS_CHOICES(object):
    pending = 'pending'
    started = 'started'
    error = 'error'
    success = 'success'
    partial_success = 'partial_success'  # some job chunks crashed for this job status


class JOB_CHUNK_STATUS_CHOICES(object):
    created = 'created'
    pending = 'pending'
    started = 'started'
    error = 'error'
    timeout = 'timeout'
    success = 'success'


class CONSUMER_STATUS_CHOICES(object):
    available = 'available'
    busy = 'busy'


metadata = sa.MetaData()

# TODO: consistent naming for tables: either 'jobs' and 'consumers' or 'job' and 'consumer'
"""State of a consumer instance"""
Consumer = sa.Table('consumer', metadata,
                    sa.Column('ip', sa.String(20), primary_key=True),
                    sa.Column('status', sa.String(255)),  # choices=CONSUMER_STATUS_CHOICES, default='available'
                    sa.Column('job_chunk_id', sa.ForeignKey('job_chunks.id')),
                    sa.Column('port', sa.String(10)))

"""A search job that is divided into multiple job chunks per database"""
Job = sa.Table('jobs', metadata,
               sa.Column('id', sa.String(36), primary_key=True),
               sa.Column('query', sa.Text),
               sa.Column('description', sa.Text, nullable=True),
               sa.Column('ordering', sa.Text, nullable=True),
               sa.Column('submitted', sa.DateTime),
               sa.Column('finished', sa.DateTime, nullable=True),
               sa.Column('result_in_db', sa.Boolean),
               sa.Column('hits', sa.Integer, nullable=True),
               sa.Column('status', sa.String(255)),  # choices=JOB_STATUS_CHOICES
               sa.Column('url', sa.String(255)))

"""Part of the search job, run against a specific database and assigned to a specific consumer"""
JobChunk = sa.Table('job_chunks', metadata,
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id')),
                    sa.Column('database', sa.String(255)),
                    sa.Column('submitted', sa.DateTime, nullable=True),
                    sa.Column('finished', sa.DateTime, nullable=True),
                    sa.Column('consumer', sa.ForeignKey('consumer.ip'), nullable=True),
                    sa.Column('hits', sa.Integer, nullable=True),
                    sa.Column('status', sa.String(255)))  # choices=JOB_CHUNK_STATUS_CHOICES, default='started'

"""Result of a specific JobChunk"""
JobChunkResult = sa.Table('job_chunk_results', metadata,
                          sa.Column('id', sa.Integer, primary_key=True),
                          sa.Column('job_chunk_id', None, sa.ForeignKey('job_chunks.id')),
                          sa.Column('rnacentral_id', sa.String(255)),
                          sa.Column('description', sa.Text, nullable=True),
                          sa.Column('score', sa.Float),
                          sa.Column('bias', sa.Float),
                          sa.Column('e_value', sa.Float),
                          sa.Column('target_length', sa.Integer),
                          sa.Column('alignment', sa.Text),
                          sa.Column('alignment_length', sa.Integer),
                          sa.Column('gap_count', sa.Integer),
                          sa.Column('match_count', sa.Integer),
                          sa.Column('nts_count1', sa.Integer),
                          sa.Column('nts_count2', sa.Integer),
                          sa.Column('identity', sa.Float),
                          sa.Column('query_coverage', sa.Float),
                          sa.Column('target_coverage', sa.Float),
                          sa.Column('gaps', sa.Float),
                          sa.Column('query_length', sa.Integer),
                          sa.Column('result_id', sa.Integer))

InfernalJob = sa.Table('infernal_job', metadata,
                       sa.Column('id', sa.Integer, primary_key=True),
                       sa.Column('job_id', sa.String(36), sa.ForeignKey('jobs.id')),
                       sa.Column('consumer', sa.ForeignKey('consumer.ip'), nullable=True),
                       sa.Column('submitted', sa.DateTime, nullable=True),
                       sa.Column('finished', sa.DateTime, nullable=True),
                       sa.Column('status', sa.String(255)))  # choices=JOB_CHUNK_STATUS_CHOICES

InfernalResult = sa.Table('infernal_result', metadata,
                          sa.Column('id', sa.Integer, primary_key=True),
                          sa.Column('infernal_job_id', None, sa.ForeignKey('infernal_job.id')),
                          sa.Column('target_name', sa.String(255)),
                          sa.Column('accession_rfam', sa.String(255)),
                          sa.Column('query_name', sa.String(255)),
                          sa.Column('accession_seq', sa.String(255)),
                          sa.Column('mdl', sa.String(255)),
                          sa.Column('mdl_from', sa.Integer),
                          sa.Column('mdl_to', sa.Integer),
                          sa.Column('seq_from', sa.Integer),
                          sa.Column('seq_to', sa.Integer),
                          sa.Column('strand', sa.String(255)),
                          sa.Column('trunc', sa.String(255)),
                          sa.Column('pipeline_pass', sa.Integer),
                          sa.Column('gc', sa.Float),
                          sa.Column('bias', sa.Float),
                          sa.Column('score', sa.Float),
                          sa.Column('e_value', sa.Float),
                          sa.Column('inc', sa.String(255)),
                          sa.Column('description', sa.String(255)),
                          sa.Column('alignment', sa.Text))


# Migrations
# ----------


async def migrate(ENVIRONMENT):
    settings = get_postgres_credentials(ENVIRONMENT)

    engine = await create_engine(
        user=settings.POSTGRES_USER,
        database=settings.POSTGRES_DATABASE,
        host=settings.POSTGRES_HOST,
        password=settings.POSTGRES_PASSWORD
    )

    async with engine:
        async with engine.acquire() as connection:
            await connection.execute('DROP TABLE IF EXISTS job_chunk_results')
            await connection.execute('DROP TABLE IF EXISTS job_chunks')
            await connection.execute('DROP TABLE IF EXISTS infernal_result')
            await connection.execute('DROP TABLE IF EXISTS infernal_job')
            await connection.execute('DROP TABLE IF EXISTS jobs')
            await connection.execute('DROP TABLE IF EXISTS consumer')

            await connection.execute('''
                CREATE TABLE consumer (
                  ip VARCHAR(20) PRIMARY KEY,
                  status VARCHAR(255) NOT NULL,
                  job_chunk_id VARCHAR(15),
                  port VARCHAR(10))
            ''')

            await connection.execute('''
                CREATE TABLE jobs (
                  id VARCHAR(36) PRIMARY KEY,
                  query TEXT,
                  description TEXT,
                  ordering TEXT,
                  submitted TIMESTAMP,
                  finished TIMESTAMP,
                  result_in_db BOOLEAN,
                  hits INTEGER,
                  status VARCHAR(255),
                  url VARCHAR(255))
            ''')

            await connection.execute('''
                CREATE TABLE job_chunks (
                  id serial PRIMARY KEY,
                  job_id VARCHAR(36) references jobs(id),
                  database VARCHAR(255),
                  submitted TIMESTAMP,
                  finished TIMESTAMP,
                  consumer VARCHAR(20) references consumer(ip),
                  hits INTEGER,
                  status VARCHAR(255))
            ''')

            await connection.execute('''
                CREATE TABLE job_chunk_results (
                  id serial PRIMARY KEY,
                  job_chunk_id INT references job_chunks(id),
                  rnacentral_id VARCHAR(255) NOT NULL,
                  description TEXT,
                  score FLOAT NOT NULL,
                  bias FLOAT NOT NULL,
                  e_value FLOAT NOT NULL,
                  target_length INTEGER NOT NULL,
                  alignment TEXT NOT NULL,
                  alignment_length INTEGER NOT NULL,
                  gap_count INTEGER NOT NULL,
                  match_count INTEGER NOT NULL,
                  nts_count1 INTEGER NOT NULL,
                  nts_count2 INTEGER NOT NULL,
                  identity FLOAT NOT NULL,
                  query_coverage FLOAT NOT NULL,
                  target_coverage FLOAT NOT NULL,
                  gaps FLOAT NOT NULL,
                  query_length INTEGER NOT NULL,
                  result_id INTEGER NOT NULL)
            ''')

            await connection.execute('''
                CREATE TABLE infernal_job (
                  id serial PRIMARY KEY,
                  job_id VARCHAR(36) references jobs(id),
                  consumer VARCHAR(20) references consumer(ip),
                  submitted TIMESTAMP,
                  finished TIMESTAMP,
                  status VARCHAR(255))
            ''')

            await connection.execute('''
                CREATE TABLE infernal_result (
                  id serial PRIMARY KEY,
                  infernal_job_id INT references infernal_job(id),
                  target_name VARCHAR(255),
                  accession_rfam VARCHAR(255),
                  query_name VARCHAR(255),
                  accession_seq VARCHAR(255),
                  mdl VARCHAR(255),
                  mdl_from INTEGER NOT NULL,
                  mdl_to INTEGER NOT NULL,
                  seq_from INTEGER NOT NULL,
                  seq_to INTEGER NOT NULL,
                  strand VARCHAR(255),
                  trunc VARCHAR(255),
                  pipeline_pass INTEGER NOT NULL,
                  gc FLOAT NOT NULL,
                  bias FLOAT NOT NULL,
                  score FLOAT NOT NULL,
                  e_value FLOAT NOT NULL,
                  inc VARCHAR(255),
                  description VARCHAR(255),
                  alignment TEXT)
            ''')

            await connection.execute('''CREATE INDEX on job_chunks (job_id)''')
            await connection.execute('''CREATE INDEX on job_chunk_results (job_chunk_id)''')
            await connection.execute('''CREATE INDEX on infernal_result (infernal_job_id)''')

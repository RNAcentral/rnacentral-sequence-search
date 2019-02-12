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
import os
import sqlalchemy as sa
from aiopg.sa import create_engine


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


# Models schema
# -------------

JOB_STATUS_CHOICES = (
    ('pending', 'pendind'),
    ('started', 'started'),
    ('success', 'success'),
    ('failed', 'failed'),
)

CONSUMER_STATUS_CHOICES = (
    ('available', 'available'),
    ('busy', 'busy')
)

metadata = sa.MetaData()

# TODO: consistent naming for tables: either 'jobs' and 'consumers' or 'job' and 'consumer'
"""State of a consumer instance"""
Consumer = sa.Table('consumer', metadata,
            sa.Column('ip', sa.String(15), primary_key=True),
            sa.Column('status', sa.String(255)))  # choices=CONSUMER_STATUS_CHOICES, default='available'

"""A search job that is divided into multiple job chunks per database"""
Job = sa.Table('jobs', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('query', sa.Text),
                 sa.Column('submitted', sa.DateTime),
                 sa.Column('finished', sa.DateTime, nullable=True),
                 sa.Column('status', sa.String(255)))  # choices=JOB_STATUS_CHOICES, default='started'

"""Part of the search job, run against a specific database and assigned to a specific consumer"""
JobChunk = sa.Table('job_chunks', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('job_id', None, sa.ForeignKey('jobs.id')),
                  sa.Column('database', sa.String(255)),
                  sa.Column('submitted', sa.DateTime),
                  sa.Column('consumer', sa.ForeignKey('consumer.ip'), nullable=True),
                  sa.Column('result', sa.String(255), nullable=True),
                  sa.Column('status', sa.String(255)))  # choices=JOB_STATUS_CHOICES, default='started'

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
            await connection.execute('DROP TABLE IF EXISTS jobs')
            await connection.execute('DROP TABLE IF EXISTS consumer')

            await connection.execute('''
                CREATE TABLE consumer (
                  ip VARCHAR(15) PRIMARY KEY,
                  status VARCHAR(255) NOT NULL)
            ''')

            for consumer_ip in settings.CONSUMER_IPS:
                await connection.execute(sa.text('''
                    INSERT INTO consumer(ip, status)
                    VALUES (:consumer_ip, 'available')
                '''), consumer_ip=consumer_ip)

            await connection.execute('''
                CREATE TABLE jobs (
                  id serial PRIMARY KEY,
                  query TEXT,
                  submitted TIMESTAMP,
                  finished TIMESTAMP,
                  status VARCHAR(255))
            ''')

            await connection.execute('''
                CREATE TABLE job_chunks (
                  id serial PRIMARY KEY,
                  job_id INT references jobs(id),
                  database VARCHAR(255),
                  submitted TIMESTAMP,
                  consumer VARCHAR(15) references consumer(ip),
                  result VARCHAR(255),
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


if __name__ == "__main__":
    """
    This code creates the necessary tables in the database - in django this
    would've been initial migration.

    To apply this migration to the database, go two directories up and say:

    $ python3 -m sequence_search.db.models
    """
    from .settings import get_postgres_credentials

    ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL')

    import asyncio
    asyncio.get_event_loop().run_until_complete(migrate(ENVIRONMENT))

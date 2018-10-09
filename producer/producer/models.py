"""
Copyright [2009-2017] EMBL-European Bioinformatics Institute
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

import sqlalchemy as sa
from aiopg.sa import create_engine


# Connection initialization code
# ------------------------------

async def init_pg(app):
    engine = await create_engine(
        user=app['settings'].POSTGRES_USER,
        database=app['settings'].POSTGRES_DATABASE,
        host=app['settings'].POSTGRES_HOST,
        password=app['settings'].POSTGRES_PASSWORD
    )

    app['connection'] = await engine.acquire()


async def close_pg(app):
    app['connection'].close()
    await app['connection'].wait_closed()


# Models schema
# -------------

STATUS_CHOICES = (
    ('started', 'started'),
    ('success', 'success'),
    ('failed', 'failed'),
)

metadata = sa.MetaData()

"""A search job that is divided into multiple job chunks per database"""
Job = sa.Table('jobs', metadata,
                 sa.Column('id', sa.Integer, primary_key=True),
                 sa.Column('query', sa.Text),
                 sa.Column('submitted', sa.DateTime),
                 sa.Column('finished', sa.DateTime, nullable=True),
                 sa.Column('status', sa.String(255)))  # choices=STATUS_CHOICES, default='started'

"""Part of the search job, run against a specific database and assigned to a specific consumer"""
JobChunk = sa.Table('job_chunks', metadata,
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('job_id', None, sa.ForeignKey('users.id')),
                  sa.Column('database', sa.String(255)),
                  sa.Column('submitted', sa.DateTime),
                  sa.Column('result', sa.String(255), nullable=True),
                  sa.Column('status', sa.String(255)))  # choices=STATUS_CHOICES, default='started'


# Migrations
# ----------

if __name__ == "__main__":
    """
    This code creates the necessary tables in the database - in django this
    would've been initial migration.

    To apply this migration to the database, go one directory up and say:

    $ python3 -m producer.models
    """
    from . import settings

    async def migrate():
        engine = await create_engine(
            user=settings.POSTGRES_USER,
            database=settings.POSTGRES_DATABASE,
            host=settings.POSTGRES_HOST,
            password=settings.POSTGRES_PASSWORD
        )

        async with engine:
            async with engine.acquire() as connection:
                await connection.execute('DROP TABLE IF EXISTS job_chunks')
                await connection.execute('DROP TABLE IF EXISTS jobs')
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
                      job_id int references jobs(id),
                      database VARCHAR(255),
                      submitted TIMESTAMP,
                      result VARCHAR(255),
                      status VARCHAR(255))
                ''')

    import asyncio
    asyncio.get_event_loop().run_until_complete(migrate())

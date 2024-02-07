"""
Copyright [2009-present] EMBL-European Bioinformatics Institute
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
import psycopg2

from . import DatabaseConnectionError, SQLError
from .models import Statistic


async def get_statistic(engine, source, period):
    """
    Check if there is a record for the source/period passed as a parameter
    :param engine: params to connect to the db
    :param source: source of the search (db name or API)
    :param period: Year-month
    :return: dict with id and total
    """
    try:
        async with engine.acquire() as connection:
            try:
                sql_query = sa.select([Statistic.c.id, Statistic.c.total]).select_from(Statistic).where(
                    (Statistic.c.source == source) & (Statistic.c.period == period)
                )
                async for row in await connection.execute(sql_query):
                    return {"statistic_id": row.id, "statistic_total": row.total}
            except Exception as e:
                raise SQLError("Failed to check if record exists for source %s and period %s" % (source, period)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in get_statistic() for "
                                      "source %s and period %s" % (source, period)) from e


async def update_statistic(engine, identifier, total):
    """
    Update the number of searches performed
    :param engine: params to connect to the db
    :param identifier: id of the statistic to be updated
    :param total: number of searches
    :return: None
    """
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''UPDATE statistic SET total=:total WHERE id=:id''')
                await connection.execute(query, id=identifier, total=total)
            except Exception as e:
                raise SQLError("Failed to update statistic for id = %s and total = %s" % (identifier, total)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in update_statistic() for "
                                      "id = %s and total = %s" % (identifier, total)) from e


async def create_statistic(engine, source, period):
    """
    Create search statistics
    :param engine: params to connect to the db
    :param source: source of the search (db name or API)
    :param period: Year-month
    :return: id
    """
    try:
        async with engine.acquire() as connection:
            try:
                statistic_id = await connection.scalar(
                    Statistic.insert().values(source=source, period=period, total=1)
                )
                return statistic_id
            except Exception as e:
                raise SQLError("Failed to create statistic for source = %s and period = %s" % (source, period)) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in create_statistic() for "
                                      "source = %s and period = %s" % (source, period)) from e

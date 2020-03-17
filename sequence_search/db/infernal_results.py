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

import sqlalchemy as sa
import psycopg2

from . import DatabaseConnectionError, SQLError
from .models import InfernalResult


async def set_infernal_job_results(engine, job_id, results):
    """
    Save infernal results
    :param engine: params to connect to the db
    :param job_id: id of the job
    :param results: data from the deoverlapped file
    :return: id of the infernal_job. It will be used to get the result and save the alignment
    """
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''
                    SELECT id
                    FROM infernal_job
                    WHERE job_id=:job_id
                ''')

                async for row in await connection.execute(query, job_id=job_id):
                    infernal_job_id = row.id
                    break

                for result in results:
                    result['infernal_job_id'] = infernal_job_id

                await connection.execute(InfernalResult.insert().values(results))

                return infernal_job_id

            except Exception as e:
                raise SQLError("Failed to set_infernal_job_results in the database, "
                               "job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in set_infernal_job_results, "
                                      "job_id = %s" % job_id) from e


async def get_infernal_result_id(engine, infernal_job_id, item):
    """
    Get infernal_result id
    :param engine: params to connect to the db
    :param infernal_job_id: id of the infernal_job
    :param item: dict with values to find the id of the infernal_result
    :return: id of the infernal_result
    """
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''
                    SELECT id
                    FROM infernal_result
                    WHERE infernal_job_id=:infernal_job_id AND accession_rfam=:accession_rfam AND mdl_from=:mdl_from
                    AND mdl_to=:mdl_to AND seq_from=:seq_from AND seq_to=:seq_to AND gc=:gc AND score=:score
                    AND e_value=:e_value
                ''')

                infernal_result_id = None
                async for row in await connection.execute(
                        query, infernal_job_id=infernal_job_id, accession_rfam=item['accession_rfam'],
                        mdl_from=item['mdl_from'], mdl_to=item['mdl_to'], seq_from=item['seq_from'],
                        seq_to=item['seq_to'], gc=item['gc'], score=item['score'], e_value=item['e_value']):
                    infernal_result_id = row.id
                    break

                return infernal_result_id

            except Exception as e:
                raise SQLError("Failed to get_infernal_result_id in the database, "
                               "infernal_job_id = %s" % infernal_job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in get_infernal_result_id, "
                                      "infernal_job_id = %s" % infernal_job_id) from e


async def save_alignment(engine, infernal_result_id, alignment):
    """
    Save the alignment
    :param engine: params to connect to the db
    :param infernal_result_id: id of the infernal_result
    :param alignment: alignment to be saved
    """
    try:
        async with engine.acquire() as connection:
            try:
                query = sa.text('''
                    UPDATE infernal_result SET alignment=:alignment 
                    WHERE id=:infernal_result_id
                ''')
                await connection.execute(query, alignment=alignment, infernal_result_id=infernal_result_id)
            except Exception as e:
                raise SQLError("Failed to save_alignment in the database, "
                               "infernal_result_id = %s" % infernal_result_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in save_alignment, "
                                      "infernal_result_id = %s" % infernal_result_id) from e

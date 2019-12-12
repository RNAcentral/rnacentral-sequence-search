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
            except Exception as e:
                raise SQLError("Failed to set_infernal_job_results in the database, "
                               "job_id = %s" % job_id) from e
    except psycopg2.Error as e:
        raise DatabaseConnectionError("Failed to open connection to the database in set_infernal_job_results, "
                                      "job_id = %s" % job_id) from e

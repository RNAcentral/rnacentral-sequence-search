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

import asyncio
from aiopg.sa import create_engine


async def init_pg():
    engine = await create_engine(
        user='aiopg',
        database='aiopg',
        host='127.0.0.1',
        password='passwd'
    )

    async with engine:
        async with engine.acquire() as conn:
            await create_tables(conn)
            await fill_data(conn)
            await count(conn)
            await show_julia(conn)
            await ave_age(conn)

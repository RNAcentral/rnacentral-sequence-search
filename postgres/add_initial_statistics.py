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

import asyncio
import os

from aiopg.sa import create_engine
from dotenv import load_dotenv

from sequence_search.db.models import Statistic

load_dotenv()


async def add_statistics():
    """
    Save the metadata of a given database.
    Run it with: python3 add_initial_statistics.py
    :return: None
    """
    # get credentials
    user = os.getenv("username")
    database = os.getenv("db")
    host = os.getenv("host")
    password = os.getenv("pass")

    initial_data = [
        {'period': '2020-05', 'source': 'RNAcentral', 'total': 1116},
        {'period': '2020-06', 'source': 'RNAcentral', 'total': 613},
        {'period': '2020-07', 'source': 'RNAcentral', 'total': 850},
        {'period': '2020-08', 'source': 'RNAcentral', 'total': 1584},
        {'period': '2020-09', 'source': 'RNAcentral', 'total': 2263},
        {'period': '2020-10', 'source': 'RNAcentral', 'total': 1435},
        {'period': '2020-11', 'source': 'RNAcentral', 'total': 900},
        {'period': '2020-12', 'source': 'RNAcentral', 'total': 672},
        {'period': '2021-01', 'source': 'RNAcentral', 'total': 1242},
        {'period': '2021-02', 'source': 'RNAcentral', 'total': 883},
        {'period': '2021-03', 'source': 'RNAcentral', 'total': 2482},
        {'period': '2021-04', 'source': 'RNAcentral', 'total': 942},
        {'period': '2021-05', 'source': 'RNAcentral', 'total': 1173},
        {'period': '2021-06', 'source': 'RNAcentral', 'total': 869},
        {'period': '2021-07', 'source': 'RNAcentral', 'total': 835},
        {'period': '2021-08', 'source': 'RNAcentral', 'total': 763},
        {'period': '2021-09', 'source': 'RNAcentral', 'total': 837},
        {'period': '2021-10', 'source': 'RNAcentral', 'total': 1336},
        {'period': '2021-11', 'source': 'RNAcentral', 'total': 1267},
        {'period': '2021-12', 'source': 'RNAcentral', 'total': 1077},
        {'period': '2022-01', 'source': 'RNAcentral', 'total': 826},
        {'period': '2022-02', 'source': 'RNAcentral', 'total': 1159},
        {'period': '2022-03', 'source': 'RNAcentral', 'total': 1002},
        {'period': '2022-04', 'source': 'RNAcentral', 'total': 488},
        {'period': '2020-05', 'source': 'Rfam', 'total': 1313},
        {'period': '2020-06', 'source': 'Rfam', 'total': 540},
        {'period': '2020-07', 'source': 'Rfam', 'total': 1611},
        {'period': '2020-08', 'source': 'Rfam', 'total': 1010},
        {'period': '2020-09', 'source': 'Rfam', 'total': 1005},
        {'period': '2020-10', 'source': 'Rfam', 'total': 1292},
        {'period': '2020-11', 'source': 'Rfam', 'total': 1806},
        {'period': '2020-12', 'source': 'Rfam', 'total': 1340},
        {'period': '2021-01', 'source': 'Rfam', 'total': 1254},
        {'period': '2021-02', 'source': 'Rfam', 'total': 1452},
        {'period': '2021-03', 'source': 'Rfam', 'total': 1538},
        {'period': '2021-04', 'source': 'Rfam', 'total': 1102},
        {'period': '2021-05', 'source': 'Rfam', 'total': 1278},
        {'period': '2021-06', 'source': 'Rfam', 'total': 1149},
        {'period': '2021-07', 'source': 'Rfam', 'total': 1031},
        {'period': '2021-08', 'source': 'Rfam', 'total': 2580},
        {'period': '2021-09', 'source': 'Rfam', 'total': 1095},
        {'period': '2021-10', 'source': 'Rfam', 'total': 2826},
        {'period': '2021-11', 'source': 'Rfam', 'total': 2305},
        {'period': '2021-12', 'source': 'Rfam', 'total': 1594},
        {'period': '2022-01', 'source': 'Rfam', 'total': 1560},
        {'period': '2022-02', 'source': 'Rfam', 'total': 1279},
        {'period': '2022-03', 'source': 'Rfam', 'total': 1204},
        {'period': '2022-04', 'source': 'Rfam', 'total': 1699},
        {'period': '2020-07', 'source': 'miRBase', 'total': 351},
        {'period': '2020-08', 'source': 'miRBase', 'total': 614},
        {'period': '2020-09', 'source': 'miRBase', 'total': 827},
        {'period': '2020-10', 'source': 'miRBase', 'total': 529},
        {'period': '2020-11', 'source': 'miRBase', 'total': 497},
        {'period': '2020-12', 'source': 'miRBase', 'total': 849},
        {'period': '2021-01', 'source': 'miRBase', 'total': 2202},
        {'period': '2021-02', 'source': 'miRBase', 'total': 1109},
        {'period': '2021-03', 'source': 'miRBase', 'total': 1109},
        {'period': '2021-04', 'source': 'miRBase', 'total': 1489},
        {'period': '2021-05', 'source': 'miRBase', 'total': 398},
        {'period': '2021-06', 'source': 'miRBase', 'total': 958},
        {'period': '2021-07', 'source': 'miRBase', 'total': 1217},
        {'period': '2021-08', 'source': 'miRBase', 'total': 381},
        {'period': '2021-09', 'source': 'miRBase', 'total': 399},
        {'period': '2021-10', 'source': 'miRBase', 'total': 385},
        {'period': '2021-11', 'source': 'miRBase', 'total': 632},
        {'period': '2021-12', 'source': 'miRBase', 'total': 442},
        {'period': '2022-01', 'source': 'miRBase', 'total': 355},
        {'period': '2022-02', 'source': 'miRBase', 'total': 477},
        {'period': '2022-03', 'source': 'miRBase', 'total': 1389},
        {'period': '2022-04', 'source': 'miRBase', 'total': 530},
        {'period': '2020-07', 'source': 'snoDB', 'total': 74},
        {'period': '2020-08', 'source': 'snoDB', 'total': 0},
        {'period': '2020-09', 'source': 'snoDB', 'total': 32},
        {'period': '2020-10', 'source': 'snoDB', 'total': 11},
        {'period': '2020-11', 'source': 'snoDB', 'total': 69},
        {'period': '2020-12', 'source': 'snoDB', 'total': 4},
        {'period': '2021-01', 'source': 'snoDB', 'total': 53},
        {'period': '2021-02', 'source': 'snoDB', 'total': 4},
        {'period': '2021-03', 'source': 'snoDB', 'total': 9},
        {'period': '2021-04', 'source': 'snoDB', 'total': 2},
        {'period': '2021-05', 'source': 'snoDB', 'total': 4},
        {'period': '2021-06', 'source': 'snoDB', 'total': 3},
        {'period': '2021-07', 'source': 'snoDB', 'total': 6},
        {'period': '2021-08', 'source': 'snoDB', 'total': 4},
        {'period': '2021-09', 'source': 'snoDB', 'total': 6},
        {'period': '2021-10', 'source': 'snoDB', 'total': 13},
        {'period': '2021-11', 'source': 'snoDB', 'total': 32},
        {'period': '2021-12', 'source': 'snoDB', 'total': 9},
        {'period': '2022-01', 'source': 'snoDB', 'total': 4},
        {'period': '2022-02', 'source': 'snoDB', 'total': 17},
        {'period': '2022-03', 'source': 'snoDB', 'total': 11},
        {'period': '2022-04', 'source': 'snoDB', 'total': 12},
        {'period': '2020-11', 'source': 'GtRNAdb', 'total': 60},
        {'period': '2020-12', 'source': 'GtRNAdb', 'total': 26},
        {'period': '2021-01', 'source': 'GtRNAdb', 'total': 10},
        {'period': '2021-02', 'source': 'GtRNAdb', 'total': 13},
        {'period': '2021-03', 'source': 'GtRNAdb', 'total': 51},
        {'period': '2021-04', 'source': 'GtRNAdb', 'total': 6},
        {'period': '2021-05', 'source': 'GtRNAdb', 'total': 38},
        {'period': '2021-06', 'source': 'GtRNAdb', 'total': 19},
        {'period': '2021-07', 'source': 'GtRNAdb', 'total': 17},
        {'period': '2021-08', 'source': 'GtRNAdb', 'total': 18},
        {'period': '2021-09', 'source': 'GtRNAdb', 'total': 16},
        {'period': '2021-10', 'source': 'GtRNAdb', 'total': 63},
        {'period': '2021-11', 'source': 'GtRNAdb', 'total': 34},
        {'period': '2021-12', 'source': 'GtRNAdb', 'total': 15},
        {'period': '2022-01', 'source': 'GtRNAdb', 'total': 30},
        {'period': '2022-02', 'source': 'GtRNAdb', 'total': 10},
        {'period': '2022-03', 'source': 'GtRNAdb', 'total': 6},
        {'period': '2022-04', 'source': 'GtRNAdb', 'total': 11},
        {'period': '2020-10', 'source': 'API', 'total': 5168},
        {'period': '2020-12', 'source': 'API', 'total': 15376},
        {'period': '2021-05', 'source': 'API', 'total': 794},
        {'period': '2021-06', 'source': 'API', 'total': 710},
        {'period': '2021-09', 'source': 'API', 'total': 747},
        {'period': '2022-02', 'source': 'API', 'total': 8816},
        {'period': '2022-03', 'source': 'API', 'total': 1083},
        {'period': '2022-04', 'source': 'API', 'total': 2094},
    ]

    async with create_engine(user=user, database=database, host=host, password=password) as engine:
        async with engine.acquire() as connection:
            await connection.execute(Statistic.insert().values(initial_data))


if __name__ == '__main__':
    asyncio.run(add_statistics())

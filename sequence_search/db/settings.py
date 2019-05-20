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

import os
from collections import namedtuple


Settings = namedtuple('Settings', [
    'POSTGRES_HOST',
    'POSTGRES_PORT',
    'POSTGRES_DATABASE',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
    'ENVIRONMENT'
])


def get_postgres_credentials(ENVIRONMENT):
    ENVIRONMENT = ENVIRONMENT.upper()

    if ENVIRONMENT == 'DOCKER-COMPOSE':
        return Settings(
            POSTGRES_HOST='postgres',
            POSTGRES_PORT=5432,
            POSTGRES_DATABASE='producer',
            POSTGRES_USER='docker',
            POSTGRES_PASSWORD='example',
            ENVIRONMENT=ENVIRONMENT
        )
    elif ENVIRONMENT == 'LOCAL':
        return Settings(
            POSTGRES_HOST='localhost',
            POSTGRES_PORT=5432,
            POSTGRES_DATABASE='producer',
            POSTGRES_USER='apetrov',
            POSTGRES_PASSWORD='example',
            ENVIRONMENT=ENVIRONMENT
        )
    elif ENVIRONMENT == 'PRODUCTION':
        return Settings(
            POSTGRES_HOST='192.168.0.6',
            POSTGRES_PORT=5432,
            POSTGRES_DATABASE='producer',
            POSTGRES_USER='docker',
            POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD', 'pass'),
            ENVIRONMENT=ENVIRONMENT
        )
    elif ENVIRONMENT == 'TEST':
        return Settings(
            POSTGRES_HOST='localhost',
            POSTGRES_PORT=5432,
            POSTGRES_DATABASE='test_producer',
            POSTGRES_USER='burkov',
            POSTGRES_PASSWORD='example',
            ENVIRONMENT='LOCAL'
        )

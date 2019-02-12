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


def get_postgres_credentials(ENVIRONMENT):
    if ENVIRONMENT == 'docker-compose':
        return {
            'POSTGRES_HOST' : 'postgres',
            'POSTGRES_PORT' : 5432,
            'POSTGRES_DATABASE' : 'producer',
            'POSTGRES_USER' : 'docker',
            'POSTGRES_PASSWORD' : 'example'
        }
    elif ENVIRONMENT == 'local':
        return {
            'POSTGRES_HOST' : 'localhost',
            'POSTGRES_PORT' : 5432,
            'POSTGRES_DATABASE' : 'producer',
            'POSTGRES_USER' : 'burkov',
            'POSTGRES_PASSWORD' : 'example'
        }
    elif ENVIRONMENT == 'production':
        return {
            'POSTGRES_HOST': '192.168.0.6',
            'POSTGRES_PORT': 5432,
            'POSTGRES_DATABASE': 'producer',
            'POSTGRES_USER': 'docker',
            'POSTGRES_PASSWORD': os.getenv('POSTRGES_PASSWORD', 'pass')
        }
    elif ENVIRONMENT == 'test':
        return {
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': 5432,
            'POSTGRES_DATABASE': 'test_producer',
            'POSTGRES_USER': 'burkov',
            'POSTGRES_PASSWORD': 'example'
        }

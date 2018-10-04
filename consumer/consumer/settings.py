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
import os
import pathlib


"""
The code below is stolen from default project.
"""


class Required:
    def __init__(self, v_type=None):
        self.v_type = v_type


class Settings:
    """
    Any setting defined here can be overridden by:

    Settings the appropriate environment variable, eg. to override FOOBAR, `export APP_FOOBAR="whatever"`.
    This is useful in production for secrets you do not wish to save in code and
    also plays nicely with docker(-compose). Settings will attempt to convert environment variables to match the
    type of the value here. See also activate.settings.sh.

    Or, passing the custom setting as a keyword argument when initialising settings (useful when testing)
    """
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL')

    # consumer folder, where media, static, templates and other subfolders are located
    PROJECT_ROOT = pathlib.Path(__file__).parent

    # full path to sequence database
    SEQDATABASES = PROJECT_ROOT / 'databases'

    # full path to nhmmer executable
    NHMMER_EXECUTABLE = 'nhmmer'

    # minimum query sequence length
    MIN_LENGTH = 10

    # maximum query sequence length
    MAX_LENGTH = 10000

    # results expiration time
    EXPIRATION = 60 * 60 * 24 * 7  # seconds

    # maximum time to run nhmmer
    MAX_RUN_TIME = 60 * 60  # seconds

    # list of rnacentral databases
    RNACENTRAL_DATABASES = [
        "greengenes",
        "pdbe",
        "refseq",
        "sgd",
        "tair",
        "lncrnadb",
        "pombase",
        "rfam",
        "snopy",
        "tmrna_web",
        "mirbase",
        "rdp",
        "rgd",
        "srpdb",
        "wormbase"
    ]

    if ENVIRONMENT == "LOCAL":
        # full path to results files
        RESULTS_DIR = PROJECT_ROOT / 'results'

        # full path to query files
        QUERY_DIR = PROJECT_ROOT / 'queries'

        # hostname to listen on
        HOST = 'localhost'

        # TCP port for the server to listen on
        PORT = 8000

        # producer server location
        PRODUCER_PROTOCOL = 'http'
        PRODUCER_HOST = 'localhost'
        PRODUCER_PORT = '8002'
        PRODUCER_JOB_DONE_URL = 'job-done'

    elif ENVIRONMENT == "TEST":
        # in test save queries and results in a temporary folder
        TMP_DIR = PROJECT_ROOT / '.tmp'

        # full path to query files
        RESULTS_DIR = PROJECT_ROOT / '.tmp' / 'results'

        # full path to query files
        QUERY_DIR = PROJECT_ROOT / '.tmp' / 'queries'

        # hostname to listen on
        HOST = 'localhost'

        # TCP port for the server to listen on
        PORT = 8000

        # producer server location
        PRODUCER_PROTOCOL = 'http'
        PRODUCER_HOST = 'localhost'
        PRODUCER_PORT = '8002'
        PRODUCER_JOB_DONE_URL = 'job-done'

    elif ENVIRONMENT == "DOCKER-COMPOSE":
        # full path to results files
        RESULTS_DIR = PROJECT_ROOT / 'results'

        # full path to query files
        QUERY_DIR = PROJECT_ROOT / 'queries'

        # hostname to listen on
        HOST = '0.0.0.0'

        # TCP port for the server to listen on
        PORT = 8000

        # producer server location
        PRODUCER_PROTOCOL = 'http'
        PRODUCER_HOST = 'producer'
        PRODUCER_PORT = '8002'
        PRODUCER_JOB_DONE_URL = 'job-done'

    elif ENVIRONMENT == "PRODUCTION":
        # hostname to listen on
        HOST = '0.0.0.0'

        # TCP port for the server to listen on
        PORT = 8000

        # full path to results files
        RESULTS_DIR = PROJECT_ROOT / 'results'

        # full path to query files
        QUERY_DIR = PROJECT_ROOT / 'queries'

        # producer server location
        PRODUCER_PROTOCOL = 'http'
        PRODUCER_HOST = '192.168.0.5'
        PRODUCER_PORT = '8002'
        PRODUCER_JOB_DONE_URL = 'job-done'

    def __init__(self, **custom_settings):
        """
        :param custom_settings: Custom settings to override defaults, only attributes already defined can be set.
        """
        self._custom_settings = custom_settings
        self.substitute_environ()
        for name, value in custom_settings.items():
            if not hasattr(self, name):
                raise TypeError('{} is not a valid setting name'.format(name))
            setattr(self, name, value)

    def substitute_environ(self):
        """
        Substitute environment variables into settings.
        """
        for attr_name in dir(self):
            if attr_name.startswith('_') or attr_name.upper() != attr_name:
                continue
            elif os.getenv(attr_name, None) is not None:
                setattr(self, attr_name, os.getenv(attr_name))


settings = Settings()

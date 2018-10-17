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
Any setting defined here can be overridden by:

Settings the appropriate environment variable, eg. to override FOOBAR, `export APP_FOOBAR="whatever"`.
This is useful in production for secrets you do not wish to save in code and
also plays nicely with docker(-compose). Settings will attempt to convert environment variables to match the
type of the value here. See also activate.settings.sh.

Or, passing the custom setting as a keyword argument when initialising settings (useful when testing)
"""

# consumer folder, where media, static, templates and other subfolders are located
PROJECT_ROOT = pathlib.Path(__file__).parent.parent

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

CONSUMER_SUBMIT_JOB_URL = 'submit-job'

ENVIRONMENT = os.getenv('ENVIRONMENT', 'LOCAL')

# add settings from environment-specific files
if ENVIRONMENT == "LOCAL":
    from .local import *
elif ENVIRONMENT == "TEST":
    from .test import *
elif ENVIRONMENT == "DOCKER-COMPOSE":
    from .docker_compose import *
elif ENVIRONMENT == "PRODUCTION":
    from .production import *

EBI_SEARCH_PROXY_URL = 'http://ves-hx-a4:8003/post'


def substitute_environment_variables():
    """
    Substitute environment variables into settings.

    This function is stolen from the default project, generated by
    aiohttp-devtools 'adev start' command.
    """
    for attr_name in globals():
        env_var = os.getenv(attr_name, None)

        if attr_name.startswith('_') or attr_name.upper() != attr_name:
            continue
        elif env_var is not None:
            # convert environment variable to the same type as the variable in settings
            original_type = type(globals()[attr_name])
            if issubclass(original_type, bool):
                env_var = env_var.upper() in ('1', 'TRUE')
            elif issubclass(original_type, int):
                env_var = int(env_var)
            elif issubclass(original_type, float):
                env_var = float(env_var)
            elif issubclass(original_type, pathlib.Path):
                env_var = pathlib.Path(env_var)
            elif issubclass(original_type, bytes):
                env_var = env_var.encode()

            globals()[attr_name] = env_var


substitute_environment_variables()

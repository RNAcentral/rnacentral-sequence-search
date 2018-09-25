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

    # hostname to listen on
    HOST = 'localhost'

    # TCP port for the server to listen on
    PORT = 8000

    # consumer folder, where media, static, templates and other subfolders are located
    PROJECT_ROOT = pathlib.Path(__file__).parent

    # full path to results files
    RESULTS_DIR = PROJECT_ROOT / 'results'

    # full path to query files
    QUERY_DIR = PROJECT_ROOT / 'queries'

    # full path to nhmmer executable
    NHMMER_EXECUTABLE = 'nhmmer'

    # full path to sequence database
    SEQDATABASE = PROJECT_ROOT / 'databases' / 'rnacentral_nhmmer.fasta'

    # minimum query sequence length
    MIN_LENGTH = 10

    # maximum query sequence length
    MAX_LENGTH = 10000

    # Redis results expiration time
    EXPIRATION = 60 * 60 * 24 * 7  # seconds

    # maximum time to run nhmmer
    MAX_RUN_TIME = 60 * 60  # seconds

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

            orig_value = getattr(self, attr_name)
            is_required = isinstance(orig_value, Required)
            orig_type = orig_value.v_type if is_required else type(orig_value)
            env_var_name = attr_name
            env_var = os.getenv(env_var_name, None)
            if env_var is not None:
                if issubclass(orig_type, bool):
                    env_var = env_var.upper() in ('1', 'TRUE')
                elif issubclass(orig_type, int):
                    env_var = int(env_var)
                elif issubclass(orig_type, pathlib.Path):
                    env_var = pathlib.Path(env_var)
                elif issubclass(orig_type, bytes):
                    env_var = env_var.encode()
                # could do floats here and lists etc via json
                setattr(self, attr_name, env_var)
            elif is_required and attr_name not in self._custom_settings:
                raise RuntimeError('The required environment variable "{0}" is currently not set, '
                                   'you\'ll need to run `source activate.settings.sh` '
                                   'or you can set that single environment variable with '
                                   '`export {0}="<value>"`'.format(env_var_name))


settings = Settings()

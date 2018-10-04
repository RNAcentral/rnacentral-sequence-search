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
import shutil

from aiohttp.test_utils import AioHTTPTestCase

from ..settings import settings


TMP_DIR = settings.PROJECT_ROOT / '.tmp'
RESULTS_DIR = settings.PROJECT_ROOT / '.tmp' / 'results'
QUERY_DIR = settings.PROJECT_ROOT / '.tmp' / 'queries'


class ConsumerTestCase(AioHTTPTestCase):
    @classmethod
    def setUpClass(cls):
        settings.RESULTS_DIR = RESULTS_DIR
        settings.QUERY_DIR = QUERY_DIR

        # create temporary directories for queries and results
        try:
            os.mkdir(TMP_DIR)
        except FileExistsError:
            pass

        try:
            os.mkdir(RESULTS_DIR)
        except FileExistsError:
            pass

        try:
            os.mkdir(QUERY_DIR)
        except FileExistsError:
            pass

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TMP_DIR)
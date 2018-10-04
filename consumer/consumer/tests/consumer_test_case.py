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


class ConsumerTestCase(AioHTTPTestCase):
    @classmethod
    def setUpClass(cls):
        """Create temporary directories for queries and results"""
        try:
            os.mkdir(settings.TMP_DIR)
        except FileExistsError:
            pass

        try:
            os.mkdir(settings.RESULTS_DIR)
        except FileExistsError:
            pass

        try:
            os.mkdir(settings.QUERY_DIR)
        except FileExistsError:
            pass

    @classmethod
    def tearDownClass(cls):
        """Remove temporary directories"""
        shutil.rmtree(settings.TMP_DIR)

    # def tearDown(self):
    #     """Clear the temporary directories after each unit-test"""
    #     super().tearDown()
    #
    #     for file in os.listdir(QUERY_DIR):
    #         os.remove(QUERY_DIR / file)
    #
    #     for file in os.listdir(RESULTS_DIR):
    #         os.remove(RESULTS_DIR / file)

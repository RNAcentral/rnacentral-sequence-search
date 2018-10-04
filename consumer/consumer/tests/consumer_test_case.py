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
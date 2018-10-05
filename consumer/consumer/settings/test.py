from . import PROJECT_ROOT

# hostname to listen on
HOST = 'localhost'

# TCP port for the server to listen on
PORT = 8000

# in test save queries and results in a temporary folder
TMP_DIR = PROJECT_ROOT / '.tmp'

# full path to query files
RESULTS_DIR = PROJECT_ROOT / '.tmp' / 'results'

# full path to query files
QUERY_DIR = PROJECT_ROOT / '.tmp' / 'queries'

# producer server location
PRODUCER_PROTOCOL = 'http'
PRODUCER_HOST = 'localhost'
PRODUCER_PORT = '8002'
PRODUCER_JOB_DONE_URL = 'job-done'

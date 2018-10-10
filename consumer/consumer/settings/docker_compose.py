from . import PROJECT_ROOT

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
PRODUCER_HOST = 'producer'
PRODUCER_PORT = '8002'
PRODUCER_JOB_DONE_URL = 'api/job-done'
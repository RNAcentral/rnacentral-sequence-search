from . import PROJECT_ROOT


# full path to results files
RESULTS_DIR = PROJECT_ROOT / 'results'

# full path to query files
QUERY_DIR = PROJECT_ROOT / 'queries'

# producer server location
PRODUCER_PROTOCOL = 'http'
PRODUCER_HOST = 'producer'
PRODUCER_PORT = '8002'
PRODUCER_JOB_DONE_URL = 'api/job-done'

# full path to nhmmer executable
NHMMER_EXECUTABLE = 'nhmmer'

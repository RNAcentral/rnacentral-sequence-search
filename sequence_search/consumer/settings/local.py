from . import PROJECT_ROOT


# full path to results files
RESULTS_DIR = PROJECT_ROOT / 'results'

# full path to query files
QUERY_DIR = PROJECT_ROOT / 'queries'

# full path to infernal results files
INFERNAL_RESULTS_DIR = PROJECT_ROOT / 'infernal-results'

# full path to infernal query files
INFERNAL_QUERY_DIR = PROJECT_ROOT / 'infernal-queries'

# full path to the rfam.cm
RFAM_CM = PROJECT_ROOT / 'rfam' / 'Rfam.cm'

# full path to the cmsearch-deoverlap.pl
DEOVERLAP = PROJECT_ROOT / 'cmsearch_tblout_deoverlap' / 'cmsearch-deoverlap.pl'

# producer server location
PRODUCER_PROTOCOL = 'http'
PRODUCER_HOST = 'localhost' # 'host.docker.internal'
PRODUCER_PORT = '8002'
PRODUCER_JOB_DONE_URL = 'api/job-done'

# full path to nhmmer executable
NHMMER_EXECUTABLE = 'nhmmer'

# full path to cmscan executable
CMSCAN_EXECUTABLE = 'cmscan'

# total number of entries to analyse from nhmmer result file
NHMMER_LIMIT = 1000

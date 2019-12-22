from . import PROJECT_ROOT


# in test save queries and results in a temporary folder
TMP_DIR = PROJECT_ROOT / '.tmp'

# full path to query files
RESULTS_DIR = PROJECT_ROOT / '.tmp' / 'results'

# full path to query files
QUERY_DIR = PROJECT_ROOT / '.tmp' / 'queries'

# full path to infernal results files
INFERNAL_RESULTS_DIR = PROJECT_ROOT / '.tmp' / 'infernal-results'

# full path to infernal query files
INFERNAL_QUERY_DIR = PROJECT_ROOT / '.tmp' / 'infernal-queries'

# full path to the rfam.cm
RFAM_CM = PROJECT_ROOT / 'rfam' / 'Rfam.cm'

# full path to the cmsearch-deoverlap.pl
DEOVERLAP = PROJECT_ROOT / 'cmsearch_tblout_deoverlap-master' / 'cmsearch-deoverlap.pl'

# producer server location
PRODUCER_PROTOCOL = 'http'
PRODUCER_HOST = 'localhost'
PRODUCER_PORT = '8002'
PRODUCER_JOB_DONE_URL = 'api/job-done'

# full path to nhmmer executable
NHMMER_EXECUTABLE = 'nhmmer'

# full path to cmscan executable
CMSCAN_EXECUTABLE = 'cmscan'


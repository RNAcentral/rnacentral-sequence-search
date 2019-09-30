# Script to regularly run a specific search and check the results

# -o allexport enables all following variable definitions to be exported.
# +o allexport disables this feature.
set -o allexport
source .conf-file
set +o allexport

CONTENT_TYPE="Content-Type: application/json"
DATABASE_AND_QUERY="{\"databases\": [\"mirbase\"], \"query\": \"CUGUACUAUCUACUGUCUCUC\"}"
HOST_AND_PORT="https://search.rnacentral.org"

# Submit a job
JOB_ID=$(curl -s -H "${CONTENT_TYPE}" -d "${DATABASE_AND_QUERY}" ${HOST_AND_PORT}/api/submit-job | jq -r '.job_id')
#echo "The job id: ${JOB_ID}"

# Job status
# Expected response: "started"
INITIAL_STATUS=$(curl -s ${HOST_AND_PORT}/api/job-status/$JOB_ID | jq -r '.chunks | .[] | .status')
#echo "The initial status: ${INITIAL_STATUS}"

# Waits 5 seconds.
sleep 5s

# Job status
# Expected response: "success"
FINAL_STATUS=$(curl -s ${HOST_AND_PORT}/api/job-status/$JOB_ID | jq -r '.chunks | .[] | .status')
#echo "The final status: ${FINAL_STATUS}"

# Facets search
# Expected response: "hitCount = 23 and textSearchError = false"
FACETS_SEARCH=$(curl -s ${HOST_AND_PORT}/api/facets-search/$JOB_ID | jq '[.hitCount,.textSearchError]')
HIT_COUNT=$(echo ${FACETS_SEARCH} |  jq '.[0]')
SEARCH_ERROR=$(echo ${FACETS_SEARCH} |  jq '.[1]')
#echo $HIT_COUNT
#echo $SEARCH_ERROR

# Send message in case of unexpected result
if [ "$INITIAL_STATUS" != "started" ] || [ "$FINAL_STATUS" != "success" ] || [ "$HIT_COUNT" != "23" ] || [ "$SEARCH_ERROR" != "false" ]
then
#    echo "There is something wrong here!"
    curl -s --url $SMTP --ssl-reqd \
      --mail-from $FROM \
      --mail-rcpt $TO \
      --user $FROM":"$PASSWORD \
      -T <(echo -e "From: ${FROM}\nTo: ${TO}\nSubject: API Error\n\n
      Please check the RNAcentral sequence search. Last output was: \n\n
      The initial status: ${INITIAL_STATUS}\n\n
      The final status: ${FINAL_STATUS}\n\n
      The hit count: ${HIT_COUNT}\n\n
      The text search error: ${SEARCH_ERROR}\n\n
      and the expected result was 'started', 'success', '23' and 'false' respectively.")
    exit
fi

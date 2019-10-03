# Script to regularly run a specific search and check the results

# -o allexport enables all following variable definitions to be exported.
# +o allexport disables this feature.
set -o allexport
source .conf-file
set +o allexport

CONTENT_TYPE="Content-Type: application/json"
DATABASE_AND_QUERY="{\"databases\": [\"mirbase\"], \"query\": \"CUGUACUAUCUACUGUCUCUC\"}"
HOST="https://rnacentral.org"
ENDPOINT="sequence-search-beta"

# First check if the $HOST is up
if curl -s --head  --request GET $HOST | grep "200 OK" > /dev/null; then
    # Submit a job
    JOB_ID=$(curl -s -H "${CONTENT_TYPE}" -d "${DATABASE_AND_QUERY}" ${HOST}/${ENDPOINT}/submit-job | jq -r '.job_id')

    # Job status
    # Expected response: "started"
    INITIAL_STATUS=$(curl -s ${HOST}/${ENDPOINT}/job-status/$JOB_ID | jq -r '.chunks | .[] | .status')

    # Waits 5 seconds.
    sleep 5s

    # Job status
    # Expected response: "success"
    FINAL_STATUS=$(curl -s ${HOST}/${ENDPOINT}/job-status/$JOB_ID | jq -r '.chunks | .[] | .status')

    # Facets search
    # Expected response: "hitCount = 23 and textSearchError = false"
    FACETS_SEARCH=$(curl -s ${HOST}/${ENDPOINT}/job-results/$JOB_ID | jq '[.hitCount,.textSearchError]')
    HIT_COUNT=$(echo ${FACETS_SEARCH} |  jq '.[0]')
    SEARCH_ERROR=$(echo ${FACETS_SEARCH} |  jq '.[1]')

    # Send message in case of unexpected result
    if [ "$INITIAL_STATUS" != "started" ] || [ "$FINAL_STATUS" != "success" ] || [ "$HIT_COUNT" != "23" ] || [ "$SEARCH_ERROR" != "false" ]
    then
        text="Ops! There is something wrong with the RNAcentral sequence search. Please check the links below: \n
        \n
        To check the status see: ${HOST}/${ENDPOINT}/job-status/$JOB_ID \n
        The status output: ${INITIAL_STATUS} and ${FINAL_STATUS}. The expected status: started and success. \n
        \n
        To check the results see: ${HOST}/${ENDPOINT}/job-results/$JOB_ID \n
        The result output: ${HIT_COUNT} and ${SEARCH_ERROR}. The expected result: 23 and false."
        escapedText=$(echo ${text} | sed 's/"/\"/g' | sed "s/'/\'/g" )
        json="{\"text\": \"$escapedText\"}"
        curl -s -d "payload=$json" $WEBHOOK_URL
        exit
    fi
# No worries if it's not up, UptimeRobot will notify the team.
else
    echo "${HOST} is DOWN!"
fi

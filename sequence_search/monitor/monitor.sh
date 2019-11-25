# Script to regularly run a search and check the results.
# Each job searches a different sequence with a different size to avoid retrieving database results.

# -o allexport enables all following variable definitions to be exported.
# +o allexport disables this feature.
set -o allexport
source $PWD/.conf-file
set +o allexport

CONTENT_TYPE="Content-Type: application/json"
SIZE=$(( $RANDOM % 5 + 20 ))
NEW_SEQUENCE=$(cat /dev/urandom | env LC_CTYPE=C tr -dc ACGTU | head -c $SIZE)
DATABASES_LIST=("flybase" "gencode" "mirbase" "pdbe" "snopy" "srpdb")
DATABASE=${DATABASES_LIST[RANDOM%${#DATABASES_LIST[@]}]}
DATABASE_AND_QUERY="{\"databases\": [\"$DATABASE\"], \"query\": \">sequence-search-test\n$NEW_SEQUENCE\"}"

# Run search on the correct target (test or default).
# Ansible adds the correct floating_ip to the .conf-file
HOST="http://$(echo $FLOATING_IP | sed 's/[][]//g'):8002"

# First check if the $HOST is up
if curl -s --head  --request GET $HOST | grep "200 OK" > /dev/null; then
    # Submit a job
    JOB_ID=$(curl -s -H "${CONTENT_TYPE}" -d "${DATABASE_AND_QUERY}" ${HOST}/api/submit-job | jq -r '.job_id')

    # Job status
    STATUS=$(curl -s ${HOST}/api/job-status/$JOB_ID | jq -r '.chunks | .[] | .status')

    # Wait up to 30 minutes to finish
    PAUSE="0"
    if [ "$STATUS" == "started" ] || [ "$STATUS" == "pending" ]
    then
        while [ $PAUSE -lt 300 ]
        do
            sleep 10
            STATUS=$(curl -s ${HOST}/api/job-status/$JOB_ID | jq -r '.chunks | .[] | .status')
            if [ "$STATUS" == "success" ] || [ "$STATUS" = "partial_success" ] || [ "$STATUS" == "error" ] || [ "$STATUS" == "timeout" ]
            then
                break
            fi
            PAUSE=$[$PAUSE+1]
        done
    fi

    # Facets search
    FACETS_SEARCH=$(curl -s ${HOST}/api/facets-search/$JOB_ID | jq '[.hitCount,.textSearchError]')
    HIT_COUNT=$(echo ${FACETS_SEARCH} |  jq '.[0]')
    SEARCH_ERROR=$(echo ${FACETS_SEARCH} |  jq '.[1]')

    # Send message in case of unexpected result
    if [ "$STATUS" != "success" ] || [ "$HIT_COUNT" -gt 0 ] && [ "$SEARCH_ERROR" != "false" ] || [ "$HIT_COUNT" == 0 ] && [ "$SEARCH_ERROR" != "true" ]
    then
        text="Ops! There is something wrong with the RNAcentral sequence search. Please check the links below: \n
        \n
        To check the status see: ${HOST}/api/job-status/$JOB_ID \n
        The job status is ${STATUS} (the expected status is success). \n
        \n
        To check the results see: ${HOST}/api/facets-search/$JOB_ID \n
        The job results are ${HIT_COUNT} and ${SEARCH_ERROR}."
        escapedText=$(echo ${text} | sed 's/"/\"/g' | sed "s/'/\'/g" )
        json="{\"text\": \"$escapedText\"}"
        curl -s -d "payload=$json" $WEBHOOK_URL
        exit
    fi
# No worries if it's not up, UptimeRobot will notify the team.
else
    echo "${HOST} is DOWN!"
fi

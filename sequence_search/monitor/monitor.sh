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
DATABASES_LIST=("gtrnadb" "snodb" "mirbase")
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

    # Wait up to 50 minutes to finish
    PAUSE=0
    if [ "$STATUS" == "started" ] || [ "$STATUS" == "pending" ]
    then
        while [ $PAUSE -lt 300 ]
        do
            sleep 10
            STATUS=$(curl -s ${HOST}/api/job-status/$JOB_ID | jq -r '.chunks | .[] | .status')
            if [ "$STATUS" == "success" ] || [ "$STATUS" == "partial_success" ]; then
                # Sequence search is working normal
                break
            elif [ "$STATUS" == "error" ] || [ "$STATUS" == "timeout" ]; then
                # It is good to check the search result in case of error
                text="Ops! There is something wrong with the RNAcentral sequence search. Please check the links below: \n
                \n
                The job status is ${STATUS}. See: ${HOST}/api/job-status/$JOB_ID \n
                \n
                To check the results see: ${HOST}/api/facets-search/$JOB_ID"
                escapedText=$(echo ${text} | sed 's/"/\"/g' | sed "s/'/\'/g" )
                json="{\"text\": \"$escapedText\"}"
                curl -s -d "payload=$json" $WEBHOOK_URL
                break
            fi
            PAUSE=$((PAUSE + 1))
        done

        # After 50 minutes, if status is still started or pending, send a message
        if [ "$STATUS" == "started" ] || [ "$STATUS" == "pending" ]; then
            # SQL queries to check the sequence search service
            CONSUMER_COUNT=$(ssh 192.168.0.6 "psql -U $USERNAME -d $DBNAME -t -c \"SELECT COUNT(ip) FROM consumer WHERE status='available';\"")
            JOB_COUNT=$(ssh 192.168.0.6 "psql -U $USERNAME -d $DBNAME -t -c \"SELECT COUNT(id) FROM jobs WHERE status='started' AND submitted BETWEEN NOW() - INTERVAL '8 HOURS' AND NOW();\"")

            # Trim whitespace
            CONSUMER_COUNT=$(echo $CONSUMER_COUNT | xargs)
            JOB_COUNT=$(echo $JOB_COUNT | xargs)

            text="A sequence search test has not been performed within a 50 minute period. There are currently $CONSUMER_COUNT consumers available and $JOB_COUNT jobs in the queue. \n
            \n
            When completed, the test search results will be available at: ${HOST}/api/facets-search/$JOB_ID"
            escapedText=$(echo ${text} | sed 's/"/\"/g' | sed "s/'/\'/g" )
            json="{\"text\": \"$escapedText\"}"
            curl -s -d "payload=$json" $WEBHOOK_URL
        fi
    fi

# No worries if it's not up, UptimeRobot will notify the team.
else
    echo "${HOST} is DOWN!"
fi

# Script to do a lot of queries and check the service. This script will submit a job and check its status.
# To do 5 searches, run: ./test_service.sh 5
#
# The output will look something like:
#   0: 9b1c63b6-fe6e-468f-90ac-0075a9933599 - successfully completed
#   1: 07f3e6f6-3be0-4b70-bd84-6f032353e346 - successfully completed
#   2: d9b18a2f-65fb-45be-90f8-d76af04525ad - successfully completed
#   3: 419e2783-43c3-4ccb-b282-40f4348329ce - successfully completed
#   4: ea23a5ef-17ca-44f3-80b6-76509af0c803 - successfully completed
#
# import HOST_TO_TEST
# -o allexport enables all following variable definitions to be exported.
# +o allexport disables this feature.
set -o allexport
source $PWD/.conf-file
set +o allexport

CONTENT_TYPE="Content-Type: application/json"
TOTAL=$1

# First check if the $HOST_TO_TEST is up
if curl -s --head  --request GET $HOST_TO_TEST | grep "200 OK" > /dev/null; then
    # Create an array to store job ids
    declare -a arr

    # Submit jobs
    # Each job runs a different sequence
    for ((i=1;i<=$TOTAL;i++)); do
        NEW_SEQUENCE=$(cat /dev/urandom | env LC_CTYPE=C tr -dc ACGTU | head -c 22)
        DATABASE_AND_QUERY_TEST="{\"databases\": [], \"query\": \"$NEW_SEQUENCE\"}"
        JOB_ID=$(curl -s -H "${CONTENT_TYPE}" -d "${DATABASE_AND_QUERY_TEST}" ${HOST_TO_TEST}/api/submit-job | jq -r '.job_id')
        arr=("${arr[@]}" $JOB_ID)
        sleep 0.1
    done

    # Now loop through the above array and check the status of the job
    for job in ${!arr[*]}
    do
        # Verify job status
        STATUS=$(curl -s ${HOST_TO_TEST}/api/job-status/${arr[$job]} | jq -r '.status')

        if [ "$STATUS" == "success" ]
        then
            printf "%4d: %s - successfully completed\n" $job ${arr[$job]}
        elif [ "$STATUS" == "started" ] || [ "$STATUS" == "pending" ]
        then
            # Wait some seconds
            PAUSE="0"
            while [ $PAUSE -lt 300 ]
            do
                sleep 10
                STATUS=$(curl -s ${HOST_TO_TEST}/api/job-status/${arr[$job]} | jq -r '.status')
                if [ "$STATUS" == "success" ]
                then
                    printf "%4d: %s - successfully completed\n" $job ${arr[$job]}
                    break
                elif [ "$STATUS" == "error" ] || [ "$STATUS" == "timeout" ]
                then
                    printf "%4d: %s - with error or timeout status\n" $job ${arr[$job]}
                    break
                fi
                PAUSE=$[$PAUSE+1]
            done
        else
            printf "%4d: %s - with unexpected result\n" $job ${arr[$job]}
        fi
    done
else
    echo "${HOST_TO_TEST} is DOWN!"
fi

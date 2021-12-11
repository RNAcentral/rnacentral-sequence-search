#!/bin/bash
# Script to change the status of the consumer that crashed.
# If we can't ping the consumer, we should change its status to avoid the producer from trying to send jobs to it.

# get variables
set -o allexport
source $PWD/.env
set +o allexport

# read IPs from file
cat consumers.txt | while read output
do
    # ping each consumer
    ping -c 1 "$output" > /dev/null

    # update the status of the consumer if it is unreachable
    if [ $? -ne 0 ]; then
        # check the current status
        status=(`psql -X -A -d $DB -U $USER -t -c "select status from consumer where ip='${output}'"`)

        # update and notify if necessary
        if [ ${status} != "error" ]; then
            psql -U $USER -d $DB -c "update consumer set status='error',job_chunk_id='unreachable' where ip='${output}'"
            curl -X POST -H 'Content-type: application/json' --data '{"text":"Unable to ping consumer '${output}'"}' $SLACK
        fi
    fi
done

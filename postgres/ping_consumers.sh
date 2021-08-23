#!/bin/bash
# Script to change the status of the consumer that crashed.
# If we can't ping the consumer, we should change its status to avoid the producer from trying to send jobs to it.

dbname="producer"
username="docker"

# read IPs from file
cat consumers.txt | while read output
do
    # ping each consumer
    ping -c 1 "$output" > /dev/null

    # update the status of the consumer if it is unreachable
    if [ $? -ne 0 ]; then
        # check the current status
        status=(`psql -X -A -d $dbname -U $username -t -c "select status from consumer where ip='${output}'"`)

        # update if necessary
        if [ ${status} != "error" ]; then
            psql -U $username -d $dbname -c "update consumer set status='error',job_chunk_id='unreachable' where ip='${output}'"
        fi
    fi
done

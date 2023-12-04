#!/bin/bash
# Script to ping consumers that crashed.
# Send message if VM remains unreachable or change status if running

# get variables
set -o allexport
source $PWD/.env
set +o allexport

# this script needs to be run after ping_consumers.sh
sleep 10

ips=( $(psql -X -A -d producer -U docker -t -c "select ip from consumer where status='error'") )

for ip in "${ips[@]}"
do
    ping -c 1 "$ip" > /dev/null

    if [ $? -ne 0 ]; then
        # VM unreachable - send a message on slack
        curl -X POST -H 'Content-type: application/json' --data '{"text":"Unable to ping consumer '${ip}'"}' $SLACK

        # change status to avoid sending too many messages
        # this will have to be fixed manually
        psql -U $USER -d $DB -c "update consumer set status='unreachable',job_chunk_id='unreachable' where ip='${ip}'"
    else
        # VM looks ok - check the current status
        status=(`psql -X -A -d $DB -U $USER -t -c "select status from consumer where ip='${ip}'"`)

        # make the vm available again
        if [ ${status} == "error" ]; then
            psql -U $USER -d $DB -c "update consumer set status='available',job_chunk_id='' where ip='${ip}'"
        fi
    fi
done
#!/bin/bash
# Script to send a message if a VM is unreachable


# get variables
set -o allexport
source $PWD/.env
set +o allexport

# array of IPs
declare -a arr=(192.168.0.5 192.168.0.6 192.168.0.7)

while :
do
    index=0

    # loop through the above array
    for ip in "${arr[@]}"; do
        # ping each VM
        ping -c 1 "$ip" > /dev/null

        # send message if VM is unreachable
        if [ $? -ne 0 ]; then
            vm=""
            if [ "$ip" = "192.168.0.5" ]; then
                vm="producer"
            elif [ "$ip" = "192.168.0.6" ]; then
                vm="database"
            elif [ "$ip" = "192.168.0.7" ]; then
                vm="nfs-server"
            fi
            curl -X POST -H 'Content-type: application/json' --data '{"text":"Critical Failure! Unable to ping VM '${ip}' - ('${vm}')"}' $SLACK
            unset "arr[$index]"
            arr=( "${arr[@]}" )
        fi
        # increment index
        (( index++ )) || true
    done

    # run a new test in 30 seconds or stop if the array is empty
    if [[ -n ${arr} ]]; then
        sleep 30
    else
        break
    fi
done
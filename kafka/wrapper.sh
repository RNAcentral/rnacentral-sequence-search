#!/bin/bash

# Start zookeeper server
nohup /usr/local/bin/kafka_2.11-1.1.0/bin/zookeeper-server-start.sh /usr/local/bin/kafka_2.11-1.1.0/config/zookeeper.properties &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start zookeeper server: $status"
  exit $status
fi

# Start kafka server
nohup /usr/local/bin/kafka_2.11-1.1.0/bin/kafka-server-start.sh /usr/local/bin/kafka_2.11-1.1.0/config/server.properties &
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start kafka server: $status"
  exit $status
fi

# Naive check runs checks once a minute to see if either of the processes exited.
# This illustrates part of the heavy lifting you need to do if you want to run
# more than one service in a container. The container exits with an error
# if it detects that either of the processes has exited.
# Otherwise it loops forever, waking up every 60 seconds

while sleep 30; do
  ps aux |grep zookeeper |grep -q -v grep
  PROCESS_1_STATUS=$?
  ps aux |grep kafka |grep -q -v grep
  PROCESS_2_STATUS=$?
  # If the greps above find anything, they exit with 0 status
  # If they are not both 0, then something is wrong
  if [ $PROCESS_1_STATUS -ne 0 -o $PROCESS_2_STATUS -ne 0 ]; then
    echo "One of the processes has already exited."
    exit 1
  fi
done

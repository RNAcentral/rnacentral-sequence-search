#!/bin/bash

TODAY=$(date +"%Y%m%d")
TIME=$(date +"%T")
REMOVE=$(date +"%Y%m%d_%H" -d "5 days ago")

echo "Removing old files"
find /backup -name "producer_${REMOVE}*" -type f -exec rm -f {} \;

echo "Starting a temporary backup"
pg_dump producer -U docker > /backup/producer_tmp.dump

echo "Create a temporary database"
createdb -U docker -T template0 producer_tmp
psql -U docker producer_tmp -f /backup/producer_tmp.dump

echo "Update the consumer column of the job_chunks table with null values"
psql -U docker producer_tmp -c 'update job_chunks set consumer = NULL;'

echo "Backup the temporary database"
pg_dump -Fc producer_tmp -U docker -T 'consumer' > /backup/producer_${TODAY}_${TIME}.dump

echo "Remove the temporary database"
dropdb -U docker producer_tmp
rm /backup/producer_tmp.dump
#!/bin/bash

TODAY=$(date +"%Y%m%d")
TIME=$(date +"%T")
REMOVE=$(date +"%Y%m%d_%H" -d "5 days ago")

echo "Removing old files"
find /backup -name "producer_${REMOVE}*" -type f -exec rm -f {} \;

echo "Backup the database"
pg_dump -Fc producer -U docker > /backup/producer_${TODAY}_${TIME}.dump

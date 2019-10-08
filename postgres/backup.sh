#!/bin/bash

TODAY=$(date +"%Y%m%d")
TIME=$(date +"%T")
REMOVE=$(date +"%Y%m%d_%H" -d "5 days ago")

echo "Removing old files"
find /backup -name "producer_${REMOVE}*" -type f -exec rm -f {} \;

echo "Starting backup"
pg_dump -Fc producer -U postgres > /backup/producer_${TODAY}_${TIME}.dump

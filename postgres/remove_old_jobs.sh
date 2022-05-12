#!/bin/bash
# Script to remove searches performed more than 7 days ago

dbname="producer"
username="docker"

old_jobs=(`psql -X -A -d $dbname -U $username -t -c "SELECT id FROM jobs WHERE submitted < NOW() - INTERVAL '7 days';"`)

for job in ${!old_jobs[*]}
do
  # delete jobs
  psql -U $username -d $dbname -c "DELETE FROM jobs WHERE id='${old_jobs[$job]}'"
done

#!/bin/bash
# Script to delete jobs that crashed. Sometimes the job is given as completed but some chunks are not executed.

dbname="producer"
username="docker"

possible_failed_jobs=(`psql -X -A -d $dbname -U $username -t -c "SELECT DISTINCT job_id FROM job_chunks WHERE status='created'"`)

for job in ${!possible_failed_jobs[*]}
do
  job_status=`psql -X -A -d $dbname -U $username -t -c "SELECT status FROM jobs WHERE id='${possible_failed_jobs[$job]}'"`
  if [ "$job_status" == "success" ] || [ "$job_status" == "partial_success" ]
  then
    # delete job
    psql -U $username -d $dbname -c "DELETE FROM jobs WHERE id='${possible_failed_jobs[$job]}'"
  fi
done

# It is possible to have a job that crashed with the status started, but this should be handled with care
#started_jobs=(`psql -X -A -d $dbname -U $username -t -c "SELECT id FROM jobs WHERE status IS DISTINCT FROM 'success' AND status IS DISTINCT FROM 'partial_success'"`)

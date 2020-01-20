#!/bin/bash
# Script to delete jobs that crashed. Sometimes the job is given as completed but some chunks are not executed.

dbname="producer"
username="docker"

possible_failed_jobs=(`psql -X -A -d $dbname -U $username -t -c "SELECT DISTINCT job_id from job_chunks where status='created'"`)

for job in ${!possible_failed_jobs[*]}
do
  job_status=`psql -X -A -d $dbname -U $username -t -c "SELECT status from jobs where id='${possible_failed_jobs[$job]}'"`
  if [ "$job_status" == "success" ] || [ "$job_status" == "partial_success" ]
  then
    # delete infernal entries
    psql -U $username -d $dbname -c "delete from infernal_result where infernal_job_id in (select id from infernal_job where job_id='${possible_failed_jobs[$job]}')"
    psql -U $username -d $dbname -c "delete from infernal_job where job_id='${possible_failed_jobs[$job]}'"

    # delete job and job_chunks entries
    psql -U $username -d $dbname -c "delete from job_chunk_results where job_chunk_id in (select id from job_chunks where job_id='${possible_failed_jobs[$job]}')"
    psql -U $username -d $dbname -c "delete from job_chunks where job_id='${possible_failed_jobs[$job]}'"
    psql -U $username -d $dbname -c "delete from jobs where id='${possible_failed_jobs[$job]}'"
  fi
done

# It is possible to have a job that crashed with the status started, but this should be handled with care
#started_jobs=(`psql -X -A -d $dbname -U $username -t -c "SELECT id FROM jobs WHERE status IS DISTINCT FROM 'success' AND status IS DISTINCT FROM 'partial_success'"`)

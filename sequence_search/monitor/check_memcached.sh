#!/bin/bash
# Script to check if memcached is running.
#
# I've seen some "Out of Memory Killer" messages.
# The monitor VM probably needs more memory, but
# for now I'm going to use this script to restart
# memcached in case the kernel kills its process.

PID=(`ps -ef | grep -v grep | grep memcached | awk '{print $2}'`)

if [ -z "$PID" ]
then
  sudo service memcached restart
fi

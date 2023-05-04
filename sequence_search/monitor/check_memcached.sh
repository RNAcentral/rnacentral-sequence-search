#!/bin/bash
# Script to check if memcached is running.
#
# I've seen some "Out of Memory Killer" messages.
# The monitor VM probably needs more memory, but
# for now I'm going to use this script to restart
# memcached in case the kernel kills its process.

systemctl is-active --quiet memcached
STATUS=$?  # returns 0 if running

if [[ "$STATUS" -ne "0" ]]; then
  sudo service memcached start
fi

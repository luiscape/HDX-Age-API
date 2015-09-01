#!/bin/bash

#
# Creating logs directory.
#
mkdir logs

#
# Start Redis worker
# as daemon.
#
source venv/bin/activate
supervisord
supervisorctl status

#
# Inspect the Python running processes.
#
# ps aux | grep python
# killall python

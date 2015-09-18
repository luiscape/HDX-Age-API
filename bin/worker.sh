#!/bin/bash

#
# Start Redis worker
# as daemon.
#
source venv/bin/activate
screen -S worker -d -m -L python worker.py
screen -ls

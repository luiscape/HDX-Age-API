#!/bin/bash

#
# Start Redis worker
# as daemon.
#
source venv/bin/activate
screen -S worker -d -m python worker.py
screen -ls

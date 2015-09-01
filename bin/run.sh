#!/bin/bash

#
# Start Redis worker as daemon.
#
make worker

#
# Running app with
# SQLite database.
#
source venv/bin/activate
manage serve

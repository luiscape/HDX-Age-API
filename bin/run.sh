#!/bin/bash

#
# Start Redis worker as daemon.
#
make worker

#
# Create database.
#
mkdir data
manage -m Docker createdb

#
# Running app with
# SQLite database.
#
source venv/bin/activate
manage -m Docker serve

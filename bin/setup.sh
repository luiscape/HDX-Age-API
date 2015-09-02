#!/bin/bash

#
# Setup Python virtual environment
# and install dependencies.
#
virtualenv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
easy_install --upgrade requests
pip install requests[security]

#
# Create database.
#
mkdir data
python manage.py createdb

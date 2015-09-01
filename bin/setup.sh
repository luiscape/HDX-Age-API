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

#
# Installing supervisord.
#
pip install supervisor --pre
easy_install --upgrade meld3


#
# Create database.
#
mkdir data
python manage.py createdb

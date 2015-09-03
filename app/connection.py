# -*- coding: utf-8 -*-
"""
    app.connection
    ~~~~~~~~~~~~~~

    Provides the redis connection
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import redis
from os import environ, getenv

#
# Check for Heroku environment variables
#
if environ.get('REDISTOGO_URL'):
    redis_url = environ.get('REDISTOGO_URL')

#
# If not present, use Docker environment variable instead.
#
else:
    redis_conn = getenv('REDIS_PORT_6379_TCP_ADDR', 'localhost')
    redis_url = 'redis://' + redis_conn + ':6379'

#
# Connect to Redis.
#
conn = redis.from_url(redis_url)

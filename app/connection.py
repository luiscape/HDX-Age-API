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


# Try Heroku environment variable.
# If not present, use Docker environment variable.
redis_host = getenv('REDIS_PORT_6379_TCP_ADDR', 'localhost')
redis_url = environ.get('REDISTOGO_URL', 'redis://%s:6379' % redis_host)

# Create Redis connection
conn = redis.from_url(redis_url)

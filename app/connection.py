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

from os import getenv

redis_conn = 'REDIS_PORT_6379_TCP_ADDR' + ':' + 'PORT_6379_TCP_PORT'
redis_url = getenv(redis_conn, 'redis://localhost:6379')
conn = redis.from_url(redis_url)

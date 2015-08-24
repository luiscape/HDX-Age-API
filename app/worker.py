# -*- coding: utf-8 -*-
"""
    app.worker
    ~~~~~~~~~~

    Provides the rq worker
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import os
import urlparse
from redis import Redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

redis_url = (os.getenv('REDISTOGO_URL') or 'http://localhost:6379')
urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

with Connection(conn):
    worker = Worker(map(Queue, listen))
    worker.work()

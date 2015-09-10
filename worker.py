# -*- coding: utf-8 -*-
"""
    app.worker
    ~~~~~~~~~~

    Provides the rq worker
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from app.connection import conn
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()

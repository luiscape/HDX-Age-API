# -*- coding: utf-8 -*-
"""
    app.views
    ~~~~~~~~~

    Provides additional api endpoints
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from flask import Blueprint, request
from rq import Queue
from loremipsum import get_sentences

from config import Config as c
from app import cache
from .utils import jsonify, make_cache_key
from app.connection import conn

q = Queue(connection=conn)
blueprint = Blueprint('blueprint', __name__)
cache_timeout = 60 * 60 * 1  # hours (in seconds)


def expensive_func(x):
    return pow(x, 100)


# endpoints
@blueprint.route('%s/lorem/' % c.API_URL_PREFIX)
@cache.cached(timeout=cache_timeout, key_prefix=make_cache_key)
def lorem():
    kwargs = {'result': get_sentences(1)[0]}
    return jsonify(**kwargs)


@blueprint.route('%s/expensive/' % c.API_URL_PREFIX)
def expensive():
    job = q.enqueue(expensive_func, 10)
    kwargs = {'job_id': job.id}
    return jsonify(**kwargs)


@blueprint.route('%s/result/<jid>/' % c.API_URL_PREFIX)
def result(jid):
    job = q.fetch_job(jid)
    kwargs = {
        'job_status': job.get_status(), 'job_id': job.id, 'result': job.result}
    return jsonify(**kwargs)


@blueprint.route('%s/double/<num>/' % c.API_URL_PREFIX)
@cache.memoize(timeout=cache_timeout)
def double(num):
    kwargs = {'result': 2 * num}
    return jsonify(**kwargs)


@blueprint.route('%s/delete/<base>/' % c.API_URL_PREFIX)
def delete(base):
    url = request.url.replace('delete/', '')
    cache.delete(url)
    kwargs = {'result': "Key: %s deleted" % url}
    return jsonify(**kwargs)


@blueprint.route('%s/reset/' % c.API_URL_PREFIX)
def reset():
    cache.clear()
    return jsonify(result='Caches reset')

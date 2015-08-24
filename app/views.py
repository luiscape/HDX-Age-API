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
from redis import Redis
from rq import Queue
from loremipsum import get_sentences

from config import Config as c
from app import cache
from .utils import jsonify, make_cache_key

q = Queue('high', connection=Redis())
blueprint = Blueprint('blueprint', __name__)
cache_timeout = 60 * 60 * 1  # hours (in seconds)


# endpoints
@blueprint.route('%s/lorem/' % c.API_URL_PREFIX)
@cache.cached(timeout=cache_timeout, key_prefix=make_cache_key)
def lorem():
    kwargs = {'result': get_sentences(1)[0]}
    return jsonify(**kwargs)


@blueprint.route('%s/expensive/' % c.API_URL_PREFIX)
@cache.cached(timeout=cache_timeout)
def expensive():
    expensive_func = lambda x: pow(x, 100)
    job = q.enqueue(expensive_func, 10)
    kwargs = {'status': job.get_status(), 'id': job.id, 'result': job.result}
    return jsonify(**kwargs)


@blueprint.route('%s/status/<jid>/' % c.API_URL_PREFIX)
def status(jid):
    job = q.fetch_job(jid)
    kwargs = {'status': job.get_status(), 'id': job.id, 'result': job.result}
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

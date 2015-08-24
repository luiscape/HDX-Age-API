# -*- coding: utf-8 -*-
"""
    app.views
    ~~~~~~~~~

    Provides additional api endpoints
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from pprint import pprint
from flask import Blueprint, make_response, request
from json import dumps
from sqlalchemy import distinct
from redis import Redis
from rq import Queue

from config import Config as c
from app import cache
from .utils import jsonify, make_cache_key

q = Queue('high', connection=Redis())
blueprint = Blueprint('blueprint', __name__)
cache_timeout = 60 * 60 * 1  # hours (in seconds)


# endpoints
@blueprint.route('/api/lorum/')
@blueprint.route('%s/lorum/' % c.API_URL_PREFIX)
@cache.cached(timeout=cache_timeout, key_prefix=make_cache_key)
def lorum():
    kwargs = {'objects': get_sentences(1)[0]}
    return jsonify(kwargs)


@blueprint.route('/api/expensive/')
@blueprint.route('%s/expensive/' % c.API_URL_PREFIX)
@cache.cached(timeout=cache_timeout)
def expensive():
    job = q.enqueue(expensive_func, q_kwargs)
    kwargs = {'objects': job.status}
    return jsonify(kwargs)


@blueprint.route('/api/double/<num>/')
@blueprint.route('%s/double/<num>/' % c.API_URL_PREFIX)
@cache.memoize(timeout=cache_timeout)
def double(num):
    kwargs = {'objects': 2 * num}
    return jsonify(kwargs)


@blueprint.route('/api/delete/<base>/')
@blueprint.route('%s/delete/<base>/' % c.API_URL_PREFIX)
def delete(base):
    url = request.url.replace('delete/', '')
    cache.delete(url)
    kwargs = {'objects': "Key: %s deleted" % url}
    return jsonify(objects=kwargs)


@blueprint.route('/api/reset/')
@blueprint.route('%s/reset/' % c.API_URL_PREFIX)
def reset():
    cache.clear()
    kwargs = {'objects': 'Caches reset'}
    return jsonify(objects=kwargs)

# -*- coding: utf-8 -*-
"""
    app.views
    ~~~~~~~~~

    Provides additional API endpoints
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import itertools as it

from datetime import datetime as dt
from bisect import bisect
from operator import itemgetter
from functools import partial
from random import choice

from flask import Blueprint, request
from rq import Queue
from loremipsum import get_sentences
from ckanutils import CKAN
from tabutils import process as tup

from config import Config as c
from app import cache, __version__, db
from app.utils import jsonify, make_cache_key, parse, count_words_at_url
from app.connection import conn
from app.models import Age

q = Queue(connection=conn)
blueprint = Blueprint('blueprint', __name__)
cache_timeout = 60 * 60 * 1  # hours (in seconds)

statuses = ['Up-to-date', 'Due for update', 'Overdue', 'Delinquent']

breakpoints = {
    0: [0, 0, 0],
    1: [1, 2, 3],
    7: [7, 14, 21],
    14: [14, 21, 28],
    30: [30, 44, 60],
    90: [90, 120, 150],
    180: [180, 210, 240],
    365: [365, 425, 455],
}

categories = {
    0: 'Archived',
    1: 'Every day',
    7: 'Every week',
    14: 'Every two weeks',
    30: 'Every month',
    90: 'Every three months',
    180: 'Every six months',
    365: 'Every year',
}


def gen_data(ckan, pids):
    for pid in pids:
        package = ckan.package_show(id=pid)
        # frequency = int(package['frequency'])
        frequency = choice(breakpoints.keys())
        breaks = breakpoints.get(frequency)
        resources = package['resources']
        last_updated = max(it.imap(ckan.get_update_date, resources))
        age = dt.now() - last_updated

        if breaks:
            status = statuses[bisect(breaks, age.days)]
        else:
            status = 'Invalid frequency. Status could not be determined.'

        data = {
            'dataset_id': pid,
            'dataset_name': package['name'],
            'last_updated': last_updated,
            'needs_update': status in statuses[1:],
            'status': status,
            'age': age.days,
            'frequency': frequency,
            'frequency_category': categories.get(frequency, 'N/A')
        }

        yield data


def _update(ckan, chunk_size, pid):
    if pid:
        pids = [pid]
    else:
        org_show = partial(ckan.organization_show, include_datasets=True)
        org_ids = it.imap(itemgetter('id'), ckan.get_all_orgs())
        orgs = (org_show(id=org_id) for org_id in org_ids)
        package_lists = it.imap(itemgetter('packages'), orgs)
        pid_getter = partial(map, itemgetter('id'))
        pids = it.chain.from_iterable(it.imap(pid_getter, package_lists))

    data = gen_data(ckan, pids)
    rows = 0

    for records in tup.chunk(data, chunk_size):
        result = db.engine.execute(Age.__table__.insert(), records)
        rows += result.rowcount

    return rows


@blueprint.route('%s/status/' % c.API_URL_PREFIX)
@cache.cached(timeout=cache_timeout, key_prefix=make_cache_key)
def status(**kwargs):
    ckan = CKAN(**kwargs)

    resp = {
        'online': True,
        'message': 'Service for checking and updating HDX dataset ages.',
        'CKAN_instance': ckan.address,
        'version': __version__,
        'repository': 'https://github.com/reubano/HDX-Age-API'
    }

    return jsonify(**resp)


def expensive_func(x):
    return pow(x, 100)


@blueprint.route('%s/lorem/' % c.API_URL_PREFIX)
@cache.cached(timeout=cache_timeout, key_prefix=make_cache_key)
def lorem():
    resp = {'result': get_sentences(1)[0]}
    return jsonify(**resp)


@blueprint.route('%s/expensive/' % c.API_URL_PREFIX)
def expensive():
    job = q.enqueue(expensive_func, 10)
    resp = {'job_id': job.id}
    return jsonify(**resp)


@blueprint.route('%s/update/' % c.API_URL_PREFIX)
@blueprint.route('%s/update/<pid>/' % c.API_URL_PREFIX)
def update(pid=None):
    kwargs = {k: parse(v) for k, v in request.args.to_dict().items()}
    sync = kwargs.pop('sync', False)
    chunk_size = int(kwargs.pop('chunk_size', 5000))

    if sync:
        resp = {'result': count_words_at_url(pid, chunk_size)}
    else:
        job = q.enqueue(count_words_at_url, 'http://nvie.com')
        result_url = 'http://%s:%s%s/result/%s/' % (
            c.HOST, c.PORT, c.API_URL_PREFIX, job.id)

        resp = {
            'job_id': job.id,
            'job_status': job.get_status(),
            'rows_updated': job.result,
            'result_url': result_url}

    return jsonify(**resp)


@blueprint.route('%s/result/<jid>/' % c.API_URL_PREFIX)
def result(jid):
    job = q.fetch_job(jid)

    resp = {
        'job_id': job.id,
        'job_status': job.get_status(),
        'rows_updated': job.result}

    return jsonify(**resp)


@blueprint.route('%s/double/<num>/' % c.API_URL_PREFIX)
@cache.memoize(timeout=cache_timeout)
def double(num):
    resp = {'result': 2 * num}
    return jsonify(**resp)


@blueprint.route('%s/delete/<base>/' % c.API_URL_PREFIX)
def delete(base):
    url = request.url.replace('delete/', '')
    cache.delete(url)
    return jsonify(result='Key: %s deleted' % url)


@blueprint.route('%s/reset/' % c.API_URL_PREFIX)
def reset():
    cache.clear()
    return jsonify(result='Caches reset')

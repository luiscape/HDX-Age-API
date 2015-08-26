# -*- coding: utf-8 -*-
"""
    app.utils
    ~~~~~~~~~

    Provides misc utility functions
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import itertools as it
import requests

from json import dumps, loads, JSONEncoder
from ast import literal_eval
from datetime import datetime as dt
from bisect import bisect
from operator import itemgetter
from functools import partial

from flask import make_response, request
from ckanutils import CKAN
from tabutils import process as tup

encoding = 'utf8'
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


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if set(['quantize', 'year']).intersection(dir(obj)):
            return str(obj)
        elif set(['next', 'union']).intersection(dir(obj)):
            return list(obj)
        return JSONEncoder.default(self, obj)


def jsonify(status=200, indent=2, sort_keys=True, **kwargs):
    options = {'indent': indent, 'sort_keys': sort_keys, 'ensure_ascii': False}
    response = make_response(dumps(kwargs, cls=CustomEncoder, **options))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.status_code = status
    return response


def make_cache_key(*args, **kwargs):
    return request.url


def parse(string):
    string = string.encode(encoding)

    if string.lower() in ('true', 'false'):
        return loads(string.lower())
    else:
        try:
            return literal_eval(string)
        except (ValueError, SyntaxError):
            return string


def gen_data(ckan, pids):
    for pid in pids:
        package = ckan.package_show(id=pid)
        resources = package['resources']

        if not resources:
            continue

        downloads = sum(int(r['tracking_summary']['total']) for r in resources)
        # frequency = choice(breakpoints.keys())  # Mocking frequency
        frequency = package.get('data_update_frequency')
        breaks = breakpoints.get(frequency)
        last_updated = max(it.imap(ckan.get_update_date, resources))
        age = dt.now() - last_updated

        if breaks:
            status = statuses[bisect(breaks, age.days)]
        else:
            status = 'Invalid frequency. Status could not be determined.'

        data = {
            'dataset_id': package['id'],
            'dataset_name': package['name'],
            'dataset_title': package['title'],
            'last_updated': last_updated.isoformat(),
            'needs_update': status in statuses[1:],
            'status': status,
            'age': int(age.days),
            'frequency': frequency,
            'frequency_category': categories.get(frequency),
            'downloads': downloads
        }

        yield data

def_chunk_size = 1
def_max_records = 3


def update(endpoint, **kwargs):
    pid = kwargs.pop('pid', None)
    chunk_size = int(kwargs.pop('chunk_size', 0)) or def_chunk_size
    max_records = int(kwargs.pop('max_records', 0)) or def_max_records
    rows = 0

    ckan = CKAN(**kwargs)

    if pid:
        pids = [pid]
    else:
        org_show = partial(ckan.organization_show, include_datasets=True)
        orgs_basic = ckan.organization_list(permission='read')
        org_ids = it.imap(itemgetter('id'), orgs_basic)
        orgs = (org_show(id=org_id) for org_id in org_ids)
        package_lists = it.imap(itemgetter('packages'), orgs)
        pid_getter = partial(map, itemgetter('id'))
        pids = it.chain.from_iterable(it.imap(pid_getter, package_lists))

    data = gen_data(ckan, pids)
    headers = {'Content-Type': 'application/json'}
    safe = []
    post = partial(requests.post, endpoint, headers=headers)

    for records in tup.chunk(data, chunk_size):
        count = len(records)
        safe.extend(records)
        [post(data=dumps(record)) for record in records]

        rows += count

        if rows >= max_records:
            break

    return rows


def count_letters(word=''):
    return len(word)


def expensive_func(x):
    return x * 10

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
from random import choice
from timeit import default_timer as timer
from dateutil.relativedelta import relativedelta

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
    """ Creates a jsonified response. Necessary because the default
    flask.jsonify doesn't correctly handle sets, dates, or iterators

    Args:
        status (int): The status code (default: 200).
        indent (int): Number of spaces to indent (default: 2).
        sort_keys (bool): Sort response dict by keys (default: True).
        kwargs (dict): The response to jsonify.

    Returns:
        (obj): Flask response
    """
    options = {'indent': indent, 'sort_keys': sort_keys, 'ensure_ascii': False}
    response = make_response(dumps(kwargs, cls=CustomEncoder, **options))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.status_code = status
    return response


def fmt_elapsed(elapsed):
    """ Generates a human readable representation of elapsed time.

    Args:
        elapsed (float): Number of elapsed seconds.

    Yields:
        (str): Elapsed time value and unit

    Examples:
        >>> formatted = fmt_elapsed(1000)
        >>> formatted.next()
        u'16 minutes'
        >>> formatted.next()
        u'40 seconds'
    """
    # http://stackoverflow.com/a/11157649/408556
    # http://stackoverflow.com/a/25823885/408556
    attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
    delta = relativedelta(seconds=elapsed)

    for attr in attrs:
        value = getattr(delta, attr)

        if value:
            yield '%d %s' % (value, attr if value > 1 else attr[:-1])


def patch_or_post(endpoint, record):
    """ Updates a record via it's REST API if it exist, otherwise creates it.

    Args:
        endpoint (str): The api resource url.
        record (dict): The record data.

    Returns:
        (obj): requests response
    """
    url = '%s/%s' % (endpoint, record['dataset_id'])
    headers = {'Content-Type': 'application/json'}
    data = dumps(record)

    if requests.head(url, headers=headers).ok:
        r = requests.patch(url, data=data, headers=headers)
    else:
        r = requests.post(endpoint, data=data, headers=headers)

    return r


def make_cache_key(*args, **kwargs):
    """ Creates a memcache key for a url and its query parameters

    Returns:
        (obj): Flask request url
    """
    return request.url


def parse(string):
    """ Parses a string into an equivalent Python object

    Args:
        string (str): The string to parse

    Returns:
        (obj): equivalent Python object

    Examples:
        >>> parse('True')
        True
        >>> parse('{"key": "value"}')
        {'key': 'value'}
    """
    string = string.encode(encoding)

    if string.lower() in {'true', 'false'}:
        return loads(string.lower())
    else:
        try:
            return literal_eval(string)
        except (ValueError, SyntaxError):
            return string


def gen_data(ckan, pids, mock_freq=False):
    """ Generates data about a ckan package.

    Args:
        ckan (obj): A `CKAN` instance.
        pids (List[str]): List of package ids.
        mock_freq (bool): Mock the `frequency` field (default: False)?

    Yields:
        (dict): The package data.
    """
    for pid in pids:
        package = ckan.package_show(id=pid)
        resources = package['resources']

        if not resources:
            continue

        downloads = sum(int(r['tracking_summary']['total']) for r in resources)

        if mock_freq:
            frequency = choice(breakpoints.keys())
        else:
            frequency = int(package.get('data_update_frequency'))

        breaks = breakpoints.get(frequency)
        last_updated = max(it.imap(ckan.get_update_date, resources))
        age = dt.now() - last_updated

        if breaks:
            status = statuses[bisect(breaks, age.days)]
        else:
            status = 'Invalid frequency'

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


def update(endpoint, **kwargs):
    """ Updates the database

    Args:
        endpoint (str): The api resource url.
        kwargs (dict): passed to CKAN constructor.

    Kwargs:
        chunk_size (int): Number of rows to process at a time (default: All).
        row_limit (int): Total number of rows to process (default: All).
        err_limit (int): Number of errors to encounter before failing
            (default: Inf).

    Returns:
        (dict): Update details
    """
    start = timer()
    pid = kwargs.pop('pid', None)
    chunk_size = kwargs.pop('chunk_size', 0)
    row_limit = kwargs.pop('row_limit', None)
    err_limit = kwargs.pop('err_limit', None)

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

    data = gen_data(ckan, pids, kwargs.get('mock_freq'))
    errors = {}

    for records in tup.chunk(data, min(row_limit or 'inf', chunk_size)):
        rs = map(partial(patch_or_post, endpoint), records)
        rows += len(filter(lambda r: r.ok, rs))
        ids = map(itemgetter('dataset_id'), records)
        errors.update(dict((k, r.json()) for k, r in zip(ids, rs) if not r.ok))

        if row_limit and rows >= row_limit:
            break

        if err_limit and len(errors) >= err_limit:
            raise Exception(errors)

    elapsed_time = ' ,'.join(fmt_elapsed(timer() - start))
    return {'rows_added': rows, 'errors': errors, 'elapsed_time': elapsed_time}

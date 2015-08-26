# -*- coding: utf-8 -*-
"""
    app.utils
    ~~~~~~~~~

    Provides misc utility functions
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from json import dumps, loads, JSONEncoder
from ast import literal_eval

from flask import make_response, request
from ckanutils import CKAN

encoding = 'utf8'


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


def do_update(pid, chunk_size):
    return _update(CKAN(**kwargs), chunk_size, pid)


def count_words_at_url(url):
    import requests
    r = requests.get(url)
    return len(r.text.split())

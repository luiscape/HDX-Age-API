# -*- coding: utf-8 -*-
"""
    tests
    ~~~~~

    Provides application unit tests
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from functools import partial
from flask.json import loads, dumps

from app import create_app

jsonx = None
client = None
base = None
app = None


def get_globals():
    global app
    global client

    return app, client


def setup_package():
    """database context creation"""
    global initialized
    global app
    global client
    global jsonx
    global base

    app = create_app(config_mode='Test')
    endpoint = app.config['API_URL_PREFIX']
    base = '%s/' % endpoint if endpoint else ''
    client = app.test_client()
    jsonx = app.test_request_context()
    jsonx.push()
    initialized = True

    print('Test Package Setup\n')


def teardown_package():
    """database context removal"""
    global initialized
    global jsonx

    jsonx.pop()
    initialized = False

    print('Test Package Teardown\n')


class APIHelper:
    global client
    global base

    json = 'application/json'

    def get(self, resource, id=None, query=None):
        # returns status_code 200
        url = '%s%s/' % (base, resource)
        url += '%s/' % id if id else ''
        get = partial(client.get, url, content_type=self.json)
        return get(q=query) if query else get()

    def delete(self, resource, id):
        # returns status_code 204
        url = '%s%s/%s/' % (base, resource, id)
        return client.delete(url, content_type=self.json)

    def post(self, data, resource):
        # returns status_code 201
        url = '%s%s/' % (base, resource)
        return client.post(url, data=dumps(data), content_type=self.json)

    def patch(self, data, resource, id=None, query=None):
        # returns status_code 200 or 201
        url = '%s%s/' % (base, resource)
        url += '%s/' % id if id else ''
        patch = partial(
            client.patch, url, data=dumps(data), content_type=self.json)

        return patch(q=query) if query else patch()

    def get_json(self, r):
        return loads(r.data)

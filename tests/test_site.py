# -*- coding: utf-8 -*-
"""
    tests.test_site
    ~~~~~~~~~~~~~~~

    Provides unit tests for the website.
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import nose.tools as nt
from datetime import datetime

from . import APIHelper, get_globals
from app import db
from app.utils import jsonify, make_cache_key

tables = None
client = None


def setup_module():
    """site initialization"""
    global initialized
    global tables
    global client

    app, client = get_globals()
    tables = [k[4:] for k in app.blueprints.keys() if k.endswith('api0')]
    db.create_all()
    initialized = True
    print('Site Module Setup\n')


class TestAPI(APIHelper):
    """Unit tests for the API"""
    global client

    def __init__(self):
        self.cls_initialized = False

    def test_home(self):
        r = client.get('/')
        nt.assert_equal(r.status_code, 200)

    def test_status(self):
        r = self.get('lorem')
        result = self.get_json(r)['result']
        nt.assert_true(len(result) > 0)


class TestUtils(APIHelper):
    """Unit tests for the utils module"""
    def __init__(self):
        self.cls_initialized = False

    def test_make_cache_key(self):
        nt.assert_equal(make_cache_key(), 'http://localhost/')

    def test_jsonify(self):
        # test string
        r = jsonify(result='Hello')
        result = self.get_json(r)['result']
        nt.assert_equal(result, 'Hello')

        # test iterator
        r = jsonify(result=iter(['Hello', 'World']))
        result = self.get_json(r)['result']
        nt.assert_equal(result, ['Hello', 'World'])

        # test date
        r = jsonify(result=datetime(2015, 1, 15))
        result = self.get_json(r)['result']
        nt.assert_equal(result, u'2015-01-15 00:00:00')

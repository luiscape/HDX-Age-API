# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~

    Provides the flask configuration
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from os import path as p, getenv

# module vars
_basedir = p.dirname(__file__)

# configurable vars
__USER__ = 'reubano'
__APP_NAME__ = 'HDX-Age-API'
__YOUR_NAME__ = 'Reuben Cummings'
__YOUR_EMAIL__ = 'reubano@gmail.com'
__YOUR_WEBSITE__ = 'http://%s.github.io' % __USER__


# configuration
class Config(object):
    ###########################################################################
    # WARNING: if running on a a staging server, you MUST set the 'STAGE' env
    # heroku config:set STAGE=true --remote staging
    ###########################################################################
    stage = getenv('STAGE', False)
    end = '-stage' if stage else ''

    ADMINS = frozenset([__YOUR_EMAIL__])
    HOST = '127.0.0.1'
    PORT = int(getenv('PORT', 3000))

    # TODO: programatically get app name
    heroku_server = '%s%s.herokuapp.com' % (__APP_NAME__, end)

    if getenv('DATABASE_URL', False):
        SERVER_NAME = heroku_server

    SECRET_KEY = getenv('SECRET_KEY', 'key')
    REPO = 'https://github.com/%s/%s' % (__USER__, __APP_NAME__)
    API_METHODS = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']
    API_ALLOW_FUNCTIONS = True
    API_ALLOW_PATCH_MANY = True
    API_MAX_RESULTS_PER_PAGE = 1000
    API_URL_PREFIX = '/v1'
    CACHE_TIMEOUT = 60 * 60 * 1  # 1 hour (in seconds)

    MOCK_FREQ = False
    DEBUG = False
    MEMCACHE = True
    TESTING = False
    PROD = False
    CHUNK_SIZE = 10000
    ERR_LIMIT = 10
    ROW_LIMIT = 0
    TIMEOUT = 60 * 60 * 3  # 3 hours (in seconds)
    RESULT_TTL = TIMEOUT * 2


class Production(Config):
    defaultdb = 'postgres://%s@localhost/app' % __USER__
    SQLALCHEMY_DATABASE_URI = getenv('DATABASE_URL', defaultdb)
    HOST = '0.0.0.0'
    PROD = True


class Docker(Config):
    database_path = p.join(_basedir, 'data', 'app.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % database_path
    HOST = '0.0.0.0'
    PROD = True
    MEMCACHE = False


class Development(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % p.join(_basedir, 'app.db')
    MOCK_FREQ = True
    DEBUG = True
    CHUNK_SIZE = 10
    ROW_LIMIT = 50
    MEMCACHE = False
    TIMEOUT = 60 * 10
    RESULT_TTL = TIMEOUT * 2


class Test(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    ROW_LIMIT = 10
    TESTING = True
    MEMCACHE = False
    TIMEOUT = 30
    RESULT_TTL = 60

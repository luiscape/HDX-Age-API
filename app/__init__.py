# -*- coding: utf-8 -*-
"""
    app
    ~~~

    Provides the flask application
"""
###########################################################################
# WARNING: if running on a a staging server, you MUST set the 'STAGE' env
# heroku config:set STAGE=true --remote staging
###########################################################################
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from future.builtins import str

import config

from functools import partial
from inspect import isclass, getmembers
from operator import itemgetter
from os import getenv

from savalidation import ValidationError
from sqlalchemy.exc import IntegrityError, OperationalError

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
from flask.ext.cache import Cache
from flask.ext.compress import Compress
from flask.ext.cors import CORS

API_EXCEPTIONS = [
    ValidationError, ValueError, AttributeError, TypeError, IntegrityError,
    OperationalError]

db = SQLAlchemy()
cache = Cache()

__title__ = 'HDX-Age-API'
__author__ = 'Reuben Cummings'
__description__ = 'Service to query the age and status of an HDX resource'
__email__ = 'reubano@gmail.com'
__version__ = '0.6.1'
__license__ = 'MIT'
__copyright__ = 'Copyright 2015 Reuben Cummings'


def _get_tables():
    from . import models

    classes = map(itemgetter(1), getmembers(models, isclass))
    return [t for t in classes if 'app.models' in str(t)]


def create_app(config_mode=None, config_file=None):
    """ Creates the Flask application

    Kwargs:
        config_mode (str): The configuration mode. Must be a `class` in
            `config.py`. One of ('Production', 'Development', 'Test',
            'Docker')
        config_file (str): The configuration file.

    Returns:
        (obj): Flask application

    Examples:
        >>> create_app('Test')
        <Flask 'app'>
    """
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    mgr = APIManager(app, flask_sqlalchemy_db=db)
    cache_config = {}

    if config_mode:
        app.config.from_object(getattr(config, config_mode))
    elif config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar('APP_SETTINGS', silent=True)

    memcached_servers = getenv('MEMCACHIER_SERVERS', getenv('MEMCACHE_SERVERS'))

    if app.config['PROD'] and app.config['MEMCACHE']:
        cache_config['CACHE_TYPE'] = 'spreadsaslmemcachedcache'
        cache_config['CACHE_MEMCACHED_SERVERS'] = [memcached_servers]
        cache_config['CACHE_MEMCACHED_USERNAME'] = getenv('MEMCACHIER_USERNAME')
        cache_config['CACHE_MEMCACHED_PASSWORD'] = getenv('MEMCACHIER_PASSWORD')
    elif app.config['MEMCACHE']:
        cache_config['CACHE_TYPE'] = 'memcached'
        cache_config['CACHE_MEMCACHED_SERVERS'] = [memcached_servers]
    else:
        cache_config['CACHE_TYPE'] = 'simple'

    cache.init_app(app, config=cache_config)
    db.init_app(app)
    CORS(app)
    Compress(app)

    @app.route('/')
    def home():
        return 'Welcome to the HDX Age API!'

    kwargs = {
        'methods': app.config['API_METHODS'],
        'validation_exceptions': API_EXCEPTIONS,
        'allow_functions': app.config['API_ALLOW_FUNCTIONS'],
        'allow_patch_many': app.config['API_ALLOW_PATCH_MANY'],
        'max_results_per_page': app.config['API_MAX_RESULTS_PER_PAGE'],
        'url_prefix': app.config['API_URL_PREFIX']}

    # Create API endpoints from `models.py`. Each model is available at
    # the endpoint `/<tablename>`.
    create_api = partial(mgr.create_api, **kwargs)

    with app.app_context():
        map(create_api, _get_tables())

    return app

# put at bottom to avoid circular reference errors
from app.views import blueprint

import os
from os import path as p

# module vars
_user = 'reubano'
_basedir = p.dirname(__file__)
_database_path = p.join(_basedir, 'data', 'app.db')

# configurable vars
__APP_NAME__ = 'HDX-Age-API'
__YOUR_NAME__ = 'Reuben Cummings'
__YOUR_EMAIL__ = 'reubano@gmail.com'
__YOUR_WEBSITE__ = 'http://%s.github.io' % _user


# configuration
class Config(object):
    ###########################################################################
    # WARNING: if running on a a staging server, you MUST set the 'STAGE' env
    # heroku config:set STAGE=true --remote staging
    ###########################################################################
    app = __APP_NAME__
    stage = os.environ.get('STAGE', False)
    end = '-stage' if stage else ''

    ADMINS = frozenset([__YOUR_EMAIL__])
    HOST = '127.0.0.1'
    PORT = int(os.environ.get('PORT', 3000))

    # TODO: programatically get app name
    heroku_server = '%s%s.herokuapp.com' % (app, end)

    if os.environ.get('DATABASE_URL', False):
        SERVER_NAME = heroku_server

    SECRET_KEY = os.environ.get('SECRET_KEY', 'key')
    API_METHODS = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']
    API_ALLOW_FUNCTIONS = True
    API_ALLOW_PATCH_MANY = True
    API_MAX_RESULTS_PER_PAGE = 1000
    API_URL_PREFIX = '/v1'

    DEBUG = False
    MEMCACHE = True
    TESTING = False
    PROD = False
    CHUNK_SIZE = 10000
    ROW_LIMIT = 0
    TIMEOUT = 30
    TTL = 60


class Production(Config):
    defaultdb = 'postgres://%s@localhost/app' % _user
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', defaultdb)
    HOST = '0.0.0.0'
    PROD = True
    TIMEOUT = 60 * 10
    TTL = TIMEOUT * 2


class Docker(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % _database_path
    HOST = '0.0.0.0'
    DEBUG_MEMCACHE = False


class Development(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % _database_path
    DEBUG = True
    CHUNK_SIZE = 10
    ROW_LIMIT = 50
    MEMCACHE = False
    TIMEOUT = 60 * 2
    TTL = TIMEOUT * 2


class Test(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    ROW_LIMIT = 10
    TESTING = True
    MEMCACHE = False

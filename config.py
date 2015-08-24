import os
from os import path as p

# module vars
_user = 'reubano'
_basedir = p.dirname(__file__)

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
    HEROKU = os.environ.get('DATABASE_URL', False)

    DEBUG = False
    ADMINS = frozenset([__YOUR_EMAIL__])
    TESTING = False
    HOST = '127.0.0.1'

    # TODO: programatically get app name
    heroku_server = '%s%s.herokuapp.com' % (app, end)

    if HEROKU:
        SERVER_NAME = heroku_server

    SECRET_KEY = os.environ.get('SECRET_KEY', 'key')
    API_METHODS = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']
    API_ALLOW_FUNCTIONS = True
    API_ALLOW_PATCH_MANY = True
    API_MAX_RESULTS_PER_PAGE = 1000
    API_URL_PREFIX = '/v1'


class Production(Config):
    defaultdb = 'postgres://%s@localhost/app' % _user
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', defaultdb)
    HOST = '0.0.0.0'


class Development(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % p.join(_basedir, 'app.db')
    DEBUG = True
    DEBUG_MEMCACHE = False


class Test(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
    DEBUG_MEMCACHE = False

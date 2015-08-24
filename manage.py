#!/usr/bin/env python

from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

import os.path as p

from subprocess import call, check_call

from flask import current_app as app
from flask.ext.script import Server, Manager

from config import Config as c
from app import create_app, db

manager = Manager(create_app)
manager.add_option(
    '-m', '--cfgmode', dest='config_mode', default='Development')
manager.add_option('-f', '--cfgfile', dest='config_file', type=p.abspath)
manager.add_command('runserver', Server(port=c.PORT))
manager.main = manager.run


@manager.command
def checkstage():
    """Checks staged with git pre-commit hook"""

    path = p.join(p.dirname(__file__), 'app', 'tests', 'test.sh')
    cmd = "sh %s" % path
    return call(cmd, shell=True)


@manager.option('-F', '--file', help='Lint file', default='')
def lint(file):
    """Check style with flake8"""
    return call("flake8 %s" % file, shell=True)


@manager.option('-w', '--where', help='Requirement file', default=None)
def test(where):
    """Run nose tests"""
    cmd = "nosetests -xvw %s" % where if where else "nosetests -xv"
    return call(cmd, shell=True)


@manager.command
def deploy():
    """Deploy staging app"""
    check_call('heroku keys:add ~/.ssh/id_rsa.pub --remote staging', shell=True)
    check_call('git push origin features', shell=True)


@manager.command
def deployprod():
    """Deploy production app"""
    check_call(
        'heroku keys:add ~/.ssh/id_rsa.pub --remote production', shell=True)
    check_call('git push origin master', shell=True)


@manager.option('-r', '--requirement', help='Requirement file', default='test')
def pipme(requirement):
    """Install requirements.txt"""
    call('pippy -r requirements/%s.txt' % requirement, shell=True)


@manager.command
def require():
    """Create requirements.txt"""
    cmd = 'pip freeze -l | grep -vxFf requirements/dev.txt '
    cmd += '| grep -vxFf requirements/prod.txt '
    cmd += '| grep -vxFf requirements/test.txt '
    cmd += '> requirements/common.txt'
    call(cmd, shell=True)


@manager.command
def createdb():
    """Creates database if it doesn't already exist"""

    with app.app_context():
        db.create_all()
        print('Database created')


@manager.command
def cleardb():
    """Removes all content from database"""

    with app.app_context():
        db.drop_all()
        print('Database cleared')


@manager.command
def resetdb():
    """Removes all content from database and creates new tables"""

    with app.app_context():
        cleardb()
        createdb()


if __name__ == '__main__':
    manager.run()

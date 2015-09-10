# -*- coding: utf-8 -*-
"""
    app.views
    ~~~~~~~~~

    Provides additional API endpoints
"""
from __future__ import (
    absolute_import, division, print_function, with_statement,
    unicode_literals)

from flask import Blueprint, request, current_app as app
from rq import Queue
from loremipsum import get_sentences
from ckanutils import CKAN
from collections import defaultdict

from config import Config as c
from app import cache, __version__, utils
from app.utils import jsonify, make_cache_key, parse
from app.connection import conn

q = Queue(connection=conn)
blueprint = Blueprint('blueprint', __name__)


@blueprint.route('%s/status/' % c.API_URL_PREFIX)
@cache.cached(timeout=c.CACHE_TIMEOUT, key_prefix=make_cache_key)
def status():
    """ Displays the current status
    """
    kwargs = {k: parse(v) for k, v in request.args.to_dict().items()}
    ckan = CKAN(**kwargs)

    resp = {
        'online': True,
        'message': 'Service for checking and updating HDX dataset ages.',
        'CKAN_instance': ckan.address,
        'version': __version__,
        'repository': c.REPO
    }

    return jsonify(**resp)


@blueprint.route('%s/lorem/' % c.API_URL_PREFIX)
@cache.cached(timeout=c.CACHE_TIMEOUT, key_prefix=make_cache_key)
def lorem():
    """ Displays random loremipsum text.
    """
    resp = {'result': get_sentences(1)[0]}
    return jsonify(**resp)


@blueprint.route('%s/update/' % c.API_URL_PREFIX)
@blueprint.route('%s/update/<pid>/' % c.API_URL_PREFIX)
def update(pid=None):
    """ Updates the database

    Args:
        pid (str): Package id of the package to update.
    """
    kwargs = {k: parse(v) for k, v in request.args.to_dict().items()}
    sync = kwargs.pop('sync', False)
    whitelist = [
        'CHUNK_SIZE', 'ROW_LIMIT', 'ERR_LIMIT', 'MOCK_FREQ', 'TIMEOUT',
        'RESULT_TTL']

    with app.app_context():
        defaults = {
            k.lower(): v for k, v in app.config.items() if k in whitelist}

        opts = defaultdict(int, pid=pid, **defaults)
        opts.update(kwargs)
        base = 'http://%(HOST)s:%(PORT)s%(API_URL_PREFIX)s' % app.config
        endpoint = '%s/age' % base

        if sync:
            resp = {'result': utils.update(endpoint, **opts)}
        else:
            job = q.enqueue(utils.update, endpoint, **opts)
            result_url = '%s/result/%s/' % (endpoint, job.id)

            resp = {
                'job_id': job.id,
                'job_status': job.get_status(),
                'result_url': result_url}

        return jsonify(**resp)


@blueprint.route('%s/result/<jid>/' % c.API_URL_PREFIX)
def result(jid):
    """ Displays a job result.

    Args:
        jid (str): The job id.
    """
    job = q.fetch_job(jid)
    statuses = {
        'queued': 202,
        'started': 202,
        'finished': 200,
        'failed': 500,
        'job not found': 404,
    }

    if job:
        job_status = job.get_status()
        result = job.result
    else:
        job_status = 'job not found'
        result = None

    resp = {
        'status': statuses[job_status],
        'job_id': jid,
        'job_status': job_status,
        'result': result}

    return jsonify(**resp)


@blueprint.route('%s/double/<num>/' % c.API_URL_PREFIX)
@cache.memoize(timeout=c.CACHE_TIMEOUT)
def double(num):
    """ Displays the double of a given number. Included as an example of the
    `cache.memoize` decorator.

    Args:
        num (int): The number to double.
    """
    resp = {'result': 2 * num}
    return jsonify(**resp)


@blueprint.route('%s/delete/<resource>/' % c.API_URL_PREFIX)
def delete(resource):
    """ Deletes the cache of a given resource

    Args:
        resource (str): The resource to delete.
    """
    url = request.url.replace('delete/', '')
    cache.delete(url)
    return jsonify(result='Key: %s deleted' % url)


@blueprint.route('%s/reset/' % c.API_URL_PREFIX)
def reset():
    """ Deletes the entire cache
    """
    cache.clear()
    return jsonify(result='Caches reset')

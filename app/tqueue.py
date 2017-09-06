# -*- coding: utf-8 -*-
import logging
import httplib
import flask

from models import JustToShow

tq_bp = flask.Blueprint('tq', 'tq')
route = tq_bp.route


@route('/example_task', methods=['GET'])
def example_task():
    JustToShow.create_and_put()
    return '', httplib.OK


@route('/cron_job_trigger', methods=['GET'])
def cron_job_trigger():
    return '', httplib.OK

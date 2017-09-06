# -*- coding: utf-8 -*-
import httplib
import logging

from functools import wraps
from flask_login import current_user
import flask


def user_required(func):

    @wraps(func)
    def wrapper(*args, **kw):
        if not current_user.is_authenticated:
            logging.debug('not current_user.is_authenticated')
            flask.abort(flask.make_response(flask.jsonify(message='UNAUTHORIZED'), httplib.UNAUTHORIZED))

        return func(*args, **kw)

    return wrapper

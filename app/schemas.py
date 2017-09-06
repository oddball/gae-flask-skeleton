# -*- coding: utf-8 -*-
import logging
from pprint import pformat
import httplib
from functools import wraps
import json

from good import Schema, Invalid, Optional, Required, Match, Maybe, All, Range, Length
from good.validators.base import ValidatorBase
import flask


def validate_input(schema):
    schema = schema()

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            # GET does not need validation
            if flask.request.method in ['POST', 'PUT', 'DELETE']:
                try:
                    data = flask.request.get_json()
                except Exception as e:
                    return flask.jsonify({"error": 'Could not decode json'}), httplib.BAD_REQUEST
                try:
                    schema(data)
                except Invalid as e:
                    logging.debug({"error": str(e)})
                    return flask.jsonify({"error": str(e)}), httplib.BAD_REQUEST
            return f(*args, **kw)

        return wrapper

    return decorator


def validate_output(schema):
    schema = schema()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Invoke the wrapped function first
            retval = func(*args, **kwargs)
            # Now do something here with retval

            assert len(retval) == 2
            status_code = retval[1]
            if (status_code / 100) == 2:
                if hasattr(retval[0], 'data'):
                    try:
                        data = json.loads(retval[0].data)
                        schema(data)
                    except Invalid as e:
                        logging.debug({"error": str(e)})
                        return flask.jsonify({"error": str(e)}), httplib.BAD_REQUEST
                else:
                    try:
                        data = json.loads(retval[0])
                        schema(data)
                    except Invalid as e:
                        logging.debug({"error": str(e)})
                        return flask.jsonify({"error": str(e)}), httplib.BAD_REQUEST

            return retval

        return wrapper

    return decorator


def profile_out_schema():
    return Schema({
        'first_name': basestring,
        'last_name': basestring,
        'id': basestring,
        Optional('cn'): basestring,
    })


def profile_in_schema():
    return Schema({
        'first_name': basestring,
        'last_name': basestring,
        Optional('cn'): basestring,
    })

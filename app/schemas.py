# -*- coding: utf-8 -*-
import logging
import httplib
from functools import wraps
import json

import flask
import jsonschema


def validate_input(schema):
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
                    jsonschema.validate(data, schema)
                except jsonschema.ValidationError as e:
                    logging.debug({"error": str(e)})
                    return flask.jsonify({"error": str(e)}), httplib.BAD_REQUEST
            return f(*args, **kw)

        return wrapper

    return decorator


def validate_output(schema):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Invoke the wrapped function first
            retval = func(*args, **kwargs)
            # Now do something here with retval

            assert len(retval) == 2
            status_code = retval[1]
            data = retval[0]
            if (status_code / 100) == 2:
                try:
                    jsonschema.validate(data, schema)
                except jsonschema.ValidationError as e:
                    logging.debug({"error": str(e)})
                    return flask.jsonify({"error": str(e)}), httplib.BAD_REQUEST

            return retval

        return wrapper

    return decorator


PROFILE_OUT_SCHEMA = {
    #"$schema": "http://json-schema.org/schema#",
    "required": [
        "first_name",
        "id",
        "last_name"
    ],
    "type": "object",
    "properties": {
        "first_name": {
            "type": "string"
        },
        "last_name": {
            "type": "string"
        },
        "id": {
            "type": "string"
        },
        "cn": {
            "type": "string"
        }
    }
}

PROFILE_IN_SCHEMA = {
    #"$schema": "http://json-schema.org/schema#",
    "required": [
        "first_name",
        "last_name"
    ],
    "type": "object",
    "properties": {
        "first_name": {
            "type": "string"
        },
        "last_name": {
            "type": "string"
        },
        "cn": {
            "type": "string"
        }
    }
}

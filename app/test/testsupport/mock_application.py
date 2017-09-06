# -*- coding: utf-8 -*-
import json
import logging


class MockApplication(object):
    """
    Mock application that
    returns a canned body and arguments to start_response and
    registers environ
    """
    # Canned results are tuples of (start_args, body)
    # If cannedresponse is a list, it will be popped until there is only
    # one item left
    cannedresponse = ((200, {'Content-Type': 'text/plain'}), '')

    def __init__(self):
        self.environ = []

    def __call__(self, environ, start_response):
        self.environ.append(environ)
        if isinstance(self.cannedresponse, list):
            if self.cannedresponse:
                start_args, cannedbody = self.cannedresponse.pop(0)
            else:
                raise ValueError('No canned results left')
        else:
            start_args, cannedbody = self.cannedresponse
        start_response(*start_args)
        if callable(cannedbody):
            return cannedbody(environ)
        return cannedbody

    def clear(self):
        self.environ[:] = []

    @property
    def path(self):
        return self.env('PATH_INFO')

    @property
    def method(self):
        return self.env('REQUEST_METHOD')

    @property
    def content_type(self):
        return self.env('CONTENT_TYPE')

    @property
    def query(self):
        qs_list = self.env('QUERY_STRING')
        return [dict(x.split('=') for x in qs.split('&')) if qs else None for qs in qs_list]

    @property
    def raw_input(self):
        res = self.env('wsgi.input')
        return [r.getvalue() for r in res]

    @property
    def input(self):
        def decode(environ):
            if environ['REQUEST_METHOD'].upper() not in ('PUT', 'POST'):
                return
            wsgi_input = environ['wsgi.input'].getvalue()
            if 'CONTENT_TYPE' in environ and 'json' in environ['CONTENT_TYPE']:
                return json.loads(wsgi_input)
            return wsgi_input
        result = [decode(e) for e in self.environ]
        return result

    def env(self, name):
        if not self.environ:
            raise ValueError('No requests registered')
        result = tuple(e[name] for e in self.environ)
        return result

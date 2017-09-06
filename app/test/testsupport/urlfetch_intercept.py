# -*- coding: utf-8 -*-
# https://gist.github.com/818005 based on
# http://code.google.com/p/wsgi-intercept/
"""
Monkey patch to hit wsgi apps when using urlfetch

This will monkey patch App Engine's urlfetch.fetch with a fetch that hits a local
wsgi app registered with add_intercept. This module is inspired by and borrows
code from the wsgi-intercept project, which doesn't work with App Engine.

This is intended only for the local SDK environment for unit tests.

Usage:

from google.appengine.api import urlfetch
import urlfetch_intercept
urlfetch_intercept.install()
urlfetch_intercept.add_intercept('example.com', my_wsgi_app)

resp = urlfetch.fetch("http://example.com/foo")
...

"""

import re
import StringIO
import urllib
import urlparse

from google.appengine.api import urlfetch
from google.appengine.api.apiproxy_rpc import RPC
from google.appengine.api.urlfetch import fetch as original_fetch
from google.appengine.api.urlfetch import make_fetch_call as original_make_fetch_call
from google.appengine.api.urlfetch import _CaselessDict
import webob

__all__ = ['install', 'uninstall', 'add_intercept', 'remove_intercept']


def install():
    urlfetch.fetch = wsgi_fetch
    urlfetch.make_fetch_call = wsgi_make_fetch_call


def uninstall():
    urlfetch.fetch = original_fetch
    urlfetch.make_fetch_call = original_make_fetch_call
    _intercepts.clear()


_intercepts = {}


def add_intercept(host, app):
    _intercepts[host] = app


def remove_intercept(host):
    del _intercepts[host]


def wsgi_make_fetch_call(rpc, url, payload=None, method=urlfetch.GET, headers={},
                         allow_truncated=False, follow_redirects=True, validate_certificate=None):
    assert rpc.service == 'urlfetch', repr(rpc.service)
    result = wsgi_fetch(url, payload, method, headers,
                        allow_truncated, follow_redirects, rpc.deadline)
    # Fake registration with stub service by setting state to finishing to
    # avoid ndb eventloop error
    rpc._UserRPC__rpc._state = RPC.FINISHING
    rpc.get_result = lambda: result


GCS_TESTBED_PATTERN = re.compile('^https?://testbed.example.com/_ah/gcs/.*$')


def wsgi_fetch(url, payload=None, method=urlfetch.GET, headers={},
               allow_truncated=False, follow_redirects=True,
               deadline=None, validate_certificate=None):

    if GCS_TESTBED_PATTERN.match(url):
        # The SDK emulation of GCS works while unit-testing too if we don't do the intercept.
        # To avoid infinite loop we apparently need to uninstall the intercept
        # temporarily.
        try:
            uninstall()
            return original_fetch(url, payload=payload, method=method, headers=headers, allow_truncated=allow_truncated,
                                  follow_redirects=follow_redirects, deadline=deadline,
                                  validate_certificate=validate_certificate)
        finally:
            install()

    url = urlparse.urlparse(url)
    app = _intercepts[url.netloc]

    req = webob.Request.blank(
        '%s?%s' % (url.path, url.query),
        base_url='{}://{}'.format(url.scheme, url.netloc))
    req.method = method
    for header in headers:
        req.headers[header] = headers[header]
    if payload:
        if isinstance(payload, str):
            req.body = payload
        elif isinstance(payload, unicode):
            req.body = payload.encode('utf-8')
        else:
            req.body = urllib.urlencode(payload)

    resp = {}
    resp['content_was_truncated'] = False
    resp['final_url'] = url

    write_results = []

    def start_response(status, headers, exc_info=None):
        resp['status_code'] = status
        resp['headers'] = headers

        def write_fn(s):
            write_results.append(s)
        return write_fn

    # run the application.
    app_result = app(req.environ, start_response)
    result = iter(app_result)

    ###

    # read all of the results.  the trick here is to get the *first*
    # bit of data from the app via the generator, *then* grab & return
    # the data passed back from the 'write' function, and then return
    # the generator data.  this is because the 'write' fn doesn't
    # necessarily get called until the first result is requested from
    # the app function.
    #
    # see twill tests, 'test_wrapper_intercept' for a test that breaks
    # if this is done incorrectly.
    output = []
    try:
        generator_data = None
        try:
            generator_data = result.next()

        finally:
            for data in write_results:
                output.append(data)

        if generator_data:
            output.append(generator_data)

            while 1:
                data = result.next()
                output.append(data)

    except StopIteration:
        pass

    resp['content'] = ''.join(output)

    if hasattr(app_result, 'close'):
        app_result.close()

    return _URLFetchResult(resp)


class _URLFetchResult(object):
    """A Pythonic representation of our fetch response protocol buffer.
    """

    def __init__(self, response_dict):
        """Constructor.

        Args:
          response_dict: the intercepted response dict to wrap.
        """
        try:
            from google.appengine.dist27 import httplib
        except ImportError:  # pragma: no cover
            import httplib

        self.__data = response_dict
        self.content = response_dict['content']
        self.status_code = response_dict['status_code']
        self.content_was_truncated = response_dict['content_was_truncated']
        self.final_url = response_dict['final_url'] or None
        self.header_msg = httplib.HTTPMessage(
            StringIO.StringIO(''.join(['%s: %s\n' % h
                                       for h in dict(response_dict['headers']).items()] + ['\n'])))
        self.headers = _CaselessDict(self.header_msg.items())

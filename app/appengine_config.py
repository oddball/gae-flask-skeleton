# -*- coding: utf-8 -*-
import os
import sys

from google.appengine.ext import vendor

import settings

# Third-party libraries are stored in "lib", vendoring will make
# sure that they are importable by the application.
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if path not in sys.path:
    vendor.add(path)


def namespace_manager_default_namespace_for_request(*args, **kwargs):
    return settings.NAMESPACE


appstats_SHELL_OK = True

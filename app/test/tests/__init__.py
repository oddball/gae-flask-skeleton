# -*- coding: utf-8 -*-
import sys
import os
import distutils

path = os.path.dirname(os.path.dirname(distutils.spawn.find_executable('dev_appserver.py')))
app_engine_path = os.path.join(path, 'platform/google_appengine')
app_engine_third_party_path = os.path.join(path, 'platform/google_appengine/lib/yaml/lib')

if app_engine_path not in sys.path:
    sys.path.insert(1, app_engine_path)

if app_engine_path not in sys.path:
    sys.path.insert(1, app_engine_third_party_path)

test_path = os.path.dirname(os.path.realpath(__file__))
app_path = os.path.dirname(test_path)
sys.path.insert(1,  app_path)


path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))), 'lib')
if path not in sys.path:
    from google.appengine.ext import vendor
    vendor.add(path)

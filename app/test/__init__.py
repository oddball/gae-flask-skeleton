# -*- coding: utf-8 -*-
import sys
import os
import distutils

path = os.path.dirname(os.path.dirname(distutils.spawn.find_executable('dev_appserver.py')))

sys.path.insert(1,  os.path.join(path, 'platform/google_appengine'))
sys.path.insert(1,  os.path.join(path, 'platform/google_appengine/lib/yaml/lib'))

test_path = os.path.dirname(os.path.realpath(__file__))
app_path = os.path.dirname(test_path)
sys.path.insert(1,  app_path) 



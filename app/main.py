# -*- coding: utf-8 -*-
from base import create_app
import os
import settings
from slash import slash_bp
from backoffice import backoffice_bp
from tqueue import tq_bp
from api import api_bp
import jinja2


this_path = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FOLDER = os.path.join(this_path, 'templates')

application = create_app(__name__)

my_loader = jinja2.ChoiceLoader([
    application.jinja_loader,
    jinja2.FileSystemLoader(TEMPLATE_FOLDER),
    jinja2.FileSystemLoader(os.path.join(this_path, 'lib/flask_bootstrap/templates'))
])

application.jinja_loader = my_loader

application.register_blueprint(slash_bp)
application.register_blueprint(tq_bp, url_prefix='/tqueue')
application.register_blueprint(api_bp, url_prefix='/api')

application.register_blueprint(backoffice_bp, url_prefix='/backoffice')
if settings.TESTBED_ACTIVE:
    from testbed import testbed_bp
    application.register_blueprint(testbed_bp, url_prefix='/testbed')

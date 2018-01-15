from app.config import Config
from .. import ApplicationTest, factory
from expects import *
from expects.matchers import Matcher
from unittest import TestCase
import os
import tempfile
import yaml

class be_successful(Matcher):
    def __init__(self):
        pass

    def _match(self, request):
        if request.status_code >= 200 and request.status_code <= 299:
            return True, ["Request was successful"]
        else:
            return False, ["Status code outside of 2xx range"]

be_successful = be_successful()

class have_in_body(Matcher):
    def __init__(self, content):
        self.content = content

    def _match(self, request):
        body = request.get_data(as_text=True)
        if self.content in body:
            return True, ["'{}' in '{}'".format(self.content, body)]
        else:
            return False, ["'{}' not in '{}'".format(self.content, body)]

class ControllerTest(ApplicationTest):
    def setUp(self):
        super().setUp()

        from app import server
        server.testing = True
        self.app = server.test_client()

        if hasattr(self, '_setup'):
            self._setup()

    def tearDown(self):
        super().tearDown()

        if hasattr(self, '_teardown'):
            self._teardown()

    def write_config(self, **kwargs):
        self.config.update(kwargs)
        with open(os.path.join(self.config_dir.name, 'application.yaml'), 'w') as handler:
            handler.write(yaml.dump(self.config, default_flow_style = False))

        Config._full_reload()

from app.config import Config
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

class ControllerTest(TestCase):
    def setUp(self):
        self.content_dir = tempfile.TemporaryDirectory()
        self.config_dir = tempfile.TemporaryDirectory()

        os.environ['CONFIG_DIR'] = self.config_dir.name

        self.config = {
            "content_directory": self.content_dir.name
        }

        self.write_config()
        Config._full_reload()

        from app import server
        server.testing = True
        self.app = server.test_client()

        if hasattr(self, '_setup'):
            self._setup()

    def tearDown(self):
        del os.environ['CONFIG_DIR']
        self.content_dir.cleanup()
        self.config_dir.cleanup()

        if hasattr(self, '_teardown'):
            self._teardown()

    def write_config(self, **kwargs):
        self.config.update(kwargs)
        with open(os.path.join(self.config_dir.name, 'application.yaml'), 'w') as handler:
            handler.write(yaml.dump(self.config, default_flow_style = False))

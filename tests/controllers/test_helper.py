from app.config import Config
from app.image_service import ImageService
from app.controllers import BaseController
from .. import ApplicationTest, factory
from moto import mock_s3
from expects import *
from expects.matchers import Matcher
from unittest import TestCase
import boto3
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

@mock_s3
class ControllerTest(ApplicationTest):
    def setUp(self):
        super().setUp()

        boto3.resource('s3').create_bucket(Bucket = 'upload_test')
        self.write_config(image_bucket = "upload_test")
        image_service = ImageService('upload_test')

        from app import server
        server.testing = True
        self.app = server.test_client()

        BaseController.set_image_service(image_service)

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

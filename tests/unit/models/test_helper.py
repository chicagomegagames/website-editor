from app import Config
from app.models import BaseModel
from unittest import TestCase
from expects import *
import os
import tempfile
import yaml

class ModelTestCase(TestCase):
    def setUp(self):
        self.content_dir = tempfile.TemporaryDirectory()

        config = {
            'content_directory': self.content_dir.name
        }
        self.config_dir = tempfile.TemporaryDirectory()
        os.environ['CONFIG_DIR'] = self.config_dir.name

        with open(os.path.join(self.config_dir.name, 'application.yaml'), 'w') as handler:
            handler.write(yaml.dump(config, default_flow_style = False))
        Config._full_reload()

    def tearDown(self):
        self.content_dir.cleanup()
        self.config_dir.cleanup()

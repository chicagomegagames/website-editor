from app.models import BaseModel
from unittest import TestCase
from expects import *
import tempfile

class ModelTestCase(TestCase):
    def setUp(self):
        self.content_dir = tempfile.TemporaryDirectory()
        BaseModel.set_base_dir(self.content_dir.name)

    def tearDown(self):
        self.content_dir.cleanup()

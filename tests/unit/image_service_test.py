from app import ImageService, Config
from expects import *
from unittest import TestCase
import filecmp
import os
import tempfile

class ImageServiceTest(TestCase):
    def setUp(self):
        self.config = Config(
            theme = "foo",
        )

        current_dir = os.path.dirname(__file__)
        self.test_file_path = os.path.join(current_dir, "..", "fixtures", "square_logo.svg")

        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_local_upload_image(self):
        service = ImageService(upload_path = self.temp_dir.name)

        with open(self.test_file_path, "rb") as test_file:
            service.upload_image("square_logo.svg", test_file)

        expect(filecmp.cmp(service.images()[0].path, self.test_file_path)).to(be_true)

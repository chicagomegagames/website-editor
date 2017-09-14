from app import ImageService, Config
# from app.image_service import _ImageService
from expects import *
from unittest import TestCase
import filecmp
import os
import tempfile
import yaml

class ImageServiceTest(TestCase):
    def setUp(self):
        current_dir = os.path.dirname(__file__)
        self.test_file_path = os.path.join(current_dir, "..", "fixtures", "square_logo.svg")

        self.temp_dir = tempfile.TemporaryDirectory()

        self.config = {
            'content_directory': os.path.join(self.temp_dir.name, 'content'),
        }
        self.config_dir = os.path.join(self.temp_dir.name, "config")
        os.environ['CONFIG_DIR'] = self.config_dir

        os.mkdir(self.config_dir)
        os.mkdir(self.config['content_directory'])

        self._write_config()

        Config._full_reload()

    def tearDown(self):
        self.temp_dir.cleanup()

    def _write_config(self):
        with open(os.path.join(self.config_dir, 'application.yaml'), 'w') as handler:
            handler.write(yaml.dump(self.config, default_flow_style = False))

    def test_local_upload_image(self):

        with open(self.test_file_path, "rb") as test_file:
            ImageService.upload_image("square_logo.svg", test_file)

        expect(filecmp.cmp(ImageService.images()[0].path, self.test_file_path)).to(be_true)

    def test_find(self):
        with open(self.test_file_path, "rb") as test_file:
            ImageService.upload_image("square_logo.svg", test_file)

        image = ImageService.images()[0]
        expect(image).not_to(be_none)
        expect(ImageService.find(image.name)).to(equal(image))

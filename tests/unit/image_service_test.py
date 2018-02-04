from .. import ApplicationTest
from app import ImageService, Config
# from app.image_service import _ImageService
from moto import mock_s3
from expects import *
from unittest import TestCase
import filecmp
import os
import tempfile
import yaml

class ImageServiceTest(ApplicationTest):
    def setUp(self):
        super().setUp()

        current_dir = os.path.dirname(__file__)
        self.test_file_path = os.path.join(current_dir, "..", "fixtures", "square_logo.svg")

        # self.config['image_bucket'] = 'upload_test'
        # self.write_config()

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

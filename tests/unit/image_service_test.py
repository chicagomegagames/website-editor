from .. import ApplicationTest, factory
from app import ImageService
from app.models import Image
from moto import mock_s3
from expects import *
import boto3
import filecmp
import os

@mock_s3
class ImageServiceTest(ApplicationTest):
    def setUp(self):
        super().setUp()

        current_dir = os.path.dirname(__file__)
        self.test_file_path = os.path.join(current_dir, "..", "fixtures", "square_logo.svg")

        self.service = ImageService('upload_test')
        self.resource = boto3.resource('s3')
        self.resource.create_bucket(Bucket = 'upload_test')


    def test_generate_filename(self):
        expect(ImageService._generate_upload_filename("foo.jpg")).to(equal("foo.jpg"))

        factory(Image).create(name = "foo.jpg")
        expect(ImageService._generate_upload_filename("foo.jpg")).not_to(equal("foo.jpg"))
        expect(ImageService._generate_upload_filename("foo.jpg")).to(start_with("foo"))
        expect(ImageService._generate_upload_filename("foo.jpg")).to(end_with(".jpg"))

        expect(ImageService._generate_upload_filename("bar.JPG")).to(equal("bar.jpg"))

    def test_local_upload_image(self):
        with open(self.test_file_path, "rb") as test_file:
            image = self.service.upload_image("square_logo.svg", test_file)

            test_file.seek(0)
            blob = test_file.read()

        upload_file = self.resource.Object('upload_test', image.name)
        upload_blob = upload_file.get()['Body'].read()

        expect(blob).to(equal(upload_blob))

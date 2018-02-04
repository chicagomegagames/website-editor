from app import Config
from app.models import Image
import boto3
import os
import shutil
import shortuuid

shortuuid.set_alphabet('abcdefghijklmnopqrstuvwxyz')

class ImageService(object):
    @staticmethod
    def _generate_upload_filename(filename):
        filename = filename.lower()

        name, extension = os.path.splitext(filename)
        while Image.where('name', '=', filename).count() == 1:
            uid = shortuuid.uuid()[0:7]
            filename = "{}-{}.{}".format(name, uid, extension)

        return filename

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self._client = Config.aws_session().client('s3')
        self.s3 = Config.aws_session().resource('s3')

        self.bucket = self.s3.Bucket(self.bucket_name)


    def upload_image(self, filename, stream):
        upload_filename = self._generate_upload_filename(filename)

        self.bucket.put_object(
            Key = filename,
            Body = stream,
        )

        image = Image.create(
            name = filename,
            bucket = self.bucket_name,
        )

        return image

    def images(self):
        Image.where('bucket_name', '=', self.bucket_name)

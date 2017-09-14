from app import Config, utils
import os
import shutil
import uuid

class _ImageService(object):
    @staticmethod
    def _generate_upload_filename(filename):
        extension = os.path.splitext(filename)[1]
        return "{}{}".format(uuid.uuid4(), extension)

    def upload_image(self, filename, stream):
        upload_filename = self._generate_upload_filename(filename)
        new_file_path = os.path.join(Config.upload_path, upload_filename)

        with open(new_file_path, "wb+", buffering=0) as new_file:
            shutil.copyfileobj(stream, new_file)

        return ImageFile(Config.upload_path, upload_filename)

    def images(self):
        return [ImageFile(Config.upload_path, file) for file in os.listdir(Config.upload_path)]

    def find(self, name):
        return ImageFile(Config.upload_path, name)

class ImageFile(object):
    def __init__(self, directory, name):
        self.directory = directory
        self.name = name
        self.path = os.path.join(self.directory, self.name)

    def __eq__(self, other):
        return other.path == self.path

    def delete(self):
        os.remove(self.path)

ImageService = _ImageService()

from .models import BaseModel
import os
import shutil
import uuid

class ImageService(object):
    @staticmethod
    def _generate_upload_filename(filename):
        extension = os.path.splitext(filename)[1]
        return "{}{}".format(uuid.uuid4(), extension)


    def __init__(self, upload_path = None):
        if upload_path is None:
            raise AttributeError("upload_path must be set when creating an ImageService")
        self.upload_path = upload_path

    def upload_image(self, filename, stream):
        upload_filename = self._generate_upload_filename(filename)
        new_file_path = os.path.join(self.upload_path, upload_filename)

        with open(new_file_path, "wb+", buffering=0) as new_file:
            shutil.copyfileobj(stream, new_file)

        return ImageFile(self.upload_path, upload_filename)

    def images(self):
        return [ImageFile(self.upload_path, file) for file in os.listdir(self.upload_path)]

class ImageFile(object):
    def __init__(self, directory, name):
        self.directory = directory
        self.name = name
        self.path = os.path.join(self.directory, self.name)

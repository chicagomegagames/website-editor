from . import _Model

class Image(_Model):
    @property
    def url(self):
        return "https://{}.s3.amazonaws.com/{}".format(self.bucket, self.name)

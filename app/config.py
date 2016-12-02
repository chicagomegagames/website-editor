import os
import yaml

class Config(object):
    REQUIRED_OPTIONS = [
        "theme",
    ]

    DEFAULT_OPTIONS = {
        "aws_access_id": None,
        "aws_secret_key": None,
        "content_directory": os.path.join(os.getcwd(), "content"),
        "debug": False,
        "default_template": "page.html",
        "deploy_locations": {},
        "host": "0.0.0.0",
        "port": 5000,
        "sentry_dns": None,
    }

    @classmethod
    def from_file(cls, file_path):
        with open(file_path) as stream:
            config = yaml.load(stream)

        return cls(**config)


    def __init__(self, options={}, **kwargs):
        if options == {}:
            args = kwargs
        else:
            args = options
        self.config = {**self.DEFAULT_OPTIONS, **args}

        if "theme" not in self.config:
            raise KeyError("'theme' is a required configuration option")

    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]

        raise AttributeError("'{}' is not an attribute of {}".format(name, self))

    def use_sentry(self):
        return self.config["sentry_dns"] is not None
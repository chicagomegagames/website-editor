from .models import BaseModel
from .generator_service import GeneratorService
import os
import traceback
import sys
import yaml

class Config(object):
    DEFAULT_OPTIONS = {
        "content_directory": os.path.join(os.getcwd(), "content"),
        "debug": False,
        "default_template": "page.html",
        "deploy_locations": {},
        "environment": "development",
        "host": "0.0.0.0",
        "port": 5000,
        "sentry_dns": None,
        "theme": "modern",
        "upload_path": None,
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

        config = dict(self.DEFAULT_OPTIONS)
        config.update(args)
        self.config = config

        if "upload_path" not in self.config or not self.config["upload_path"]:
            self.config["upload_path"] = os.path.join(self.config["content_directory"], "image_uploads")

        BaseModel.set_base_dir(self.config["content_directory"])

    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]

        raise AttributeError("'{}' is not an attribute of {}".format(name, self))

    def use_sentry(self):
        return self.config["sentry_dns"] is not None

    def capture_exception(self, err = None):
        if self.use_sentry() and "sentry" in self.config:
            self.sentry.captureException()
        else:
            print(err)
            traceback.print_tb(err.__traceback__, file=sys.stdout)

    def themes(self):
        if "theme_directory" in self.config:
            theme_dir = self.config["theme_directory"]
        else:
            theme_dir = os.path.join(self.config["content_directory"], "themes")

        themes = filter(os.path.isdir, [os.path.join(theme_dir, name) for name in os.listdir(theme_dir)])
        return {
            os.path.basename(path): path for path in themes
        }

    def site_generators(self):
        return {
            key: GeneratorService(
                key = key,
                name = cfg["name"],
                location = cfg["location"],
                default_theme_path = os.path.join(self.config["content_directory"], "themes", self.config["theme"]),
            ) for key, cfg in self.config["deploy_locations"].items()
        }

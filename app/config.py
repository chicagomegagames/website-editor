from orator import DatabaseManager
from app import utils
import boto3
import os
import traceback
import sys
import yaml

class _Config(object):
    @classmethod
    def load(cls):
        if 'CONFIG_DIR' in os.environ:
            config_dir = os.environ['CONFIG_DIR']
        else:
            config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')

        path = os.path.join(config_dir, 'application.yaml')
        return cls(path)

    def __init__(self, path):
        self.path = path
        self.config = {}
        self._database = None
        self._aws_session = None

        self.reload()

    def __getattr__(self, name):
        if name in self.config:
            return self.config[name]

        raise AttributeError("'{}' is not an attribute of {}".format(name, self))

    @property
    def upload_path(self):
        return os.path.join(self.config["content_directory"], "image_uploads")

    def use_sentry(self):
        return 'sentry_dns' in self.config

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

    def database(self):
        if not 'databases' in self.config
            return None

        if not self._database:
            self._database = DatabaseManager(self.config['databases'])

        return self._database

    def aws_session(self):
        if not self._aws_session:
            creds = {}
            if 'aws_credentials' in self.config:
                creds = self.config['aws_credentials']
            self._aws_session = boto3.Session(**creds)

        return self._aws_session

    def reload(self):
        if 'path' not in self.__dict__ and 'CONFIG_DIR' in os.environ:
            config_dir = os.environ['CONFIG_DIR']
            self.path = os.path.join(config_dir, 'application.yaml')

        if os.path.exists(self.path):
            with open(self.path) as stream:
                from_file = yaml.load(stream)
        else:
            from_file = {}

        self.config.update(from_file)

        if 'content_directory' in self.config:
            utils.make_directory_tree(self.upload_path)

        self._database = None
        self._session = None


    def _full_reload(self):
        if 'CONFIG_DIR' not in os.environ:
            return

        self.path = os.path.join(os.environ['CONFIG_DIR'], 'application.yaml')
        self.config = {}
        self.reload()

Config = _Config.load()

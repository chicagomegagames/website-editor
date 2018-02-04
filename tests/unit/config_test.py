from unittest import TestCase
from app import Config
from expects import *
import orator
import os
import tempfile
import yaml

class TestConfig(TestCase):
    def setUp(self):
        self.config = {}
        self.config_dir = tempfile.TemporaryDirectory()

        os.environ['CONFIG_DIR'] = self.config_dir.name

        self.write_config()

        Config._full_reload()

    def tearDown(self):
        del os.environ['CONFIG_DIR']
        self.config_dir.cleanup()

    def write_config(self):
        with open(os.path.join(self.config_dir.name, 'application.yaml'), 'w') as handler:
            handler.write(yaml.dump(self.config, default_flow_style = False))

    def test_getattr(self):
        self.config = {
            "theme": "foo",
        }
        self.write_config()
        Config.reload()

        expect(lambda: Config.foo).to(raise_error(AttributeError))
        expect(lambda: Config.theme).not_to(raise_error)

    def test_reload(self):
        self.config = {
            "theme": "foo",
            "debug": True,
        }
        self.write_config()

        Config.reload()

        expect(Config.theme).to(equal("foo"))
        expect(Config.debug).to(be_true)

    def test_reload_creates_image_upload_directory(self):
        content_dir = tempfile.TemporaryDirectory()

        self.config = {
            'content_directory': content_dir.name
        }
        self.write_config()
        Config.reload()

        expect(os.path.exists(os.path.join(content_dir.name, 'image_uploads'))).to(be_true)

        content_dir.cleanup()

    def test_no_file(self):
        os.environ['CONFIG_DIR'] = os.path.join(self.config_dir.name, 'not_a_dir')
        expect(
            lambda: Config._full_reload()
        ).not_to(raise_error)

    def test_use_sentry(self):
        expect(Config.use_sentry()).to(be_false)

        self.config['sentry_dns'] = "https://user:pass@sentry.io/application_id"
        self.write_config()
        Config.reload()

        expect(Config.use_sentry()).to(be_true)

    def test_get_database(self):
        self.config['databases'] = {
            "connection": {
                "driver": "sqlite",
                "database": ":memory:",
            },
        }
        self.write_config()
        Config.reload()

        db = Config.database()
        expect(db).to(be_an(orator.DatabaseManager))

    def test_get_database_no_config(self):
        expect(
            lambda: Config.database()
        ).to(raise_error(AttributeError))

    def test_database_is_memoized(self):
        self.config['databases'] = {
            "connection": {
                "driver": "sqlite",
                "database": ":memory:",
            },
        }
        self.write_config()
        Config.reload()

        db1 = Config.database()
        db2 = Config.database()

        expect(db1).to(be(db2))

        Config.reload()
        db3 = Config.database()

        expect(db1).not_to(be(db3))

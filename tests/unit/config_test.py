from unittest import TestCase
from app import Config
from app.models import BaseModel
from expects import *
import os
import tempfile
import yaml

class TestConfig(TestCase):
    def test_getattr(self):
        config = Config()

        expect(lambda: config.foo).to(raise_error(AttributeError))
        expect(lambda: config.theme).not_to(raise_error)

    def test_from_file(self):
        test_config = {
            "theme": "foo",
            "debug": True,
        }

        os_file_handle, path = tempfile.mkstemp()
        with os.fdopen(os_file_handle, 'w') as file_handle:
            file_handle.write(yaml.dump(test_config, default_flow_style=False))

        config = Config.from_file(path)

        expect(config.theme).to(equal("foo"))
        expect(config.debug).to(be_true)

        os.remove(path)

    def test_use_sentry(self):
        no_sentry = Config(sentry_dns=None)
        expect(no_sentry.use_sentry()).to(be_false)

        has_sentry = Config(sentry_dns="https://user:pass@sentry.io/application_id")
        expect(has_sentry.use_sentry()).to(be_true)

    def test_content_directory_affects_content_directory(self):
        default_config = Config()
        expect(default_config.content_directory).to(equal(BaseModel.BASE_CONTENT_DIR))

        tempdir = tempfile.TemporaryDirectory()
        changed_config = Config(content_directory=tempdir.name)
        expect(changed_config.content_directory).to(equal(BaseModel.BASE_CONTENT_DIR))

    def test_site_generators(self):
        testdir = tempfile.TemporaryDirectory()
        config = Config(deploy_locations = {
            "test": {
                "location": testdir.name,
                "name": "Test",
                "url": "http://example.com",
            }
        })

        generators = config.site_generators()
        expect(generators).to(have_key("test"))

        test_generator = generators["test"]
        expect(test_generator.location).to(equal(testdir.name))
        expect(test_generator.name).to(equal("Test"))

        testdir.cleanup()

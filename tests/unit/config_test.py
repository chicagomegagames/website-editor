from unittest import TestCase
from app import Config
from expects import *
import os
import tempfile
import yaml

class TestConfig(TestCase):
    def test_required_options(self):
        expect(lambda: Config()).to(raise_error(KeyError, "'theme' is a required configuration option"))
        expect(lambda: Config(theme="foo")).not_to(raise_error)

    def test_getattr(self):
        config = Config(theme="foo")

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

        print(config.config)
        expect(config.theme).to(equal("foo"))
        expect(config.debug).to(be_true)

        os.remove(path)

    def test_use_sentry(self):
        no_sentry = Config(theme="foo", sentry_dns=None)
        expect(no_sentry.use_sentry()).to(be_false)

        has_sentry = Config(theme="foo", sentry_dns="https://user:pass@sentry.io/application_id")
        expect(has_sentry.use_sentry()).to(be_true)

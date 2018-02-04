from app import Config
from app.models import _Model

from orator import DatabaseManager
from orator.migrations import Migrator, DatabaseMigrationRepository
from unittest import TestCase

import os
import tempfile
import yaml

from .factories import factory


class FakeDatabase():
    def __init__(self):
        self.db_directory = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.db_directory.name, 'test.db')

        self.db_manager = DatabaseManager(self.database_configuration())

        migrations_directory = os.path.join(os.path.dirname(__file__), "..", 'migrations')

        migration_repository = DatabaseMigrationRepository(self.db_manager, "migrations")
        migration_repository.create_repository()
        migrator = Migrator(
            migration_repository,
            self.db_manager,
        )
        migrator.reset(migrations_directory)
        migrator.run(migrations_directory)

        _Model.set_connection_resolver(self.db_manager)

    def database_configuration(self):
        return {
            'default': 'test',
            'test': {
                'driver': 'sqlite',
                'database': self.db_file,
            },
        }

    def cleanup(self):
        self.db_directory.cleanup()
        _Model.set_connection_resolver(None)


class ApplicationTest(TestCase):
    def setUp(self):
        self.database = FakeDatabase()

        self.config_dir = tempfile.TemporaryDirectory()
        os.environ['CONFIG_DIR'] = self.config_dir.name

        # TODO: remove when fully database-ized
        self.content_dir = tempfile.TemporaryDirectory()

        self.config = {
            'databases': self.database.database_configuration(),
            'content_directory': self.content_dir.name,
        }

        self.write_config()

    def tearDown(self):
        self.config_dir.cleanup()
        self.content_dir.cleanup()
        self.database.cleanup()

    def write_config(self):
        with open(os.path.join(self.config_dir.name, 'application.yaml'), 'w') as handler:
            handler.write(yaml.dump(self.config, default_flow_style = False))

        Config._full_reload()

from app import Config

import orator
import inflection

class _Model(orator.Model):
    __resolver = Config.database()

    __primary_key__ = 'pk'
    __guarded__ = []

    @classmethod
    def _table_name(cls):
        return cls.__table__ or inflection.tableize(cls.__name__)

    @classmethod
    def _columns(cls):
        connection = cls.resolve_connection()
        columns = connection.get_schema_manager().list_table_columns(cls._table_name())
        return {name: column.get_type() for name, column in columns.items()}

    # HACK!!!
    #   Done to allow templates to use column names as a variable
    #       {% set column = 'pk' %}
    #       {{ user[column] }}
    def __getitem__(self, item):
        return getattr(self, item)

from .base_model import BaseModel
from .game import Game
from .page import Page
from .event import Event

from .image import Image

from .model_converter import ModelConverter

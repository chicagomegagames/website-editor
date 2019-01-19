from . import _Model
from app.utils import html_from_markdown
import yaml

class _ContentModel():
    ROUTE_PREFIX = ""
    REQUIRED_META = {}
    OPTIONAL_META = {}

    @classmethod
    def _all_meta(cls):
        if not hasattr(cls, '_all_meta_dict'):
            cls._all_meta_dict = {}

        if cls.__name__ not in cls._all_meta_dict:
            all_meta = dict(cls.OPTIONAL_META)
            all_meta.update(cls.REQUIRED_META)
            cls._all_meta_dict[cls.__name__] = all_meta

        return cls._all_meta_dict[cls.__name__]

    @classmethod
    def _convert_form(cls, form):
        new_form = {}
        for key, info in cls._all_meta().items():
            if key not in form:
                continue
            value = form[key]
            if info["type"] == "boolean":
                value = value in ["true", "True", True]
            new_form[key] = value

        return new_form

    @property
    def content(self):
        return html_from_markdown(self.markdown)


class _DatabaseModel(_Model, _ContentModel):
    @classmethod
    def all_sorted(cls):
        return cls.order_by("name", "asc").get()

class BaseModel(_DatabaseModel):
    pass

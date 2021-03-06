from app import Config
from app.utils import make_directory_tree, html_from_markdown
from app.models.base_model import _ContentModel
import os
import yaml

class FileAlreadyExistsError(Exception):
    def __init__(self, cls, filename):
        self.class_name = cls.__name__
        self.filename = filename
        self.path = os.path.join(Config.content_directory, cls.CONTENT_DIR, filename)

        super().__init__("Couldn't create {cls}, file already exists <{path}>".format(cls=self.class_name, path=self.path))

class _FileModel(_ContentModel):
    @classmethod
    def all(cls):
        path = os.path.join(Config.content_directory, cls.CONTENT_DIR)

        if not os.path.exists(path):
            os.mkdir(path)

        files = filter(os.path.isfile, [os.path.join(path, name) for name in os.listdir(path)])
        return list(map(cls, map(os.path.basename, files)))

    @classmethod
    def _sort(cls, models):
        return models

    @classmethod
    def all_sorted(cls):
        return cls._sort(cls.all())

    @classmethod
    def create(cls, filename, **kwargs):
        base_path = os.path.join(Config.content_directory, cls.CONTENT_DIR)
        if not os.path.exists(base_path):
            make_directory_tree(base_path)

        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            raise FileAlreadyExistsError(cls, filename)

        dummy_meta = cls._default_meta()

        for key, value in kwargs.items():
            if key in cls._all_meta():
                dummy_meta[key] = value

        with open(path, "w+") as writer:
            writer.write("---\n")
            writer.write(yaml.dump(dummy_meta, default_flow_style=False))
            writer.write("---\n\n")
            if "markdown" in kwargs:
                writer.write(kwargs["markdown"])
        model = cls(filename)

        for key in cls.REQUIRED_META:
            if key not in model.metadata:
                model.metadata[key] = None

        model.save(force=True)
        return model

    @classmethod
    def _default_meta(cls):
        meta = {}
        for key, details in cls._all_meta().items():
            if "default" in details and not callable(details["default"]):
                meta[key] = details["default"]
        return meta

    def __init__(self, filename, **kwargs):
        self.filename = filename
        self.path = os.path.join(Config.content_directory, self.CONTENT_DIR, filename)
        self.parse_page()
        self._valid = False
        self.errors = []

    def __str__(self):
        return "<{cls}: {path}>".format(cls=self.__class__.__name__, path=self.path)

    def __eq__(self, other):
        return self.path == other.path

    def __getattr__(self, attr):
        if attr in self.metadata:
            return self.metadata[attr]
        else:
            super().__getattr__(attr)

    @property
    def name(self):
        return self.metadata["name"]

    def set_path(self, filename):
        if "path" in self.__dict__:
            old_path = self.path
        else:
            old_path = None

        new_path = os.path.join(Config.content_directory, self.CONTENT_DIR, filename)
        if old_path == new_path:
            return

        if os.path.exists(new_path):
            raise FileAlreadyExistsError(self.__class__, filename)

        self.filename = filename
        self.path = new_path

        if old_path and os.path.exists(old_path):
            os.rename(old_path, self.path)

    def parse_page(self):
        contents = ""
        with open(self.path) as f:
            contents = "".join(f)

        content_splits = contents.split("---")
        metadata = content_splits[1]
        markdown = ("---".join(content_splits[2:])).strip()
        self.markdown = markdown

        self.metadata = self._default_meta()
        self.metadata.update(yaml.load(metadata))

    def serialize(self):
        return {
            "markdown": self.markdown,
            "metadata": self.metadata,
            "required_meta": self.REQUIRED_META,
            "optional_meta": self.OPTIONAL_META,
        }


    def validate(self):
        self.errors = []
        for key in self.REQUIRED_META:
            if key not in self.metadata or self.metadata[key] is None:
                self.errors.append("Metadata \"{key}\" is required".format(key=key))

        self._valid = self.errors == []
        return self._valid

    def update(self, **kwargs):
        if "metadata" in kwargs:
            self.metadata.update(self._convert_form(kwargs["metadata"]))

        if "markdown" in kwargs:
            if self.markdown != kwargs["markdown"]:
                self.markdown = kwargs["markdown"]

        if "filename" in kwargs:
            self.set_path(kwargs["filename"])

    def refresh(self):
        self.parse_page()
        self.validate()

    def save(self, force = False):
        if not force:
            self.validate()

            if not self._valid:
                return False

        with open(self.path, "r+") as f:
            f.seek(0)
            f.write("---\n")
            f.write(yaml.dump(
                {key: value for key, value in self.metadata.items()},
                default_flow_style=False)
            )
            f.write("---\n\n")
            f.write(self.markdown)
            f.truncate()

        return True

    def delete(self):
        os.remove(self.path)

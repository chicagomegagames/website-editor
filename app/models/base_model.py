from app.utils import make_directory_tree, html_from_markdown
import os
import yaml

class FileAlreadyExistsError(Exception):
    def __init__(self, cls, filename):
        self.class_name = cls.__name__
        self.filename = filename
        self.path = os.path.join(cls.BASE_CONTENT_DIR, cls.CONTENT_DIR, filename)

        super().__init__("Couldn't create {cls}, file already exists <{path}>".format(cls=self.class_name, path=self.path))

class BaseModel():
    BASE_CONTENT_DIR = "content"
    ROUTE_PREFIX = ""
    REQUIRED_META = {}
    OPTIONAL_META = {}

    @classmethod
    def set_base_dir(cls, directory):
        cls.BASE_CONTENT_DIR = directory

        if not os.path.exists(cls.BASE_CONTENT_DIR):
            make_directory_tree(cls.BASE_CONTENT_DIR)

    @classmethod
    def _sort(cls, models):
        return models

    @classmethod
    def all(cls):
        path = os.path.join(cls.BASE_CONTENT_DIR, cls.CONTENT_DIR)

        if not os.path.exists(path):
            os.mkdir(path)

        files = filter(os.path.isfile, [os.path.join(path, name) for name in os.listdir(path)])
        return cls._sort(list(map(cls, map(os.path.basename, files))))


    @classmethod
    def create(cls, filename, **kwargs):
        base_path = os.path.join(cls.BASE_CONTENT_DIR, cls.CONTENT_DIR)
        if not os.path.exists(base_path):
            make_directory_tree(base_path)

        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            raise FileAlreadyExistsError(cls, filename)

        dummy_meta = cls._default_meta()
        for key, value in kwargs.items():
            if key in dummy_meta:
                dummy_meta[key] = value

        with open(path, "w+") as writer:
            writer.write("---\n")
            writer.write(yaml.dump(dummy_meta, default_flow_style=False))
            writer.write("---\n\n")
            if "markdown" in kwargs:
                writer.write(kwargs["markdown"])
        model = cls(filename)
        return model

    @classmethod
    def _default_meta(cls):
        all_meta = dict(cls.OPTIONAL_META)
        all_meta.update(cls.REQUIRED_META)

        meta = {}
        for key, details in all_meta.items():
            if "default" in details:
                meta[key] = details["default"]
            else:
                meta[key] = None

        return meta

    def __init__(self, filename, **kwargs):
        self.filename = filename
        self.path = os.path.join(self.BASE_CONTENT_DIR, self.CONTENT_DIR, filename)
        self.parse_page()
        self._valid = False
        self.errors = []

    def __str__(self):
        return "<{cls}: {path}>".format(cls=self.__class__.__name__, path=self.path)

    def __getattr__(self, name):
        if "metadata" in self.__dict__ and name in self.metadata:
            return self.metadata[name]

        raise AttributeError("'{}' is not an attribute of {}".format(name, self))

    def __eq__(self, other):
        return self.path == other.path

    def set_path(self, filename):
        if "path" in self.__dict__:
            old_path = self.path
        else:
            old_path = None

        new_path = os.path.join(self.BASE_CONTENT_DIR, self.CONTENT_DIR, filename)
        if old_path == new_path:
            return

        if os.path.exists(new_path):
            raise FileAlreadyExistsError(self.__class__, filename)

        self.filename = filename
        self.path = new_path

        if old_path and os.path.exists(old_path):
            os.rename(old_path, self.path)


    def meta(self):
        meta = {}
        for name, info in self.REQUIRED_META.items():
            meta[name] = {"value": self.metadata[name], "type": info["type"]}

        for name, info in self.OPTIONAL_META.items():
            if name not in self.metadata or not self.metadata[name]:
                continue
            meta[name] = {"value": self.metadata[name], "type": info["type"]}

        return meta

    def parse_page(self):
        contents = ""
        with open(self.path) as f:
            contents = "".join(f)

        content_splits = contents.split("---")
        metadata = content_splits[1]
        markdown = ("---".join(content_splits[2:])).strip()
        self.markdown = markdown
        self.__regenerate_markdown()

        self.metadata = self._default_meta()
        self.metadata.update(yaml.load(metadata))

    def serialize(self):
        return {
            "markdown": self.markdown,
            "metadata": self.metadata,
            "required_meta": self.REQUIRED_META,
            "optional_meta": self.OPTIONAL_META,
        }

    def __regenerate_markdown(self):
        self.content = html_from_markdown(self.markdown)

    def validate(self):
        self.errors = []
        for key in self.REQUIRED_META:
            if key not in self.metadata or self.metadata[key] is None:
                self.errors.append("Metadata \"{key}\" is required".format(key=key))

        self._valid = self.errors == []
        return self._valid

    def update(self, **kwargs):
        if "metadata" in kwargs:
            for meta, value in kwargs["metadata"].items():
                if meta in self.REQUIRED_META or meta in self.OPTIONAL_META:
                    self.metadata[meta] = value

        if "markdown" in kwargs:
            if self.markdown != kwargs["markdown"]:
                self.markdown = kwargs["markdown"]
                self.__regenerate_markdown()

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

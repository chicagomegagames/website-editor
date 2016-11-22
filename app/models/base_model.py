import markdown2
import os
import os.path
import yaml
import logging

class BaseModel():
    BASE_CONTENT_DIR = "content"
    REQUIRED_META = []
    OPTIONAL_META = []

    @classmethod
    def set_base_dir(cls, directory):
        cls.BASE_CONTENT_DIR = directory

    @classmethod
    def all(cls):
        path = os.path.join(cls.BASE_CONTENT_DIR, cls.CONTENT_DIR)
        return [cls(filename) for filename in os.listdir(path)]

    @classmethod
    def create(cls, filename):
        path = os.path.join(cls.BASE_CONTENT_DIR, cls.CONTENT_DIR, filename)
        dummy_meta = {}
        for meta in cls.REQUIRED_META:
            dummy_meta[meta] = None
        with open(path, "w+") as writer:
            writer.write("---\n")
            writer.write(yaml.dump(dummy_meta, default_flow_style=False))
            writer.write("---\n\n")
        model = cls(filename)
        return model

    def __init__(self, filename, **kwargs):
        self.filename = filename
        self.path = os.path.join(self.BASE_CONTENT_DIR, self.CONTENT_DIR, filename)
        self.parse_page()
        self.__changed = False
        self.__valid = False
        self.errors = []

    def __str__(self):
        return "<{cls}: {path}>".format(cls=self.__class__.__name__, path=self.path)

    def parse_page(self):
        contents = ""
        with open(self.path) as f:
            contents = "".join(f)

        content_splits = contents.split("---")
        metadata = content_splits[1]
        markdown = "---".join(content_splits[2:])

        parsed_html = markdown2.markdown(markdown, extras=["fenced-code-blocks", "smarty-pants"])

        self.content = u"{parsed}".format(parsed=parsed_html)
        self.markdown = markdown
        self.metadata = yaml.load(metadata)

    def serialize(self):
        return {
            "markdown": self.markdown,
            "metadata": self.metadata,
            "required_meta": self.REQUIRED_META,
            "optional_meta": self.OPTIONAL_META,
        }

    def __regenerate_markdown(self):
        self.content = markdown2.markdown(self.markdown, extras=["fenced-code-blocks", "smarty-pants"])

    def validate(self):
        self.errors = []
        for key in self.REQUIRED_META:
            if key not in self.metadata or not self.metadata[key]:
                self.errors.append("Metadata \"{key}\" is required".format(key=key))

        self.__valid = self.errors == []
        return self.__valid

    def update(self, **kwargs):
        if "metadata" in kwargs:
            if self.metadata != kwargs["metadata"]:
                self.metadata = kwargs["metadata"]
                self.__changed = True

        if "markdown" in kwargs:
            if self.markdown != kwargs["markdown"]:
                self.markdown = kwargs["markdown"]
                self.__regenerate_markdown()
                self.__changed = True

    def save(self):
        self.validate()

        if not self.__changed or not self.__valid:
            return False

        with open(self.path, "r+") as f:
            f.seek(0)
            f.write("---\n")
            f.write(yaml.dump(self.metadata, default_flow_style=False))
            f.write("---\n\n")
            f.write(self.markdown)
            f.truncate()

        return True

    def delete(self):
        os.remove(self.path)

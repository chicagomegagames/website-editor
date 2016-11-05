import markdown2
import os
import os.path
import yaml

class InvalidModelError(Exception):
    def __init__(self, reason, model):
        self.reason = reason
        super().__init__("{reason}\n\tin <{classname}: {filename}>".format(reason=reason, classname=model.__class__.__name__, filename=model.filename))

class BaseModel():
    BASE_CONTENT_DIR = "content"
    REQUIRED_META = [
        "name"
    ]

    @classmethod
    def all(cls):
        path = os.path.join(cls.BASE_CONTENT_DIR, cls.CONTENT_DIR)
        return [cls(filename) for filename in os.listdir(path)]

    def __init__(self, filename):
        self.filename = filename
        self.path = os.path.join(self.BASE_CONTENT_DIR, self.CONTENT_DIR, filename)
        self.parse_page()
        self.__changed = False
        self.__valid = False
        self.errors = []

    def parse_page(self):
        contents = ""
        with open(self.path) as f:
            contents = "".join(f)

        parsed_file = markdown2.markdown(contents, extras=["fenced-code-blocks", "metadata", "smarty-pants"])

        self.content = u"{parsed}".format(parsed=parsed_file)
        self.markdown = "---".join(contents.split("---")[2:]).strip()
        self.metadata = parsed_file.metadata

    def serialize(self):
        return {
            "markdown": self.markdown,
            "metadata": self.metadata,
            "required_meta": self.REQUIRED_META,
        }

    def validate(self):
        self.errors = []
        for key in self.REQUIRED_META:
            if key not in self.metadata or not self.metadata[key]:
                self.errors.append("Metadata \"{key}\" is required".format(key=key))

        self.__valid = self.errors == []
        return self.__valid

    def save(self):
        self.validate()

        if not self.__changed or not self.__valid:
            return False

        with open(self.path, "r+") as f:
            f.seek(0)
            f.write("---\n")
            f.write(yaml.dump(self.metadata, default_flow_style=False))
            f.write("---\n\n")
            f.write(self.content)
            f.truncate()

        return True

    def update(self, **kwargs):
        if "metadata" in kwargs:
            if self.metadata != kwargs["metadata"]:
                self.metadata = kwargs["metadata"]
                self.__changed = True

        if "markdown" in kwargs:
            if self.markdown != kwargs["markdown"]:
                self.markdown = kwargs["markdown"]
                self.__changed = True

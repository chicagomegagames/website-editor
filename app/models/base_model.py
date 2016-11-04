import markdown2
import os
import os.path
import yaml

class InvalidModelError(Exception):
    def __init__(self, reason, model):
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

    def parse_page(self):
        contents = ""
        with open(self.path) as f:
            contents = "".join(f)

        parsed_file = markdown2.markdown(contents, extras=["fenced-code-blocks", "metadata", "smarty-pants"])

        self.content = u"{parsed}".format(parsed=parsed_file)
        self.metadata = parsed_file.metadata

    def validate(self):
        for key in self.REQUIRED_META:
            if key not in self.metadata:
                raise InvalidModelError("Metadata \"{key}\" not found".format(key=key), self)

    def save(self):
        self.validate()

        with open(self.path, "r+") as f:
            f.seek(0)
        f.write("---\n")
        f.write(yaml.dump(self.metadata, default_flow_style=False))
        f.write("---\n")
        f.write(self.content)
        f.truncate()

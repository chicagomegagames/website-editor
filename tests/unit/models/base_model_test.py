from app.models import BaseModel, FileAlreadyExistsError
from expects import *
from unittest import TestCase
import tempfile
import os

class Foo(BaseModel):
    CONTENT_DIR = "foo"
    REQUIRED_META = {
        "name": "text",
    }
    OPTIONAL_META = {
        "some_field": "text",
    }

class TestBaseModel(TestCase):
    def setUp(self):
        self.content_dir = tempfile.TemporaryDirectory()
        BaseModel.set_base_dir(self.content_dir.name)

    def tearDown(self):
        self.content_dir.cleanup()

    def test_all_no_directory(self):
        expect(lambda: Foo.all()).not_to(raise_error)

    def test_base_dir_not_exist(self):
        new_content_dir = os.path.join(self.content_dir.name, "notcreated")
        BaseModel.set_base_dir(new_content_dir)

        expect(lambda: Foo.create("base_model")).not_to(raise_error)

    def test_create_no_options(self):
        expect(lambda: Foo.create("filename.md")).not_to(raise_error)

    def test_create_with_meta_options(self):
        expect(lambda: Foo.create("filename.md", name = "foo file")).not_to(raise_error)
        foo = Foo("filename.md")

        expect(foo.metadata["name"]).to(equal("foo file"))

    def test_create_with_optional_meta_args(self):
        expect(lambda: Foo.create("file.md", some_field="blargity")).not_to(raise_error)
        foo = Foo("file.md")

        expect(foo.metadata["some_field"]).to(equal("blargity"))

    def test_create_two_with_same_filename(self):
        expect(lambda: Foo.create("file.md")).not_to(raise_error)
        expect(lambda: Foo.create("file.md")).to(raise_error(FileAlreadyExistsError))

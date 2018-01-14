from .test_helper import *
from app.models import BaseModel, FileAlreadyExistsError
import os
import tempfile

class Foo(BaseModel):
    CONTENT_DIR = "foo"
    REQUIRED_META = {
        "name": {"type": "text"},
    }
    OPTIONAL_META = {
        "some_field": {"type": "text"},
    }

class TestBaseModel(ApplicationTest):
    def test_all_no_directory(self):
        expect(lambda: Foo.all()).not_to(raise_error)

    def test_base_dir_not_exist(self):
        new_content_dir = os.path.join(self.content_dir.name, "notcreated")

        expect(lambda: Foo.create("base_model")).not_to(raise_error)

    def test_create_no_options(self):
        expect(lambda: Foo.create("filename.md")).not_to(raise_error)

    def test_create_with_meta_options(self):
        expect(lambda: Foo.create("filename.md", name = "foo file")).not_to(raise_error)
        foo = Foo("filename.md")

        expect(foo.metadata["name"]).to(equal("foo file"))

    def test_save(self):
        foo = Foo.create("filename.md")
        foo.metadata["name"] = "foo?"
        expect(lambda: foo.save()).not_to(raise_error)

        foo2 = Foo("filename.md")
        expect(foo2.metadata["name"]).to(equal("foo?"))

    def test_save_force(self):
        class Bar(BaseModel):
            CONTENT_DIR = "bar"
            REQUIRED_META = {"field": {"type": "text"}}

        bar = Bar.create("bar.md")
        del bar.metadata["field"]

        bar.validate()
        expect(bar._valid).to(be_false)

        expect(bar.save()).to(be_false)
        expect(bar.save(force=True)).to(be_true)

    def test_create_with_optional_meta_args(self):
        expect(lambda: Foo.create("file.md", some_field="blargity")).not_to(raise_error)
        foo = Foo("file.md")

        expect(foo.metadata["some_field"]).to(equal("blargity"))

    def test_create_with_markdown(self):
        expect(lambda: Foo.create("file.md", markdown="blah blah blah")).not_to(raise_error)
        foo = Foo("file.md")

        expect(foo.markdown).to(equal("blah blah blah"))

    def test_create_two_with_same_filename(self):
        expect(lambda: Foo.create("file.md")).not_to(raise_error)
        expect(lambda: Foo.create("file.md")).to(raise_error(FileAlreadyExistsError))

    def test_refresh(self):
        foo = Foo.create("foo.md", name="Foo!")
        foo_changer = Foo("foo.md")
        foo_changer.metadata["name"] = "Not Foo."
        expect(foo_changer.save()).to(be_true)

        expect(foo.metadata["name"]).to(equal("Foo!"))
        expect(lambda: foo.refresh()).not_to(raise_error)
        expect(foo.metadata["name"]).to(equal("Not Foo."))

    def test_update_filename(self):
        foo = Foo.create("foo.md", name = "Foo!", some_field = "soemthing cool")
        expect(foo.save()).to(be_true)
        expect(lambda: foo.update(filename="foo2.md")).not_to(raise_error)
        expect(lambda: Foo("foo2.md")).not_to(raise_error(FileNotFoundError))

        foo2 = Foo("foo2.md")
        expect(foo2).to(equal(foo))

        foo3 = Foo.create("foo3.md")
        expect(lambda: foo3.update(filename="foo2.md")).to(raise_error(FileAlreadyExistsError))

    def test_update_filename_same_name(self):
        foo = Foo.create("foo.md", name = "Foo!", some_field = "soemthing cool")
        expect(foo.save()).to(be_true)
        expect(lambda: foo.update(filename="foo.md")).not_to(raise_error)

    def test_special_character_conversion(self):
        foo = Foo.create("foo.md", name="Foo!", some_field="wut", markdown="Übeltäter")
        expect(foo.content).to(equal("<p>&#220;belt&#228;ter</p>\n"))

    def test_header_ids(self):
        foo = Foo.create("foo.md", name="foo", markdown="# Foo")
        expect(foo.content).to(equal("<h1 id=\"foo\">Foo</h1>\n"))

    def test_metadata_default(self):
        class Bar(BaseModel):
            CONTENT_DIR = "bar"
            REQUIRED_META = {
                "field": {
                    "type": "text",
                    "default": "default value",
                },
            }

        bar1 = Bar.create("bar1.md")
        expect(bar1.metadata).to(have_key("field"))
        expect(bar1.metadata["field"]).to(equal("default value"))

        bar2 = Bar.create("bar2.md", field="bar bar bar")
        expect(bar2.metadata).to(have_key("field"))
        expect(bar2.metadata["field"]).to(equal("bar bar bar"))

    def test_boolean_required_meta(self):
        class Bar(BaseModel):
            CONTENT_DIR = "bar"
            REQUIRED_META = {
                "field": {
                    "type": "boolean",
                }
            }

        bar = Bar.create("bar.md", field=False)
        expect(bar.validate()).to(be_true)

from .test_helper import *
from app.config import Config
from app.models import Page
from unittest.mock import Mock
import json
import tempfile

class DangerControllerTest(ControllerTest):
    def _setup(self):
        self.deploy_dir = tempfile.TemporaryDirectory()

        self.write_config(
            theme_directory = os.path.join(
                os.path.dirname(__file__),
                "..",
                "fixtures",
                "themes",
            ),
            theme = "test_theme",
            deploy_locations = {
                "test": {
                    "location": self.deploy_dir.name,
                    "name": "Test",
                    "url": "http://example.com",
                },
            },
        )

    def _teardown(self):
        self.deploy_dir.cleanup()

    def test_index(self):
        response = self.app.get("/danger/")
        expect(response).to(be_successful)

        expect(response).to(have_in_body("<option value=\"test_theme\">test_theme</option>"))
        expect(response).to(have_in_body("<option value=\"test\">Test</option>"))

    def test_deploy(self):
        p = factory(Page).create(slug = "/", markdown = "FOO!!")
        p.save()

        response = self.app.post("/danger/deploy",
            data = {"theme": "test_theme", "location": "test"}
        )
        expect(response).to(be_successful)

        index = os.path.join(self.deploy_dir.name, "current", "index.html")
        expect(os.path.exists(index)).to(be_true)

        index_file = open(index, "r")
        index_contents = "".join(index_file.readlines())
        index_file.close()

        expect(index_contents).to(contain("FOO!!"))

    def test_deploy_error(self):
        all_mock = Mock()
        all_mock.side_effect = Exception("Boom")
        original_all = Page.all
        Page.all = all_mock

        response = self.app.post("/danger/deploy",
            data = {"theme": "test_theme", "location": "test"}
        )

        expect(response.status_code).to(equal(500))

        Page.all = original_all

    def test_deploy_no_theme(self):
        response = self.app.post("/danger/deploy",
            data = {"location": "test"}
        )

        expect(response.status_code).to(equal(400))
        resp_body = json.loads(response.get_data(as_text=True))

        expect(resp_body).to(have_key("field"))
        expect(resp_body["field"]).to(contain("theme"))

    def test_deploy_bad_theme(self):
        response = self.app.post("/danger/deploy",
            data = {"theme": "not_a_theme", "location": "test"}
        )

        expect(response.status_code).to(equal(400))
        resp_body = json.loads(response.get_data(as_text=True))

        expect(resp_body).to(have_key("field"))
        expect(resp_body["field"]).to(contain("theme"))

    def test_deploy_no_generator(self):
        response = self.app.post("/danger/deploy",
            data = {"theme": "test_theme"}
        )

        expect(response.status_code).to(equal(400))
        resp_body = json.loads(response.get_data(as_text=True))

        expect(resp_body).to(have_key("field"))
        expect(resp_body["field"]).to(contain("location"))

    def test_deploy_bad_location(self):
        response = self.app.post("/danger/deploy",
            data = {"theme": "test_theme", "location": "doesnt_exist"}
        )

        expect(response.status_code).to(equal(400))
        resp_body = json.loads(response.get_data(as_text=True))

        expect(resp_body).to(have_key("field"))
        expect(resp_body["field"]).to(contain("location"))

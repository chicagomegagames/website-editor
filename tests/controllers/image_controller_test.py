from app import create_app, Config
from expects import *
from expects.matchers import Matcher
from unittest import TestCase
import json
import os
import tempfile

class be_successful(Matcher):
    def __init__(self):
        pass

    def _match(self, request):
        if request.status_code >= 200 and request.status_code <= 299:
            return True, ["Request was successful"]
        else:
            return False, ["Status code outside of 2xx range"]

be_successful = be_successful()


class ImageControllerTest(TestCase):
    def setUp(self):
        self.upload_dir = tempfile.TemporaryDirectory()

        current_dir = os.path.dirname(__file__)
        self.test_file_path = os.path.join(current_dir, "..", "fixtures", "square_logo.svg")

        app = create_app(Config(theme="foo", upload_path=self.upload_dir.name))
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        self.upload_dir.cleanup()

    def test_index_no_images(self):
        response = self.app.get("/images/")
        expect(response).to(be_successful)

        expect(response.get_data(as_text=True)).to(contain("No images uploaded"))

    def test_upload_image(self):
        upload_response_body = None
        with open(self.test_file_path, "rb") as test_file:
            upload_response = self.app.post("/images/upload",
                data = {"image": (test_file, "square_logo.svg")}
            )

            expect(upload_response).to(be_successful)
            upload_response_body = json.loads(upload_response.get_data(as_text=True))

        index_response = self.app.get("/images/")
        expect(index_response.get_data(as_text=True)).to(contain(upload_response_body["filename"]))


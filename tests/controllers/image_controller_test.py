from .test_helper import *

import json
import os
import tempfile

class ImageControllerTest(ControllerTest):
    def _setup(self):
        self.upload_dir = os.path.join(self.content_dir.name, 'image_uploads')

        current_dir = os.path.dirname(__file__)
        self.test_file_path = os.path.join(current_dir, "..", "fixtures", "square_logo.svg")

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
            expect(upload_response_body).to(have_key("success"))
            expect(upload_response_body["success"]).to(be_true)
            expect(upload_response_body["filename"]).to(end_with(".svg"))

        index_response = self.app.get("/images/")
        expect(index_response.get_data(as_text=True)).to(contain(upload_response_body["filename"]))


    def _upload_fixture(self):
        with open(self.test_file_path, "rb") as test_file:
            upload_response = self.app.post("/images/upload",
                data = {"image": (test_file, "square_logo.svg")}
            )

            return json.loads(upload_response.get_data(as_text=True))["filename"]

    def xtest_get_image(self):
        image = self._upload_fixture()

        response = self.app.get("/images/{}".format(image))
        expect(response).to(be_successful)

    def xtest_delete(self):
        image = self._upload_fixture()
        get_response = self.app.get("/images/")
        expect(get_response).to(be_successful)
        expect(get_response).to(have_in_body(image))

        response = self.app.post("/images/{}".format(image), data={"_method": "DELETE"})
        expect(response.status_code).to(equal(302))

        get_response = self.app.get("/images/")
        expect(get_response).to(be_successful)
        expect(get_response).not_to(have_in_body(image))

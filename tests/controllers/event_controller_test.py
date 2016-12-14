from .test_helper import *
from app import Config, create_app
from app.models import Event, BaseModel
import tempfile

class EventControllerTest(TestCase):
    def setUp(self):
        self.base_dir = tempfile.TemporaryDirectory()

        app = create_app(Config(theme = "foo", content_directory = self.base_dir.name))
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        self.base_dir.cleanup()

    def test_index_no_models(self):
        response = self.app.get("/events/")
        expect(response).to(be_successful)
        expect(response).to(have_in_body("No events created"))

    def test_index_with_models(self):
        event = Event.create(filename="january_wts.md", name="Watch the Skies", date="January 28, 2017", location="Location TBD")

        response = self.app.get("/events/")
        expect(response).to(be_successful)
        expect(response).to(have_in_body("Watch the Skies"))
        expect(response).to(have_in_body("January 28, 2017"))
        expect(response).to(have_in_body("Location TBD"))

    def test_get_new(self):
        response = self.app.get("/events/new")
        expect(response).to(be_successful)
        expect(response).to(have_in_body("new event"))
        expect(response).not_to(have_in_body("Filename"))

    def test_post_new(self):
        response = self.app.post("/events/new", data = {
            "metadata[name]": "Don's Cool Event",
            "metadata[date]": "December 20, 2016",
            "metadata[location]": "TBD",
            "markdown": "This is going to be one cool event guys.",
        })

        expect(response.status_code).to(equal(302))
        print(response.headers)
        expect(response.headers["Location"]).to(end_with("/events/"))

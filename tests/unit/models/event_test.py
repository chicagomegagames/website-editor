from app.models import Event
from .test_helper import *

class TestEvent(ModelTestCase):
    def test_extrapolate_filename(self):
        event = Event.create(name="Event Foo", date="10 January 2017", location="foo")
        expect(event.filename).to(equal("2017-01-10-event_foo.md"))

    def test_passed_in_filename(self):
        expect(lambda: Event.create(filename="event.md", name="Event Foo", date="10 January 2017", location="foo")).not_to(raise_error)
        expect(lambda: Event("event.md")).not_to(raise_error)

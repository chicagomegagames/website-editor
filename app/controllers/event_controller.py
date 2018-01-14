from .base_controller import DatabaseModelController
from app.models import Event
from flask import url_for

class EventController(DatabaseModelController):
    def __init__(self):
        super().__init__(Event, "events")

    def index(self):
        events = Event.all_sorted()
        return self.template("events/index.html", events=events)

    def _new_redirect_location(self, model):
        return url_for(".index")

    def get(self, slug):
        return self.cls.where('pk', '=', slug).first_or_fail()

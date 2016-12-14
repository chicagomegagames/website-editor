from .base_controller import ModelController
from app.models import Event
from flask import url_for

class EventController(ModelController):
    def __init__(self, site_config):
        super().__init__(Event, "events", site_config)
        self.view_options["edit_show_filename"] = False

    def index(self):
        events = Event.all()
        return self.template("events/index.html", events=events)

    def _model_create(self, form):
        event = self.cls.create(markdown=form["markdown"], **form["metadata"])
        form["filename"] = event.filename
        return event

    def _new_redirect_location(self, model):
        return url_for(".index")

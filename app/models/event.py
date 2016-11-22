from flask import render_template, Blueprint, url_for, request, redirect, jsonify
from . import BaseModel
from dateutil.parser import parse as date_parse
from datetime import date, datetime

import inspect

class Event(BaseModel):
    CONTENT_DIR = "events"
    ROUTE_PREFIX = "events"
    REQUIRED_META = [
        "name",
        "date",
        "location",
    ]

    OPTIONAL_META = [
        "time",
    ]

    @classmethod
    def all(cls):
        return sorted(super().all(), key=lambda event: event.date)

    @classmethod
    def future_events(cls):
        #events = sorted(cls.all(), key=lambda event: event.date)
        return [event for event in events if event.future_event]

    @classmethod
    def create(cls):
        filename = datetime.now().strftime("%Y-%m-%d-%H%M.md")
        return super().create(filename)

    def __init__(self, filename):
        super().__init__(filename)
        if "date" in self.metadata and self.metadata["date"]:
            self.date = date_parse(self.metadata["date"]).date()
            today = date.today()

            self.future_event = today <= self.date
        else:
            self.date = date.today()
            self.future_event = False


    @classmethod
    def _app_blueprint(cls, site_config = None):
        blueprint = Blueprint(cls.ROUTE_PREFIX, __name__, url_prefix = "/{}".format(cls.ROUTE_PREFIX))

        def _is_delete_request(request):
            if request.method == "POST" and "_method" in request.form:
                return request.form["_method"] == "DELETE"
            return False

        def template(name, **kwargs):
            if callable(site_config):
                config = site_config()
            else:
                config = site_config

            return render_template(name, site=config, prefix=cls.ROUTE_PREFIX, **kwargs)

        @blueprint.route("/")
        def all():
            return template("events.html", events=Event.all())

        @blueprint.route("/<filename>", methods=["GET", "POST"])
        def show(filename):
            model = cls(filename)

            if _is_delete_request(request):
                model.delete()
                return redirect(url_for("index"))

            return template("model.html", model=model)

        @blueprint.route("/<filename>/edit", methods=["GET", "POST"])
        def edit(filename):
            model = cls(filename)

            errors = []
            if request.method == "POST":
                # assumption: if you posted data to this route, it is
                # valid json. gorrammit.
                model.update(**request.get_json(force=True))
                if not model.validate():
                    errors = model.errors
                else:
                    model.save()

                response = {}
                if errors != []:
                    response["errors"] = errors
                    response["success"] = False
                else:
                    response["success"] = True
                    response["model"] = model.serialize()

                return jsonify(**response)

            return template("edit.html", model=model, required_meta=model.REQUIRED_META, optional_meta=model.OPTIONAL_META, errors=[])

        @blueprint.route("/new", methods=["GET"])
        def new_event():
            model = Event.create()
            return jsonify(success=True, edit_path=url_for(".edit", filename=model.filename))

        return blueprint

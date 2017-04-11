from flask import render_template, Blueprint, url_for, request, redirect, jsonify
from . import BaseModel
from dateutil.parser import parse as date_parse
from datetime import date, datetime
import re

import inspect

class Event(BaseModel):
    CONTENT_DIR = "events"
    ROUTE_PREFIX = "events"
    REQUIRED_META = {
        "name": {
            "type": "text",
            "hint": "Name of the event",
        },
        "date": {
            "type": "text",
            "hint": "Date when the event will take place (should allow most formatting)",
        },
        "location": {
            "type": "text",
            "hint": "Where the event will be held (more specific is better, but as broad as 'Chicagoland' works too)",
        },
    }

    OPTIONAL_META = {
        "time": {
            "type": "text",
            "hint": "Time when the event is scheduled to take place (ex '10:00am - 3:00pm')"
        },
    }

    @classmethod
    def all(cls):
        return sorted(super().all(), key=lambda event: event.date)

    @classmethod
    def future_events(cls):
        return [event for event in cls.all() if event.future_event]

    @classmethod
    def create(cls, **kwargs):
        if "filename" in kwargs:
            filename = kwargs["filename"]
            del kwargs["filename"]
        elif "date" in kwargs:
            date = date_parse(kwargs["date"])
            date_str = date.strftime("%Y-%m-%d")

            if "name" in kwargs:
                formated_name = re.sub(r'\ +', '_', re.sub(r'\W+', ' ', kwargs["name"].lower()).strip())
                filename = "{}-{}.md".format(date_str, formated_name)
            else:
                filename = "{}.md".format(date_str)
        else:
            filename = datetime.now().strftime("%Y-%m-%d-%H%M.md")

        return super().create(filename, **kwargs)

    def __init__(self, filename):
        super().__init__(filename)
        if "date" in self.metadata and self.metadata["date"]:
            self.date = date_parse(self.metadata["date"]).date()
            today = date.today()

            self.future_event = today <= self.date
        else:
            self.date = date.today()
            self.future_event = False

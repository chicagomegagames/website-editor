from flask import render_template, Blueprint, url_for, request, redirect, jsonify
from . import DatabaseModel
from dateutil.parser import parse as date_parse
from datetime import date, datetime
import re
import orator

import inspect

class Event(DatabaseModel):
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
    def all_sorted(cls):
        return cls.order_by("date", "asc").get()

    @classmethod
    def future_events(cls):
        today = date.today()
        return cls.where("date", ">", today).get()

    @property
    def future_event(self):
        today = date.today()

        if isinstance(self.date, str):
            return today <= date_parse(self.date).date()

        return today <= self.date

from . import BaseModel
from dateutil.parser import parse as date_parse
from datetime import date

class Event(BaseModel):
    CONTENT_DIR = "events"
    REQUIRED_META = [
        "name",
        "date",
        "location",
    ]

    OPTIONAL_META = [
        "time",
    ]

    @classmethod
    def future_events(cls):
        events = sorted(cls.all(), key=lambda event: event.date)
        return [event for event in events if event.future_event]


    def __init__(self, filename):
        super().__init__(filename)
        self.date = date_parse(self.metadata["date"]).date()
        today = date.today()

        self.future_event = today <= self.date

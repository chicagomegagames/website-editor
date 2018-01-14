from .base_controller import DatabaseModelController
from app.models import Page

class PageController(DatabaseModelController):
    def __init__(self):
        super().__init__(Page, "pages")

from .base_controller import ModelController
from app.models import Page

class PageController(ModelController):
    def __init__(self):
        super().__init__(Page, "pages")

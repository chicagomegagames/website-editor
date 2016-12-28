from .base_controller import ModelController
from app.models import Page

class PageController(ModelController):
    def __init__(self, config):
        super().__init__(Page, "pages", config)

from .base_controller import ModelController
from app.models import BlogPost

class BlogController(ModelController):
    def __init__(self):
        super().__init__(BlogPost, "blog")
        self.model_name = "Blog Post"

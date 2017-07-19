from .base_controller import ModelController
from app.models import BlogPost

class BlogController(ModelController):
    def __init__(self, config, image_service):
        super().__init__(BlogPost, "blog", config, image_service)
        self.model_name = "Blog Post"

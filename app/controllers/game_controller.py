from .base_controller import ModelController
from app.models import Game

class GameController(ModelController):
    def __init__(self, config, image_service):
        super().__init__(Game, "games", config, image_service)

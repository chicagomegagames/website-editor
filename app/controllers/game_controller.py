from .base_controller import ModelController
from app.models import Game

class GameController(ModelController):
    def __init__(self, config):
        super().__init__(Game, "games", config)

from .base_controller import ModelController
from app.models import Game

class GameController(ModelController):
    def __init__(self, site_config):
        super().__init__(Game, "games", site_config)

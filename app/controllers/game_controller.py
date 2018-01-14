from .base_controller import DatabaseModelController
from app.models import Game

class GameController(DatabaseModelController):
    def __init__(self):
        super().__init__(Game, "games")

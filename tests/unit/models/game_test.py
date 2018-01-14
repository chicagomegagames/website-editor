from app.models import Game
from .test_helper import *

class TestGame(ApplicationTest):
    def test_slug(self):
        game = factory(Game).create(name = "My Kind of Town")
        expect(game.slug).to(equal("my_kind_of_town"))

        game.update(name = "My Kind of Blarg")
        game.save()

        expect(game.slug).to(equal("my_kind_of_blarg"))

from app.models import Game
from expects import *
from unittest import TestCase

class TestGame(TestCase):
    def test_slug(self):
        game = Game.create("my_kind_of_town.md", name="My Kind of Town")
        expect(game.slug).to(equal("my_kind_of_town"))

        game.update(metadata = {"name": "My Kind of Blarg"})
        expect(game.slug).to(equal("my_kind_of_blarg"))

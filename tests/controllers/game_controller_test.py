from .test_helper import *

from app.models import Game, BaseModel
import tempfile

class GameControllerTest(ControllerTest):
    def test_index_no_models(self):
        response = self.app.get("/games/")
        expect(response).to(be_successful)
        expect(response).to(have_in_body("No games created"))

    def test_index_with_models(self):
        factory(Game).create(name = "Watch the Skies")
        factory(Game).create(name = "My Kind of Town")

        response = self.app.get("/games/")
        expect(response).to(be_successful)

        expect(response).to(have_in_body("href=\"/games/my_kind_of_town\""))
        expect(response).to(have_in_body("href=\"/games/watch_the_skies\""))
        expect(response).to(have_in_body("Watch the Skies"))
        expect(response).to(have_in_body("My Kind of Town"))

    def test_show(self):
        factory(Game).create(name = "My Kind of Town")

        response = self.app.get("/games/my_kind_of_town")
        expect(response).to(be_successful)
        expect(response).to(have_in_body("My Kind of Town"))

    def test_show_not_found(self):
        response = self.app.get("/games/no_game")
        expect(response.status_code).to(equal(404))

    def test_show_delete(self):
        factory(Game).create(name = "My Kind of Town")

        response = self.app.post("/games/my_kind_of_town", data={"_method": "DELETE"})
        expect(response.status_code).to(equal(302))
        expect(response.headers["Location"]).to(contain("/games/"))

        expect(lambda: Game.where("slug", "=", "my_kind_of_town").first_or_failure()).to(raise_error)

    def test_edit(self):
        game = factory(Game).create(name = "My Kind of Town")

        response = self.app.get("/games/my_kind_of_town/edit")
        expect(response).to(be_successful)
        expect(response).to(have_in_body("value=\"My Kind of Town\""))

        edit_response = self.app.post("/games/my_kind_of_town/edit", data = {
            "markdown": "Hello! Yes, this is dog.",
        })

        expect(edit_response).to(be_successful)

        game = game.fresh()
        expect(game.markdown).to(equal("Hello! Yes, this is dog."))

    def test_new(self):
        form_response = self.app.get("/games/new")
        expect(form_response).to(be_successful)
        expect(form_response).to(have_in_body("new game"))

        create_response = self.app.post("/games/new", data = {
            "name": "Foo, the game!",
            "markdown": "Foo is a pretty cool game that you should play.",
        })

        expect(create_response.status_code).to(equal(302))
        expect(create_response.headers["Location"]).to(end_with("/games/foo_the_game"))

        show_response = self.app.get("/games/foo_the_game")
        expect(show_response).to(be_successful)
        expect(show_response).to(have_in_body("Foo, the game!"))

    def test_edit_without_all_meta(self):
        game = factory(Game).create(name = "My Kind of Town")

        edit_response = self.app.post("/games/my_kind_of_town/edit", data = {
            "markdown": "Hello! Yes, this is dog.",
        })
        expect(edit_response).to(be_successful)

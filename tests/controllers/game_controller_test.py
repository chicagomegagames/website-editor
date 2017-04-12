from .test_helper import *

from app import Config, create_app
from app.models import Game, BaseModel
import tempfile

class GameControllerTest(TestCase):
    def setUp(self):
        self.base_dir = tempfile.TemporaryDirectory()

        app = create_app(Config(theme = "foo", content_directory = self.base_dir.name))
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        self.base_dir.cleanup()

    def test_index_no_models(self):
        response = self.app.get("/games/")
        expect(response).to(be_successful)
        expect(response).to(have_in_body("No games created"))

    def test_index_with_models(self):
        Game.create("watch_the_skies.md", name="Watch the Skies")
        Game.create("my_kind_of_town.md", name="My Kind of Town")

        response = self.app.get("/games/")
        expect(response).to(be_successful)

        expect(response).to(have_in_body("href=\"/games/my_kind_of_town.md\""))
        expect(response).to(have_in_body("href=\"/games/watch_the_skies.md\""))

    def test_show(self):
        game = Game.create("my_kind_of_town.md",
            name = "My Kind of Town",
        )

        response = self.app.get("/games/my_kind_of_town.md")
        expect(response).to(be_successful)
        expect(response).to(have_in_body("My Kind of Town"))

    def test_show_not_found(self):
        response = self.app.get("/games/no_game")
        expect(response.status_code).to(equal(404))

    def test_show_delete(self):
        game = Game.create("my_kind_of_town.md")
        response = self.app.post("/games/my_kind_of_town.md", data={"_method": "DELETE"})
        expect(response.status_code).to(equal(302))
        expect(response.headers["Location"]).to(contain("/games/"))

        expect(lambda: Game("my_kind_of_town.md")).to(raise_error(FileNotFoundError))

    def test_edit(self):
        game = Game.create("my_kind_of_town.md",
            name = "My Kind of Town",
        )

        response = self.app.get("/games/my_kind_of_town.md/edit")
        expect(response).to(be_successful)
        expect(response).to(have_in_body("value=\"My Kind of Town\""))

        edit_response = self.app.post("/games/my_kind_of_town.md/edit", data = {
            "markdown": "Hello! Yes, this is dog.",
            "metadata[hero_image]": "assets/foo.jpg",
        })

        expect(edit_response).to(be_successful)

        game.refresh()
        expect(game.markdown).to(equal("Hello! Yes, this is dog."))

    def test_edit_filename(self):
        game = Game.create("my_kind_of_town.md",
            name = "My Kind of Town",
        )

        new_game_file = "mkot.md"
        response = self.app.post("/games/my_kind_of_town.md/edit", data = {
            "filename": new_game_file,
        })

        expect(response.status_code).to(equal(302))
        expect(response.headers["Location"]).to(contain("/games/mkot.md"))

        expect(lambda: Game("my_kind_of_town.md")).to(raise_error(FileNotFoundError))
        expect(lambda: Game("mkot.md")).not_to(raise_error(FileNotFoundError))

        game2 = Game("mkot.md")
        expect(game2.name).to(equal("My Kind of Town"))

    def test_edit_filename_passed_no_change(self):
        game = Game.create("my_kind_of_town.md",
            name = "My Kind of Town",
        )

        response = self.app.post("/games/my_kind_of_town.md/edit", data = {
            "filename": "my_kind_of_town.md",
        })
        expect(response).to(be_successful)

    def test_new(self):
        form_response = self.app.get("/games/new")
        expect(form_response).to(be_successful)
        expect(form_response).to(have_in_body("new game"))

        create_response = self.app.post("/games/new", data = {
            "filename": "foo.md",
            "metadata[name]": "Foo, the game!",
            "markdown": "Foo is a pretty cool game that you should play.",
        })

        expect(create_response.status_code).to(equal(302))
        expect(create_response.headers["Location"]).to(contain("/games/foo.md"))

        show_response = self.app.get("/games/foo.md")
        expect(show_response).to(be_successful)
        expect(show_response).to(have_in_body("Foo, the game!"))

    def test_edit_without_all_meta(self):
        game = Game.create("my_kind_of_town.md",
            name = "My Kind of Town",
        )

        edit_response = self.app.post("/games/my_kind_of_town.md/edit", data = {
            "markdown": "Hello! Yes, this is dog.",
        })
        expect(edit_response).to(be_successful)

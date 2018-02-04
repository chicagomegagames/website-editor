from .test_helper import *

from app.models import ModelConverter, Page, Game, Event
from app.models.base_model import _FileModel

from datetime import date
import orator

class PageFile(_FileModel):
    CONTENT_DIR = Page.CONTENT_DIR
    REQUIRED_META = Page.REQUIRED_META
    OPTIONAL_META = Page.OPTIONAL_META

class GameFile(_FileModel):
    CONTENT_DIR = Game.CONTENT_DIR
    REQUIRED_META = Game.REQUIRED_META
    OPTIONAL_META = Game.OPTIONAL_META

class TestModelConverter(ApplicationTest):
    def test_turns_file_models_into_database_models(self):
        file_page = PageFile.create("filename.md", name = "Test Page", slug = "/test_page/", hero_image = "/path/to/image")

        ModelConverter.convert(Page)

        database_page = Page.where("slug", "=", "/test_page/").first_or_fail()

        expect(database_page.name).to(equal(file_page.metadata['name']))
        expect(database_page.slug).to(equal(file_page.metadata['slug']))
        expect(database_page.hero_image).to(equal(file_page.metadata['hero_image']))

    def test_works_for_multiple_classes(self):
        file_page = PageFile.create("filename.md", name = "Test Page", slug = "/test_page/", hero_image = "/path/to/image")
        file_game = GameFile.create("filename.md", name = "Watch the Skies", blurb = "wtf mates?")

        ModelConverter.convert(Page)
        ModelConverter.convert(Game)

        database_game = Game.where("name", "=", file_game.metadata['name']).first_or_fail()

        expect(database_game.blurb).to(equal(file_game.metadata['blurb']))

    def test_ignores_unexpected_metadata(self):
        optional_meta = Event.OPTIONAL_META
        optional_meta['game_link'] = {
            'type': 'text',
            'hint': 'who cares?',
        }

        class BadEvent(_FileModel):
            CONTENT_DIR = Event.CONTENT_DIR
            REQUIRED_META = Event.REQUIRED_META
            OPTIONAL_META = optional_meta

        today = date.today()
        bad_event = BadEvent.create(
            "file.md",
            name = "Some Cool Event",
            date = today,
            location = "A Place",
            game_link = "http://google.com",
        )

        expect(lambda: ModelConverter.convert(Event)).not_to(raise_error(orator.exceptions.query.QueryException))

        db_event = Event.where("name", "=", bad_event.metadata['name']).first_or_fail()
        expect(db_event.location).to(equal(bad_event.location))
        expect(lambda: db_event.game_link).to(raise_error(AttributeError))

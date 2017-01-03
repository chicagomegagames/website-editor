from app import GeneratorService, ImageService
from app.models import BaseModel, Page, Game
from expects import *
from freezegun import freeze_time
from unittest import TestCase
from unittest.mock import Mock
import filecmp
import tempfile
import os

TestThemePath = os.path.join(
    os.path.dirname(__file__),
    "..",
    "fixtures",
    "themes",
    "test_theme",
)

class TestGeneratorService(TestCase):
    def setUp(self):
        self.deploy_dir = tempfile.TemporaryDirectory()
        self.generator = GeneratorService(
            name = "test",
            location = self.deploy_dir.name,
            default_theme_path = TestThemePath,
        )

        self.content_dir = tempfile.TemporaryDirectory()
        BaseModel.set_base_dir(self.content_dir.name)

    def tearDown(self):
        self.deploy_dir.cleanup()
        self.content_dir.cleanup()

    def test_creates_new_deploy_dir(self):
        with freeze_time("2016-12-27 19:00:20"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        with freeze_time("2016-12-27 20:30:00"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        expect(self.generator.deploys()).to(equal(["2016-12-27_190020", "2016-12-27_203000"]))

    def test_deploy_returns_path(self):
        deploy_path = self.generator.deploy()
        expect(self.generator.deploys()).to(equal([deploy_path]))

    def test_symlinks_to_current(self):
        deploy_name = self.generator.deploy()
        deploy_path = os.path.join(self.generator.location, deploy_name)
        current_path = os.path.join(self.generator.location, "current")
        expect(os.path.realpath(current_path)).to(equal(os.path.realpath(deploy_path)))

    def test_creates_content(self):
        p = Page.create("test.md", markdown="foo!", slug="/", title="Test!")
        p.save()

        deploy_name = self.generator.deploy(theme_path = TestThemePath)

        index_file = os.path.join(self.generator.location, deploy_name, "index.html")
        expect(os.path.exists(index_file)).to(be_true)

    def test_creates_game_pages(self):
        g = Game.create("foo.md", name="Foo", markdown="This is game")
        expect(g.save()).to(be_true)

        deploy_name = self.generator.deploy(theme_path = TestThemePath)

        game_file = os.path.join(self.generator.location, deploy_name, "games", "foo", "index.html")
        expect(os.path.exists(game_file)).to(be_true)

    def test_copy_assets(self):
        deploy_name = self.generator.deploy(theme_path = TestThemePath)
        deployed_logo = os.path.join(self.generator.location, deploy_name, "assets", "logo.svg")
        expect(os.path.exists(deployed_logo)).to(be_true)

        test_logo = os.path.join(TestThemePath, "assets", "logo.svg")
        expect(filecmp.cmp(deployed_logo, test_logo)).to(be_true)

    def test_copy_image_service(self):
        image_upload_path = tempfile.TemporaryDirectory()
        image_service = ImageService(upload_path = image_upload_path.name)
        image_to_upload = os.path.join(os.path.dirname(__file__), "..", "fixtures", "square_logo.svg")
        upload_image = None
        with open(image_to_upload, "rb") as upload_file:
            upload_image = image_service.upload_image("square_logo.svg", upload_file)

        deploy_name = self.generator.deploy(
            theme_path = TestThemePath,
            image_service = image_service,
        )

        image_path = upload_image.path
        expect(os.path.exists(image_path)).to(be_true)
        expect(filecmp.cmp(image_path, image_to_upload))

        image_upload_path.cleanup()

    def test_rollsback_failures(self):
        all_mock = Mock()
        all_mock.side_effect = Exception("Boom")
        original_all = Page.all

        with freeze_time("2016-12-27 19:00:20"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        with freeze_time("2016-12-28 20:30:00"):
            Page.all = all_mock
            expect(lambda: self.generator.deploy()).to(raise_error(Exception, "Boom"))
            Page.all = original_all

        expect(self.generator.deploys()).to(equal(["2016-12-27_190020"]))

    def test_removes_old_deploys(self):
        with freeze_time("2016-12-27 00:00:10"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        with freeze_time("2016-12-27 00:00:20"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        with freeze_time("2016-12-27 00:00:30"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        with freeze_time("2016-12-27 00:00:40"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        with freeze_time("2016-12-27 00:00:50"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        with freeze_time("2016-12-27 00:01:00"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)

        expect(self.generator.deploys()).to(equal([
            "2016-12-27_000020",
            "2016-12-27_000030",
            "2016-12-27_000040",
            "2016-12-27_000050",
            "2016-12-27_000100",
        ]))

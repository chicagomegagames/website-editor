from app import GeneratorService, Config, Deploy
from app.models import BaseModel, Page, Game

from .. import ApplicationTest, factory
from expects import *
from freezegun import freeze_time
from moto import mock_s3
from unittest import TestCase
from unittest.mock import Mock
import filecmp
import tempfile
import os
import yaml

TestThemePath = os.path.join(
    os.path.dirname(__file__),
    "..",
    "fixtures",
    "themes",
    "test_theme",
)

@mock_s3
class TestGeneratorService(ApplicationTest):
    def setUp(self):
        super().setUp()

        self.deploy_dir = tempfile.TemporaryDirectory()
        self.generator = GeneratorService(
            name = "test",
            location = self.deploy_dir.name,
            default_theme_path = TestThemePath,
        )

    def tearDown(self):
        super().tearDown()

        self.deploy_dir.cleanup()

    def test_creates_new_deploy_dir(self):
        with freeze_time("2016-12-27 19:00:20"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        with freeze_time("2016-12-27 20:30:00"):
            expect(lambda: self.generator.deploy()).not_to(raise_error)
        expect(self.generator.deploys()).to(equal(["2016-12-27_190020", "2016-12-27_203000"]))

    def test_deploy_returns_path(self):
        deploy_path = self.generator.deploy(theme_path = TestThemePath)
        expect(self.generator.deploys()).to(equal([deploy_path]))

    def test_deploy_uses_default_theme_path(self):
        generator1 = GeneratorService(
            name = "test1",
            location = os.path.join(self.deploy_dir.name, "test1"),
            default_theme_path = TestThemePath,
        )

        expect(
            lambda: generator1.deploy()
        ).not_to(raise_error(NameError))


        generator2 = GeneratorService(
            name = "test2",
            location = os.path.join(self.deploy_dir.name, "test2"),
        )

        expect(
            lambda: generator2.deploy()
        ).to(raise_error(NameError))

    def test_symlinks_to_current(self):
        deploy_name = self.generator.deploy()
        deploy_path = os.path.join(self.generator.location, deploy_name)
        current_path = os.path.join(self.generator.location, "current")
        expect(os.path.realpath(current_path)).to(equal(os.path.realpath(deploy_path)))

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


class TestDeploy(ApplicationTest):
    def setUp(self):
        super().setUp()

        self.deploy_dir = tempfile.TemporaryDirectory()
        self.theme_path = TestThemePath

    def tearDown(self):
        super().tearDown()

        self.deploy_dir.cleanup()

    def test_creates_content(self):
        deployer = Deploy(
            deploy_dir = self.deploy_dir.name,
            theme_path = self.theme_path,
        )

        p = factory(Page).create(slug = "/")
        p.save()

        deployer.deploy()

        index_file = os.path.join(deployer.path, "index.html")
        expect(os.path.exists(index_file)).to(be_true)

    def test_creates_game_pages(self):
        deployer = Deploy(
            deploy_dir = self.deploy_dir.name,
            theme_path = self.theme_path,
        )

        g = factory(Game).create(name = "Foo", markdown = "This is game")
        g.save()

        deployer.deploy()

        game_file = os.path.join(deployer.path, "games", "foo", "index.html")
        expect(os.path.exists(game_file)).to(be_true)

    def test_copy_assets(self):
        deployer = Deploy(
            deploy_dir = self.deploy_dir.name,
            theme_path = self.theme_path,
        )

        deployer.deploy()

        deployed_logo = os.path.join(deployer.path, "assets", "logo.svg")
        expect(os.path.exists(deployed_logo)).to(be_true)

        test_logo = os.path.join(self.theme_path, "assets", "logo.svg")
        expect(filecmp.cmp(deployed_logo, test_logo)).to(be_true)

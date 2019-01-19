from datetime import datetime
from app import Config
from app.models import Page, Game, Event
from app.utils import make_directory_tree, html_from_markdown
import jinja2
import os
import shutil

class Deploy():
    def __init__(self, deploy_dir = None, theme_path = None):
        self.path = deploy_dir
        self.theme_path = theme_path

        self.template_environment = jinja2.Environment(
            loader = jinja2.FileSystemLoader(os.path.join(theme_path, 'templates'))
        )
        self.template_environment.filters["markdown"] = lambda x: html_from_markdown(str(x))

    def deploy(self):
        pages = Page.all()
        games = Game.all()
        calendar = Event.future_events()

        self.site = {"games": games, "pages": pages, "calendar": calendar}

        for page in pages:
            self._create_page(page, page.slug, page.layout)

        for game in games:
            slug = game.slug
            while len(slug) > 0 and slug[0] == "/":
                slug = slug[1:]
            slug = os.path.join("games", slug)

            self._create_page(game, slug, game.layout)

        assets_dir = os.path.join(self.theme_path, "assets")
        if os.path.exists(assets_dir):
            copy_dir = os.path.join(self.path, "assets")
            if os.path.exists(copy_dir):
                shutil.rmtree(copy_dir)
            shutil.copytree(assets_dir, copy_dir)

    def _create_page(self, model, slug, template_name):
        while len(slug) > 0 and slug[0] == "/":
            slug = slug[1:]

        output_dir = os.path.join(self.path, slug)
        output_file = os.path.join(output_dir, "index.html")
        make_directory_tree(output_dir)

        template = self.template_environment.get_template(template_name)
        with open(output_file, "w+") as writer:
            writer.write(template.render(page=model, site=self.site))

    def _render(self, template_name, **context):
        template = self.template_environment.get_template(template_name)
        return template.render(
            asset=lambda x: "{base}/{asset}".format(base = "/assets", asset = x),
            url=lambda x: "/{url}".format(url=x),
            **context,
        )


class GeneratorService(object):
    @classmethod
    def all(cls):
        return {
            key: cls(
                key = key,
                name = cfg["name"],
                location = cfg["location"],
                default_theme_path = os.path.join(Config.content_directory, "themes", Config.theme),
            ) for key, cfg in Config.deploy_locations.items()
        }

    def __init__(self, name, location, key = None, default_theme_path = None):
        self.key = key
        self.name = name
        self.location = location
        self.default_theme_path = default_theme_path

        self.template_environment = None

    def deploys(self):
        all_deploys = os.listdir(self.location)
        all_deploys.remove("current")
        all_deploys.sort()
        return all_deploys


    def deploy(self, theme_path = None):
        if not theme_path:
            if not self.default_theme_path:
                raise NameError("No theme_path or default_theme_path set")
            theme_path = self.default_theme_path

        now = datetime.now()
        directory_name = now.strftime("%Y-%m-%d_%H%M%S")

        path = os.path.join(self.location, directory_name)
        os.mkdir(path)

        try:
            deploy = Deploy(
                deploy_dir = path,
                theme_path = theme_path
            )
            deploy.deploy()

            self.symlink_deploy(directory_name)
            self.cleanup_old_deploys()

            return directory_name
        except Exception as e:
            shutil.rmtree(path)
            raise e

    def symlink_deploy(self, deploy):
        current_path = os.path.join(self.location, "current")
        deploy_path = os.path.join(self.location, deploy)
        if os.path.exists(current_path):
            os.remove(current_path)
        os.symlink(deploy_path, current_path)

    def cleanup_old_deploys(self):
        deploys = self.deploys()
        deploys.sort(reverse=True)

        real_current_path = os.path.realpath(os.path.join(self.location, "current"))
        for deploy in deploys[5:]:
            deploy_path = os.path.join(self.location, deploy)
            real_deploy_path = os.path.realpath(deploy_path)

            if real_current_path != real_deploy_path:
                shutil.rmtree(deploy_path)

from datetime import datetime
from app.models import Page, Game, Event
from app.utils import make_directory_tree, html_from_markdown
import jinja2
import os
import shutil

class GeneratorService(object):
    def __init__(self, name, location, key = None, default_theme_path = None):
        self.key = key
        self.name = name
        self.location = location
        self.default_theme_path = default_theme_path

    def deploys(self):
        all_deploys = os.listdir(self.location)
        all_deploys.remove("current")
        all_deploys.sort()
        return all_deploys

    def generate(self, path, theme_path = None, image_service = None):
        if theme_path is None:
            theme_path = self.default_theme_path

        template_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(theme_path, "templates"))
        )

        template_environment.filters["markdown"] = lambda x: html_from_markdown(str(x))

        pages = Page.all()
        games = Game.all()
        calendar = Event.future_events()
        site = {"games": games, "pages": pages, "calendar": calendar}

        pages_to_generate = list(pages)
        for game in games:
            slug = game.slug
            while len(slug) > 0 and slug[0] == "/":
                slug = slug[1:]
            game.metadata["slug"] = os.path.join("games", slug)
            pages_to_generate.append(game)

        for page in pages_to_generate:
            slug = page.metadata["slug"]
            while len(slug) > 0 and slug[0] == "/":
                slug = slug[1:]

            output_dir = os.path.join(path, slug)
            output_file = os.path.join(output_dir, "index.html")
            make_directory_tree(output_dir)

            if "layout" in page.metadata and page.metadata["layout"]:
                layout = page.metadata["layout"]
            else:
                layout = "page.html"
            template = template_environment.get_template(layout)
            with open(output_file, "w+") as writer:
                writer.write(template.render(page=page, site=site))

        assets_dir = os.path.join(theme_path, "assets")
        if os.path.exists(assets_dir):
            copy_dir = os.path.join(path, "assets")
            if os.path.exists(copy_dir):
                shutil.rmtree(copy_dir)
            shutil.copytree(assets_dir, copy_dir)

        if image_service:
            img_dir = os.path.join(path, "images")
            if os.path.exists(img_dir):
                shutil.rmtree(img_dir)
            shutil.copytree(image_service.upload_path, img_dir)

    def deploy(self, theme_path = None, image_service = None):
        now = datetime.now()
        directory_name = now.strftime("%Y-%m-%d_%H%M%S")

        path = os.path.join(self.location, directory_name)
        os.mkdir(path)

        try:
            self.generate(path, theme_path=theme_path, image_service=image_service)
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

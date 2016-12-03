import os
import jinja2
import shutil
from .models import Game, Page, Event
from .utils import make_directory_tree

def publish_site(location=os.path.join(os.getcwd(), "_site"), theme="default"):
    errors = []

    if os.path.exists(location):
        root, dirs, files = next(os.walk(location))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

        for f in files:
            os.remove(os.path.join(root, f))

    make_directory_tree(location)

    theme_dir = os.path.join(os.getcwd(), "content", "themes", theme)
    templ_dir = os.path.join(theme_dir, "templates")
    templ_env = jinja2.Environment(loader=jinja2.FileSystemLoader(templ_dir))

    pages = Page.all()
    games = Game.all()
    calendar = Event.future_events()
    site = {"games": games, "pages": pages, "calendar": calendar}

    pages_to_generate = list(pages)
    for game in games:
        slug = game.metadata["slug"]
        if slug[0] == "/":
            slug = slug[1:]

        game.metadata["slug"] = os.path.join("games", slug)
        pages_to_generate.append(game)

    for page in pages_to_generate:
        slug = page.metadata["slug"]
        if slug[0] == "/":
            slug = slug[1:]

        output_directory = os.path.join(location, slug)
        output_file = os.path.join(output_directory, "index.html")
        make_directory_tree(output_directory)

        if "layout" in page.metadata and page.metadata["layout"]:
            layout = page.metadata["layout"]
        else:
            layout = "page.html"

        try:
            template = templ_env.get_template(layout)
            with open(output_file, "w+") as writer:
                writer.write(template.render(site=site, page=page))
        except jinja2.exceptions.TemplateNotFound as e:
            error = "Template not found `{}` for `{}`".format(layout, slug)
            errors.append(error)
            return error

    assets_dir = os.path.join(theme_dir, "assets")
    if os.path.exists(assets_dir):
        shutil.copytree(assets_dir, os.path.join(location, "assets"))

    return None

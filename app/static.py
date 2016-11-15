import os
import jinja2
import shutil
from .models import Game, Page

def publish_site(location=os.path.join(os.getcwd(), "_site"), theme="default"):
    if os.path.exists(location):
        #shutil.rmtree(location)
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
    site = {"games": games, "pages": pages}

    for page in pages:
        slug = page.metadata["slug"]
        if slug[0] == "/":
            slug = slug[1:]

        output_directory = os.path.join(location, slug)
        output_file = os.path.join(output_directory, "index.html")
        make_directory_tree(output_directory)

        if "layout" in page.metadata:
            layout = page.metadata["layout"]
        else:
            layout = "default.html"

        template = templ_env.get_template(layout)
        with open(output_file, "w+") as writer:
            writer.write(template.render(site=site, page=page))

    assets_dir = os.path.join(theme_dir, "assets")
    if os.path.exists(assets_dir):
        shutil.copytree(assets_dir, os.path.join(location, "assets"))

def make_directory_tree(path):
    if not os.path.exists(path):
        make_directory_tree(os.path.dirname(path))
        os.mkdir(path)

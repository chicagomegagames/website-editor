from app import Config
from app.models import Page, Game, Event
from app.utils import html_from_markdown
from pathlib import Path
import jinja2

class PreviewService(object):
    def __init__(self, theme):
        self.theme = theme
        self.theme_path = Path(Config.content_directory) / "themes" / theme
        self.environment = jinja2.Environment(
            loader = jinja2.FileSystemLoader(str(self.theme_path / "templates"))
        )
        self.environment.filters["markdown"] = lambda x: html_from_markdown(str(x))

    def _render(self, template_name, **context):
        template = self.environment.get_template(template_name)
        return template.render(
            asset=lambda x: "{base}/{asset}".format(base = "/preview/assets", asset = x),
            url=lambda x: "{base}/{url}".format(base = "/preview", url = x),
            **context,
        )

    def rendered_page(self, path):
        site = {
            "games": Game.all(),
            "pages": Page.all(),
            "calendar": Event.future_events(),
        }

        # is game?
        if path.startswith("games/"):
            # remove trailing slash
            slug = "/".join(path.split("/")[1:])
            game = Game.where("slug", "=", slug).first()

            if game:
                return self._render(game.layout, page=game, site=site)

        # not game
        if path != "/":
            path = "/{}/".format(path)
        page = Page.where("slug", "=", path).first()
        if page:
            return self._render(page.layout, page=page, site=site)

        return None

from . import DatabaseModel
import re

class Game(DatabaseModel):
    CONTENT_DIR = "games"
    ROUTE_PREFIX = "game"
    REQUIRED_META = {
        "name": {
            "type": "text",
            "hint": "The name of the game",
        },
        "show_quick_facts": {
            "type": "boolean",
            "hint": "Should the 'Quick Facts' block be visible?",
            "default": False,
        },
        "hidden": {
            "type": "boolean",
            "hint": "Should this game be shown on the All Games page?",
            "default": True,
        },
        "layout": {
            "type": "text",
            "hint": "filename of the template this page should be rendered with (ex 'page.html', 'game.html')",
            "default": "game.html",
        },
    }

    OPTIONAL_META = {
        "blurb": {
            "type": "markdown",
            "hint": "(markdown) Short blurb for the All Games page",
        },
        "control_count": {
            "type": "text",
            "hint": "The number of Control this game requires (ex '5-8')",
        },
        "credits": {
            "type": "markdown",
            "hint": "(markdown) Who built the game, and what they contributed",
        },
        "game_length": {
            "type": "text",
            "hint": "How long this game typically lasts (ex '5 hours')",
        },
        "hero_image": {
            "type": "image",
            "hint": "The big image that goes behind the name and subtitle",
        },
        "logo_image": {
            "type": "image",
            "hint": "Game logo (if one exists)",
        },
        "player_count": {
            "type": "text",
            "hint": "The number of players this game supports (ex '40-50')",
        },
        "preview_image": {
            "type": "image",
            "hint": "The image used on the All Games page for this game",
        },
        "subtitle": {
            "type": "text",
            "hint": "Subtitle for the game (ex 'the Chicago-style zombie survival megagame')",
        },
    }

    @property
    def logo_or_title(self):
        if self.logo_image:
            return "<img src='{}' alt='{}' />".format(self.logo_image, self.name)
        else:
            return self.name

    def save(self, **kwargs):
        if self.name:
            self.slug = re.sub(r'\ +', '_', re.sub(r'\W+', ' ', self.name.lower()).strip())
        return super().save(**kwargs)

from . import BaseModel
import re

class Game(BaseModel):
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
    }

    OPTIONAL_META = {
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
        "layout": {
            "type": "text",
            "hint": "filename of the template this page should be rendered with (ex 'page.html', 'game.html')",
            "default": "game.html",
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
        }
    }

    @classmethod
    def _sort(cls, models):
        return sorted(models, key=lambda m: m.metadata["name"])

    def generated_slug(self):
        return re.sub(r'\ +', '_', re.sub(r'\W+', ' ', self.metadata["name"].lower()).strip())

    @property
    def slug(self):
        if "slug" in self.metadata:
            return self.metadata["slug"]
        else:
            return self.generated_slug()

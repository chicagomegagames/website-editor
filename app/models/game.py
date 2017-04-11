from . import BaseModel
import re

class Game(BaseModel):
    CONTENT_DIR = "games"
    ROUTE_PREFIX = "game"
    REQUIRED_META = {
        "name": {"type": "text"},
    }

    OPTIONAL_META = {
        "control_count": {"type": "text"},
        "credits": {"type": "markdown"},
        "game_length": {"type": "text"},
        "hero_alt": {"type": "text"},
        "hero_caption": {"type": "text"},
        "hero_image": {"type": "image"},
        "layout": {"type": "text"},
        "player_count": {"type": "text"},
        "preview_image": {"type": "image"},
    }

    @classmethod
    def _sort(cls, models):
        return sorted(models, key=lambda m: m.metadata["name"])

    def generated_slug(self):
        return re.sub(r'\ +', '_', re.sub(r'\W+', ' ', self.name.lower()).strip())

    def __getattr__(self, name):
        if name == "slug":
            return self.generated_slug()

        return super().__getattr__(name)

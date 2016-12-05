from . import BaseModel
import re

class Game(BaseModel):
    CONTENT_DIR = "games"
    ROUTE_PREFIX = "game"
    REQUIRED_META = {
        "name": {"type": "text"},
    }

    OPTIONAL_META = {
        "hero_image": {"type": "image"},
        "hero_alt": {"type": "text"},
        "hero_caption": {"type": "text"},
        "layout": {"type": "text"},
    }

    def generated_slug(self):
        return re.sub(r'\ +', '_', re.sub(r'\W+', ' ', self.name.lower()).strip())

    def __getattr__(self, name):
        if name == "slug":
            return self.generated_slug()

        return super().__getattr__(name)

from . import BaseModel

class Game(BaseModel):
    CONTENT_DIR = "games"
    ROUTE_PREFIX = "game"
    REQUIRED_META = {
        "name": {"type": "text"},
        "slug": {"type": "text"},
    }

    OPTIONAL_META = {
        "hero_image": {"type": "image"},
        "hero_alt": {"type": "text"},
        "hero_caption": {"type": "text"},
        "layout": {"type": "text"},
    }

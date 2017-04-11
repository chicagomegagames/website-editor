from . import BaseModel

class Page(BaseModel):
    CONTENT_DIR = "pages"
    ROUTE_PREFIX = "page"

    REQUIRED_META = {
        "name": {"type": "text"},
        "slug": {"type": "text"},
        "layout": {"type": "text"},
    }

    OPTIONAL_META = {
        "hero_image": {"type": "image"},
        "hero_alt": {"type": "text"},
        "hero_caption": {"type": "text"},
    }

    @classmethod
    def _sort(cls, models):
        return sorted(models, key=lambda m: m.metadata["slug"])

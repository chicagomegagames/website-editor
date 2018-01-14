from . import DatabaseModel

class Page(DatabaseModel):
    CONTENT_DIR = "pages"
    ROUTE_PREFIX = "page"

    REQUIRED_META = {
        "name": {
            "type": "text",
            "hint": "Page name (also used as the title)",
        },
        "slug": {
            "type": "text",
            "hint": "URL slug for the page (ex '/' for the index, '/about/faq/', can be multi-level)",
        },
        "layout": {
            "type": "text",
            "hint": "layout to be used for the page (ex 'page.html')",
            "default": "page.html",
        },
    }

    OPTIONAL_META = {
        "hero_image": {
            "type": "image",
            "hint": "Big, lead-in image",
        },
    }

    @classmethod
    def _sort(cls, models):
        return sorted(models, key=lambda m: m.metadata["slug"])

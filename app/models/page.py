from . import BaseModel

class Page(BaseModel):
    CONTENT_DIR = "pages"
    ROUTE_PREFIX = "page"
    REQUIRED_META = list(BaseModel.REQUIRED_META)
    REQUIRED_META.extend([
        "name",
        "slug",
        "layout",
    ])

    OPTIONAL_META = [
        "hero_image",
        "hero_alt",
        "hero_caption",
    ]

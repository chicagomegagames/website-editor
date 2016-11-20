from . import BaseModel

class Game(BaseModel):
    CONTENT_DIR = "games"
    REQUIRED_META = list(BaseModel.REQUIRED_META)
    REQUIRED_META.extend([
        "name",
        "slug",
    ])

    OPTIONAL_META = [
        "hero_imgage",
        "hero_alt",
        "hero_caption",
        "layout"
    ]

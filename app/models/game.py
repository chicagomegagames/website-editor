from . import BaseModel

class Game(BaseModel):
    CONTENT_DIR = "games"
    REQUIRED_META = list(BaseModel.REQUIRED_META)
    REQUIRED_META.append("image")
    REQUIRED_META.append("name")

    def __init__(self, filename):
        self.filename = filename
        super().__init__(filename)

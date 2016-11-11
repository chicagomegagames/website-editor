from . import BaseModel

class Page(BaseModel):
    CONTENT_DIR = "pages"
    REQUIRED_META = list(BaseModel.REQUIRED_META)
    REQUIRED_META.append("slug")
    REQUIRED_META.append("layout")
    REQUIRED_META.append("title")

    def __init__(self, filename):
        self.filename = filename
        super().__init__(filename)

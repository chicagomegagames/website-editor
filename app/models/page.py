from . import BaseModel

class Page():
  CONTENT_DIR = "pages"

  def __init__(self, name, **kwargs):
    self.name = name



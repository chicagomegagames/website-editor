from . import FileModel
from dateutil.parser import parse as date_parse
import datetime

class BlogPost(FileModel):
    CONTENT_DIR = "blog"
    ROUTE_PREFIX = "blog"

    REQUIRED_META = {
        "title": {
            "type": "text",
            "hint": "Blog post title",
        },
        "date": {
            "type": "date",
            "hint": "Publication date for the post",
            "default": lambda x: datetime.datetime.now().strftime("%Y-%m-%d"),
        },
        "author_name": {
            "type": "text",
        }
    }

    OPTIONAL_META = {
        "author_email": {
            "type": "email",
            "hint": "Author's email, uses gravatar to get an avatar",
        },
        "header_image": {
            "type": "image",
            "hint": "Used behind the title, and as a preview image",
        }
    }

    @classmethod
    def _sort(cls, models):
        return sorted(models, key=lambda x: x.date)

    @property
    def name(self):
        return self.metadata["title"]

    @property
    def date(self):
        return date_parse(self.metadata["date"]).date()

    @property
    def slug(self):
        return "/blog/{}/{}/".format(
            self.date().strftime("%Y/%m/%d"),
            re.sub(r'\ +', '_', re.sub(r'\W+', ' ', self.metadata["title"].lower()).strip())
        )

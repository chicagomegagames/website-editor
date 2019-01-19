from .base_controller import BaseController
from flask import send_from_directory

class PreviewController(BaseController):
    def __init__(self, preview_service):
        super().__init__("preview")
        self.preview_service = preview_service

        self.route('/', defaults={'path': '/'})(self.preview)
        self.route("/assets/<path:path>")(self.asset)
        self.route("/<path:path>")(self.preview)

    def preview(self, path):
        print(path)
        rendered = self.preview_service.rendered_page(path)
        if rendered:
            return rendered
        else:
            return self._template("404.html"), 404

    def asset(self, path):
        return send_from_directory(str(self.preview_service.theme_path / "assets"), path)

from .base_controller import BaseController
from app import ImageService
from flask import request, jsonify, send_file, redirect, url_for

class ImageController(BaseController):
    def __init__(self):
        super().__init__("images")

        self.route("/")(self.index)
        self.route("/upload", methods=["POST"])(self.upload)
        self.route("/<filename>", methods=["GET", "POST"])(self.show)

    def index(self):
        images = ImageService.images()
        return self.template("images/index.html", images=images)

    def upload(self):
        upload_image = request.files["image"]
        image = ImageService.upload_image(upload_image.filename, upload_image.stream)

        return jsonify(filename=image.name, success=True)

    def show(self, filename):
        image = ImageService.find(filename)

        if self.is_delete_request():
            image.delete()
            return redirect(url_for(".index"))

        return send_file(image.path)

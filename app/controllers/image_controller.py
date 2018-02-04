from .base_controller import BaseController
from app import config
from app.models import Image
from flask import request, jsonify, send_file, redirect, url_for

class ImageController(BaseController):
    def __init__(self):
        super().__init__("images")

        self.route("/")(self.index)
        self.route("/upload", methods=["POST"])(self.upload)

    def index(self):
        images = Image.all()
        return self.template("images/index.html", images=images)

    def upload(self):
        upload_image = request.files["image"]
        image = self.image_service.upload_image(upload_image.filename, upload_image.stream)

        return jsonify(filename=image.name, success=True)

from flask import Blueprint, request, jsonify

class ImageController(Blueprint):
    def __init__(self, image_service = None):
        super().__init__("images", __name__, url_prefix = "/images")

        self.image_service = image_service

        self.route("/")(self.index)
        self.route("/upload", methods=["POST"])(self.upload)

    def index(self):
        images = self.image_service.images()
        if images:
            return jsonify([image.name for image in images])
        else:
            return "No images uploaded"

    def upload(self):
        upload_image = request.files["image"]
        image = self.image_service.upload_image(upload_image.name, upload_image.stream)

        return jsonify(filename=image.name)

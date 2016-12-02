from flask import Blueprint, request, jsonify

class ImageController(object):
    def __init__(self, image_service = None):
        self.image_service = image_service

    def _blueprint(self):
        blueprint = Blueprint("images", __name__, url_prefix = "/images")

        #blueprint.route("/", self.index)
        blueprint.add_url_rule("/", "index", self.index)
        blueprint.add_url_rule("/upload", "upload", self.upload, methods=["POST"])

        return blueprint

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

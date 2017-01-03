from .base_controller import BaseController
from flask import request, jsonify

class DangerController(BaseController):
    def __init__(self, config, image_service = None):
        super().__init__("danger", config)

        self.image_service = image_service
        self.generators = config.site_generators()

        self.route("/")(self.index)
        self.route("/deploy", methods=["POST"])(self.deploy)

    def index(self):
        themes = list(self.config.themes().keys())
        if self.config.theme and self.config.theme in themes:
            default_theme = self.config.theme
            themes.remove(default_theme)
        else:
            default_theme = None

        return self.template("danger/index.html", generators=self.generators.values(), themes=themes, default_theme=default_theme)

    def deploy(self):
        if "location" not in request.form:
            return jsonify(success=False, message="No location specified", field="location"), 400
        generator_key = request.form["location"]

        if generator_key not in self.generators:
            return jsonify(success=False, message="That deploy location doesn't exist", field="location"), 400

        if "theme" not in request.form:
            return jsonify(success=False, message="No theme specified", field="theme"), 400
        theme_name = request.form["theme"]
        all_themes = self.config.themes()

        if theme_name not in all_themes:
            return jsonify(success=False, message="Theme not found", field="theme"), 400
        theme_path = all_themes[theme_name]

        try:
            self.generators[generator_key].deploy(theme_path = theme_path, image_service = self.image_service)
        except Exception as e:
            self.config.capture_exception(e)
            return jsonify(success=False, message="An error occurred when trying to deploy the site. No changes have been made, and your friendly neighborhood administrator has been alerted."), 500

        return jsonify(success=True), 200

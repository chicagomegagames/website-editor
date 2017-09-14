from .base_controller import BaseController
from app import Config, GeneratorService
from flask import request, jsonify

class DangerController(BaseController):
    def __init__(self):
        super().__init__("danger")

        self.route("/")(self.index)
        self.route("/deploy", methods=["POST"])(self.deploy)
        self.route("/error")(self.error)

    def index(self):
        themes = list(Config.themes().keys())
        if Config.theme and Config.theme in themes:
            default_theme = Config.theme
            themes.remove(default_theme)
        else:
            default_theme = None

        return self.template("danger/index.html", generators=GeneratorService.all().values(), themes=themes, default_theme=default_theme)

    def deploy(self):
        if "location" not in request.form:
            return jsonify(success=False, message="No location specified", field="location"), 400
        generator_key = request.form["location"]

        if generator_key not in GeneratorService.all():
            return jsonify(success=False, message="That deploy location doesn't exist", field="location"), 400

        if "theme" not in request.form:
            return jsonify(success=False, message="No theme specified", field="theme"), 400
        theme_name = request.form["theme"]
        all_themes = Config.themes()

        if theme_name not in all_themes:
            return jsonify(success=False, message="Theme not found", field="theme"), 400
        theme_path = all_themes[theme_name]

        try:
            GeneratorService.all()[generator_key].deploy(theme_path = theme_path)
        except Exception as e:
            Config.capture_exception(e)
            return jsonify(success=False, message="An error occurred when trying to deploy the site. No changes have been made, and your friendly neighborhood administrator has been alerted."), 500

        return jsonify(success=True), 200

    def error(self):
        raise Exception("Test exception to confirm everything's working as intended")

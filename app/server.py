from flask import Flask, render_template, request, jsonify, redirect, url_for
from raven.contrib.flask import Sentry
from .controllers import ImageController, GameController, PageController, EventController, DangerController
from .image_service import ImageService
from .models import BaseModel, Game, Page, Event
from .static import publish_site
import os
import raven
import sys

def create_app(config = None):
    app = Flask("megagame editor")
    if config.use_sentry():
        app.config["SENTRY_CONFIG"] = {
            "release": raven.fetch_git_sha(os.getcwd()),
            "environment": config.environment,
        }
        sentry = Sentry(app, dsn=config.sentry_dns)
        config.config["sentry"] = sentry

    image_service = ImageService(upload_path = config.upload_path)
    app.register_blueprint(ImageController(config, image_service = image_service))
    app.register_blueprint(DangerController(config, image_service = image_service))
    app.register_blueprint(GameController(config))
    app.register_blueprint(PageController(config))
    app.register_blueprint(EventController(config))


    def template(name, **kwargs):
        return render_template(name, config=config, **kwargs)

    @app.route("/")
    def index():
        return template("index.html")

    if config.environment == "development":
        @app.route("/routes")
        def routes():
            out = []
            for rule in app.url_map.iter_rules():
                options = {}
                for arg in rule.arguments:
                    options[arg] = "[{}]".format(arg)
                url = url_for(rule.endpoint, **options)
                out.append("{}\t{}".format(rule.endpoint, url))

            return "<pre>" + "\n".join(out) + "</pre>"

    return app

def run_app(config=None):
    BaseModel.set_base_dir(config.content_directory)

    app = create_app(config)
    app.run(debug=config.debug, host=config.host, port=config.port)

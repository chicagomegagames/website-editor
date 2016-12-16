from flask import Flask, render_template, request, jsonify, redirect, url_for
from raven.contrib.flask import Sentry
from .controllers import ImageController, GameController, PageController, EventController
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

    config_function = site_config(config)

    image_service = ImageService(upload_path = config.upload_path)
    app.register_blueprint(ImageController(config_function, image_service=image_service))
    app.register_blueprint(GameController(config_function))
    app.register_blueprint(PageController(config_function))
    app.register_blueprint(EventController(config_function))


    def template(name, **kwargs):
        return render_template(name, site=config_function(), **kwargs)

    @app.route("/")
    def index():
        return template("index.html")

    @app.route("/danger")
    def danger_zone():
        return template("danger.html", title="Danger Zone")

    @app.route("/danger/error")
    def fake_error():
        raise Exception("Purposefully raised error to confirm everything is working.")

    @app.route("/deploy/<location>")
    def deploy(location):
        #deploy_location = os.path.join(os.getcwd(), "deploy", location)
        if location not in config.deploy_locations:
            abort(500)

        errors = publish_site(location=config.deploy_locations[location]["location"], theme=config.theme)

        if errors is not None:
            return errors

        return redirect(url_for("danger_zone"))

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

def site_config(config):
    def _config():
        return {
            "games": Game.all(),
            "pages": Page.all(),
            "config": config,
        }

    return _config

def run_app(config=None):
    BaseModel.set_base_dir(config.content_directory)

    app = create_app(config)
    app.run(debug=config.debug, host=config.host, port=config.port)

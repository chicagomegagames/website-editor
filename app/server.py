from flask import Flask, render_template, request, jsonify, redirect, url_for
from raven.contrib.flask import Sentry
from .models import BaseModel, Game, Page, Event
from .static import publish_site
import os
import sys

def create_app(config = {}):
    app = Flask("megagame editor")
    if "sentry_dns" in config:
        sentry = Sentry(app, dsn=config["sentry_dns"])

    config_function = site_config(config)
    app.register_blueprint(Game._app_blueprint(site_config=config_function))
    app.register_blueprint(Page._app_blueprint(site_config=config_function))
    app.register_blueprint(Event._app_blueprint(site_config=config_function))


    def template(name, **kwargs):
        return render_template(name, site=config_function(), **kwargs)

    @app.route("/")
    def index():
        return template("index.html")

    @app.route("/danger")
    def danger_zone():
        return template("danger.html", title="Danger Zone")

    @app.route("/deploy/<location>")
    def deploy(location):
        #deploy_location = os.path.join(os.getcwd(), "deploy", location)
        if location not in config["deploy_locations"]:
            abort(500)

        errors = publish_site(location=config["deploy_locations"][location]["location"], theme=config["theme"])

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

def run_app(config={}):
    if "debug" in config:
        debug = config["debug"]
    else:
        debug = False

    if "host" in config:
        host = config["host"]
    else:
        host = "0.0.0.0"

    if "content_directory" in config:
        BaseModel.set_base_dir(config["content_directory"])

    if "deploy_locations" not in config:
        config["deploy_locations"] = {}

    app = create_app(config)
    app.run(debug=debug, host=host)

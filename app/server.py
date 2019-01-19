from flask import Flask, render_template, request, jsonify, redirect, url_for
from raven.contrib.flask import Sentry
from .controllers import BaseController, ImageController, GameController, PageController, EventController, DangerController, PreviewController
from .models import BaseModel, Game, Page, Event
from .static import publish_site
from .config import Config
from .image_service import ImageService
from .preview_service import PreviewService
import os
import raven
import sys

if 'APP_ENV' in os.environ:
    APP_ENV = os.environ['APP_ENV']
else:
    APP_ENV = 'development'

Config._full_reload()

app = Flask("megagame editor")

if Config.use_sentry():
    app.config["SENTRY_CONFIG"] = {
        "release": raven.fetch_git_sha(os.getcwd()),
        "environment": Config.environment,
    }
    sentry = Sentry(app, dsn=Config.sentry_dns)
    Config.config["sentry"] = sentry

image_service = ImageService(Config.image_bucket)
BaseController.set_image_service(image_service)

app.register_blueprint(ImageController())
app.register_blueprint(DangerController())
app.register_blueprint(GameController())
app.register_blueprint(PageController())
app.register_blueprint(EventController())
app.register_blueprint(PreviewController(PreviewService(Config.theme)))


def template(name, **kwargs):
    return render_template(name, config=Config, **kwargs)

@app.route("/")
def index():
    return template("index.html")

if APP_ENV == 'development':
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


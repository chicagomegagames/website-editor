from flask import Flask, render_template, request, jsonify, redirect, url_for
from .models import Game, Page
from .static import publish_site
import logging
import os
import sys

app = Flask("magegame editor")
global global_config

logging.basicConfig(filename="app.log")
logger = logging.getLogger("megagame_editor")
logger.setLevel(logging.DEBUG)

def site():
    global global_config
    site = {
        "games": Game.all(),
        "pages": Page.all(),
        "config": global_config,
    }

    return site

def template(name, **kwargs):
    return render_template(name, site=site(), **kwargs)

def edit_model(model):
    errors = []
    if request.method == "POST":
        # assumption: if you posted data to this route, it is
        # valid json. gorrammit.
        model.update(**request.get_json(force=True))
        if not model.validate():
            errors = model.errors
        else:
            model.save()

        response = {}
        if errors != []:
            response["errors"] = errors
            response["success"] = False
        else:
            response["success"] = True
            response["model"] = model.serialize()

        return jsonify(**response)

    required_meta = {}
    other_meta = {}
    for key, value in model.metadata.items():
        if key in model.REQUIRED_META:
            required_meta[key] = value
        else:
            other_meta[key] = value

    for key in model.REQUIRED_META:
        if key not in required_meta:
            required_meta[key] = None

    return template("edit.html", model=model, required_meta=required_meta, other_meta=other_meta, errors=errors)

@app.route("/")
def index():
    games = Game.all()
    return template("index.html", games=games)

@app.route("/game/<filename>", methods=["GET", "POST"])
def game(filename):
    game = Game(filename)

    if request.method == "DELETE":
        game.delete()
        return redirect(url_for("index"))

    return template("model.html", model=game, prefix="game")

@app.route("/game/<filename>/edit", methods=["GET", "POST"])
def edit_game(filename):
    return edit_model(Game(filename))


@app.route("/page/<filename>")
def page(filename):
    page= Page(filename)

    return template("model.html", model=page, prefix="page")

@app.route("/page/<filename>/edit", methods=["GET", "POST"])
def edit_page(filename):
    return edit_model(Page(filename))

@app.route("/danger")
def danger_zone():
    return template("danger.html", title="Danger Zone")

@app.route("/deploy/<location>")
def deploy(location):
    global global_config
    deploy_location = os.path.join(os.getcwd(), "deploy", location)
    publish_site(location=deploy_location, theme=global_config["theme"])

    return redirect(url_for("danger_zone"))

def run_app(config={}):
    global global_config
    global_config = config
    app.run(debug=True)

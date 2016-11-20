from flask import Flask, render_template, request, jsonify, redirect, url_for
from .models import BaseModel, Game, Page, Event
from .static import publish_site
import logging
import os
import sys

app = Flask("magegame editor")
global global_config

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

    return template("edit.html", model=model, required_meta=model.REQUIRED_META, optional_meta=model.OPTIONAL_META, errors=errors)

def is_delete_request():
    if request.method == "POST" and "_method" in request.form:
        return request.form["_method"] == "DELETE"
    return False

@app.route("/")
def index():
    games = Game.all()
    return template("index.html", games=games)

@app.route("/game/<filename>", methods=["GET", "POST"])
def game(filename):
    game = Game(filename)

    if is_delete_request():
        game.delete()
        return redirect(url_for("index"))

    return template("model.html", model=game, prefix="game")

@app.route("/game/<filename>/edit", methods=["GET", "POST"])
def edit_game(filename):
    return edit_model(Game(filename))

@app.route("/game/new/<filename>", methods=["POST"])
def new_game(filename):
    game = Game.create(filename)
    response = {"success": True, "edit_path": url_for("edit_game", filename=game.filename)}
    return jsonify(**response)

@app.route("/page/<filename>")
def page(filename):
    page = Page(filename)

    return template("model.html", model=page, prefix="page")

@app.route("/page/<filename>/edit", methods=["GET", "POST"])
def edit_page(filename):
    return edit_model(Page(filename))

@app.route("/page/new/<filename>", methods=["POST"])
def new_page(filename):
    page = Page.create(filename)
    response = {"success": True, "edit_path": url_for("edit_page", filename=page.filename)}
    return jsonify(**response)

@app.route("/events/")
def all_events():
    events = Event.all()
    return template("events.html", events=events)

@app.route("/danger")
def danger_zone():
    return template("danger.html", title="Danger Zone")

@app.route("/deploy/<location>")
def deploy(location):
    global global_config
    #deploy_location = os.path.join(os.getcwd(), "deploy", location)
    if location not in global_config["deploy_locations"]:
        abort(500)

    publish_site(location=global_config["deploy_locations"][location]["location"], theme=global_config["theme"])

    return redirect(url_for("danger_zone"))

def run_app(config={}):
    global global_config
    global_config = config
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

    app.run(debug=debug, host=host)

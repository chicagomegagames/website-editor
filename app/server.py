from flask import Flask, render_template, request, jsonify
from .models import Game, InvalidModelError
import sys
import logging

app = Flask("makeme_admin")
logging.basicConfig(filename="app.log")
logger = logging.getLogger("megagame_editor")
logger.setLevel(logging.DEBUG)

def site():
    site = {}
    site["games"] = Game.all()

    return site

def template(name, **kwargs):
    return render_template(name, site=site(), **kwargs)

@app.route("/")
def index():
    games = Game.all()
    return template("index.html", games=games)

@app.route("/game/<filename>")
def game(filename):
    game = Game(filename)
    return template("game.html", game=game)

@app.route("/game/<filename>/edit", methods=["GET", "POST"])
def edit_game(filename):
    game = Game(filename)
    errors = []

    if request.method == "POST":
        # assumption: if you posted data to this route, it is
        # valid json. gorrammit.
        game.update(**request.get_json(force=True))
        if not game.validate():
            errors = game.errors
        else:
            game.save()

        response = {}
        if errors != []:
            response["errors"] = errors
            response["success"] = False
        else:
            response["success"] = True
            response["model"] = game.serialize()

        return jsonify(**response)

    required_meta = {}
    other_meta = {}
    for key, value in game.metadata.items():
        if key in game.REQUIRED_META:
            required_meta[key] = value
        else:
            other_meta[key] = value

    for key in game.REQUIRED_META:
        if key not in required_meta:
            required_meta[key] = None

    return template("edit.html", model=game, required_meta=required_meta, other_meta=other_meta, errors=errors)

def run_app():
    app.run()

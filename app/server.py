from flask import Flask, render_template
from .models import Game

app = Flask("makeme_admin")

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
    # if request.method == "POST":
    #   game.update(**request.form)

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

    return template("edit.html", model=game, required_meta=required_meta, other_meta=other_meta)

def run_app():
    app.run()

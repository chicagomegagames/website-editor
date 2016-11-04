from flask import Flask, render_template
from .models import Game

app = Flask("makeme_admin")

@app.route("/")
def index():
  games = Game.all()
  return render_template("index.html", games=games)

@app.route("/game/<filename>")
def game(filename):
  game = Game(filename)
  return render_template("game.html", game=game)

def run_app():
  app.run()

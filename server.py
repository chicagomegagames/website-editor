from app.server import run_app
import yaml
import os

config = {}
if os.path.exists("config.yaml"):
    with open("config.yaml") as stream:
        config = yaml.load(stream)

run_app(config=config)

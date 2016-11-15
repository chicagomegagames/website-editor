from app.server import run_app
import yaml
import os
import argparse


def main():
    parser = argparse.ArgumentParser(description="The MegaGame Editor application.")
    parser.add_argument("--config", type=str, help="YAML Configuration file", required=True)

    args = parser.parse_args()

    config = {}
    if os.path.exists(args.config):
        with open(args.config) as stream:
            config = yaml.load(stream)

    run_app(config=config)

if __name__ == "__main__":
    main()

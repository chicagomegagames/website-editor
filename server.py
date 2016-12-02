from app import Config
from app.server import run_app
import yaml
import os
import argparse


def main():
    parser = argparse.ArgumentParser(description="The MegaGame Editor application.")
    parser.add_argument("--config", type=str, help="YAML Configuration file", required=True)

    args = parser.parse_args()

    run_app(config=Config.from_file(args.config))

if __name__ == "__main__":
    main()

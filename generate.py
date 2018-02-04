from app import Deploy
from app.models import BaseModel
import argparse
import os.path

def main():
    parser = argparse.ArgumentParser(description="Just generate the site.")
    parser.add_argument("content", type=str, help="Where the content is stored")
    parser.add_argument("location", type=str, help="Where to generate the site")
    parser.add_argument("--theme", type=str, help="Theme to generate", required=True)

    args = parser.parse_args()

    BaseModel.set_base_dir(args.content)
    image_service = ImageService(os.path.join(args.content, "image_uploads"))
    theme_path = os.path.join(args.content, "themes", args.theme)

    deployer = Deploy(
        deploy_dir = args.location,
        theme_path = theme_path,
    )
    deployer.deploy()

if __name__ == "__main__":
    main()

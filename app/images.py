from dotenv import load_dotenv
from imagekitio import ImageKit
import os

load_dotenv()

imagekit = ImageKit(
    private_key = os.environ.get("IMAGEKIT_PRIVATE_KEY")
    # public_key = os.getenv("IMAGEKIT_PUBLIC_KEY"),
    # url_endpoint = os.environ.get("IMAGEKIT_URL_ENDPOINT"),
)
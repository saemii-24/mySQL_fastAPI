from dotenv import load_dotenv
from imagekitio import ImageKit
import os

load_dotenv()

imagekit = ImageKit(
    authentication_parameters={
        "publicKey": os.getenv("IMAGEKIT_PUBLIC_KEY"),
        "privateKey": os.getenv("IMAGEKIT_PRIVATE_KEY"),
        "urlEndpoint": os.getenv("IMAGEKIT_URL"),
    }
)

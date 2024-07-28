from enum import Enum


VERSION = 1
ASSETS_DIR_NAME = "assets"
MODEL_FILE_NAME = "model.json"

class FilepathOutput(Enum):
    LOCAL_PATH = 0,
    MODEL_PATH = 1,
    FULL_PATH = 2,
    IMAGE_DATA = 3

from enum import Enum


VERSION = 1
ASSETS_DIR_NAME = "assets"
MODEL_FILE_NAME = "model.json"
MOUTH_CLOSED_THRESHOLD = 0.02
MOUTH_OPEN_THRESHOLD = 0.06


class FilepathOutput(Enum):
    LOCAL_PATH = 0,
    MODEL_PATH = 1,
    FULL_PATH = 2,
    IMAGE_DATA = 3

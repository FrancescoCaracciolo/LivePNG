from enum import Enum

"""Version of the LivePNG format"""
VERSION = 1
"""Name of the assets directory"""
ASSETS_DIR_NAME = "assets"
"""Name of the model file"""
MODEL_FILE_NAME = "model.json"
"""Amplitude to consider the mouth closed"""
MOUTH_CLOSED_THRESHOLD = 0.02
"""Amplitude to consider the mouth fully open"""
MOUTH_OPEN_THRESHOLD = 0.06


class FilepathOutput(Enum):
    """Enum to specify what type of output the images should have"""

    """Output the local path to the image"""
    LOCAL_PATH = 0,
    """Output the path from the model folder"""
    MODEL_PATH = 1,
    """Output the system path from the root"""
    FULL_PATH = 2,
    """Output the raw image data"""
    IMAGE_DATA = 3

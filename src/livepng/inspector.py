import os
from . import constants
from .exceptions import NoFolderInspectedException, WrongFormatException 
import json

class ModelInspector:
    """Inspect the directories and create the model json"""

    def __init__(self, name: str) -> None:
        """Initialize the inspector

        Args:
            name (str): name of the model
        """
        self.name = name 
        self.json_model = None
        self.directory = None

    def analyze_directory(self, path: str):
        """Analyze the model from the given path

        Args:
            path (str): path of the folder

        Raises:
            WrongFormatException: if the modle is in the wrong format
        """
        assets_dir = os.path.join(path, constants.ASSETS_DIR_NAME)
        if not os.path.isdir(assets_dir):
            raise WrongFormatException("There is no " + constants.ASSETS_DIR_NAME + " directory in the specified path")
        self.json_model = {}
        self.__set_root_info()
        self.__inspect_assets(assets_dir)
        self.directory = path
    
    def __set_root_info(self):
        """Set the name and the version of the model"""
        if self.json_model is None:
            return
        self.json_model["name"] = self.name
        self.json_model["version"] = constants.VERSION
        self.json_model["styles"] = {}

    def __inspect_assets(self, path:str):
        """Analyze styles subdirectories from the given model path"""
        if self.json_model is None:
            return
        styles = [subpath for subpath in os.listdir(path) if os.path.isdir(os.path.join(path, subpath))]
        if len(styles) == 0:
            raise WrongFormatException("There are no styles in the assets dir")
        for style in styles:
            self.__inspect_style(os.path.join(path, style), style)

    def __inspect_style(self, style_path:str, style:str):
        """Analyze expressions in the given style"""
        print(style_path)
        if self.json_model is None:
            return
        self.json_model["styles"][style] = {}
        self.json_model["styles"][style]["expressions"] = {}
        expressions = [subpath for subpath in os.listdir(style_path) if os.path.isdir(os.path.join(style_path, subpath))]
        if len(expressions) == 0:
            raise WrongFormatException("Style " + style + " has no expressions")
        for expression in expressions:
            self.__inspect_expression(os.path.join(style_path, expression), style, expression)

    def __inspect_expression(self, expression_path: str, style: str, expression: str):
        if self.json_model is None:
            return
        self.json_model["styles"][style]["expressions"][expression] = {}
        variants = [subpath for subpath in os.listdir(expression_path) if os.path.isdir(os.path.join(expression_path, subpath))]
        if len(variants) == 0:
            raise WrongFormatException("Expression " + expression + " of style " + style + " has no variants")
        for variant in variants:
            self.__inspect_images(os.path.join(expression_path, variant), style, expression, variant)

    def __inspect_images(self, variant_path, style, expression, variant):
        if self.json_model is None:
            return
        self.json_model["styles"][style]["expressions"][expression][variant] = []
        images = [file for file in os.listdir(variant_path) if os.path.isfile(os.path.join(variant_path, file))]
        for image in images:
            self.json_model["styles"][style]["expressions"][expression][variant].append(image)
    
    def get_model_data(self):
        """Get the model data as a dict"""
        return self.json_model

    def get_model_json(self):
        """Get the model data as a JSON file dump"""
        return json.dumps(self.json_model, indent=2)

    def save_model(self, path:str|None =None):
        """Save model.json in the specified path, if omitted, it is saved in directory/model.json"""
        if self.json_model is None:
            raise NoFolderInspectedException("There is no JSON Model data")
        if path is None:
            if self.directory is None:
                raise NoFolderInspectedException("There is no folder inspected")
            path = os.path.join(self.directory, constants.MODEL_FILE_NAME)
        with open(path, "w+") as f:
            f.write(self.get_model_json())
        

import os
from livepng.exceptions import InvalidModelException
from .constants import ASSETS_DIR_NAME
import json

class ModelValidator:
    """Check if a model is valid"""

    @staticmethod
    def is_file_valid(path: str) -> bool:
        """path: path to the json file"""
        try:
            ModelValidator.validate_file(path)
        except InvalidModelException:
            return False
        return True

    @staticmethod
    def is_model_valid(json_data: dict, path: str):
        try:
            ModelValidator.validate_json(json_data, path)
        except InvalidModelException:
            return False
        return True

    @staticmethod
    def validate_file(path: str):
        """path: path to the json file, throws InvalidModelException if the model is not valid"""
        with open(path, "r") as f:
            js = json.loads(f.read())
        ModelValidator.validate_json(js, os.path.dirname(path))

    @staticmethod
    def validate_json(json: dict, path: str):
        if "name" not in json:
            raise InvalidModelException("The model does not have a name")
        # Version check is omitted
        if "styles" not in json or len(json["styles"]) == 0:
            raise InvalidModelException("No styles in model file")

        if not os.path.isdir(os.path.join(path, ASSETS_DIR_NAME)):
            raise InvalidModelException("No assets folder found")
        
        for style in json["styles"]:
            ModelValidator.check_styles(json["styles"][style], style, os.path.join(path, ASSETS_DIR_NAME, style))

    @staticmethod
    def check_styles(style:dict, style_name: str, path: str):
        if not os.path.isdir(path):
            raise InvalidModelException("There is no dir for style " + style_name)
        if "expressions" not in style or len(style["expressions"]) == 0:
            raise InvalidModelException("There is no expression in the style " + style_name)
        for expression in style["expressions"]:
            ModelValidator.check_expression(style["expressions"][expression], expression, os.path.join(path, expression))
    
    @staticmethod
    def check_expression(expression: dict, expression_name: str, path: str):
        if not os.path.isdir(path):
            raise InvalidModelException("There is no expression for expression " + expression_name)
        for variant in expression:
            if not os.path.isdir(os.path.join(path, variant)):
                raise InvalidModelException("Directory not found for expression " + expression_name)
            ModelValidator.check_variant(expression[variant], variant, os.path.join(path, variant))

    @staticmethod
    def check_variant(variant, variant_name, path):
        if len(variant) == 0:
            raise InvalidModelException("Variant " + variant_name + " has no images")
        for image in variant:
            if not os.path.isfile(os.path.join(path, image)):
                raise InvalidModelException("Image " + os.path.join(path, image) + " not found")




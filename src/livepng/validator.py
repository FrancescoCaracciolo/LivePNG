import os
from livepng.exceptions import InvalidModelException
from .constants import ASSETS_DIR_NAME
import json

class ModelValidator:
    """Check if a model is valid"""

    @staticmethod
    def is_file_valid(path: str) -> bool:
        """Check if a model is valid from a json file

        Args:
            path (str): path of the model.json file

        Returns:
            bool: if the model is valid
        """
        try:
            ModelValidator.validate_file(path)
        except InvalidModelException:
            return False
        return True

    @staticmethod
    def is_model_valid(json_data: dict, path: str):
        """Check if the model is valid from JSON extracted dict and model path

        Args:
            json_data (dict): Extracted model.json data
            path (str): path of the model

        Throws:
            InvalidModelException if the model is not valid
        """
        try:
            ModelValidator.validate_json(json_data, path)
        except InvalidModelException:
            return False
        return True

    @staticmethod
    def validate_file(path: str):
        """Check if the model is valid from the location of the model.json file

        Args:
            path (str): Path to the model.json file
        
        Throws:
            InvalidModelException if the model is not valid
        """
        with open(path, "r") as f:
            js = json.loads(f.read())
        ModelValidator.validate_json(js, os.path.dirname(path))

    @staticmethod
    def validate_json(json: dict, path: str):
        """Check if the model is valid from the decoded content of the model.json file

        Args:
            json (dict): decoded content of the json file
            path (str): Path to the folder of the model
        
        Throws:
            InvalidModelException if the model is not valid
        """    
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
        """Check if the given style is valid

        Args:
            style (dict): Decoded content of the json file for the given style
            style_name (str): Name of the style
            path (str): Path to the folder of the style
        
        Throws:
            InvalidModelException if the model is not valid
        """    
        if not os.path.isdir(path):
            raise InvalidModelException("There is no dir for style " + style_name)
        if "expressions" not in style or len(style["expressions"]) == 0:
            raise InvalidModelException("There is no expression in the style " + style_name)
        for expression in style["expressions"]:
            ModelValidator.check_expression(style["expressions"][expression], expression, os.path.join(path, expression))
    
    @staticmethod
    def check_expression(expression: dict, expression_name: str, path: str):
        """Check if the given expression is valid

        Args:
            expression (dict): Decoded content of the json file for the given expression
            expression_name (str): Name of the expression
            path (str): Path to the folder of the expression
        
        Throws:
            InvalidModelException if the model is not valid
        """    
        if not os.path.isdir(path):
            raise InvalidModelException("There is no expression for expression " + expression_name)
        for variant in expression:
            if not os.path.isdir(os.path.join(path, variant)):
                raise InvalidModelException("Directory not found for expression " + expression_name)
            ModelValidator.check_variant(expression[variant], variant, os.path.join(path, variant))

    @staticmethod
    def check_variant(variant, variant_name, path):
        """Check if the given variant is valid

        Args:
            variant (dict): Decoded content of the json file for the given variant
            variant_name (str): Name of the variant
            path (str): Path to the folder of the variant
        
        Throws:
            InvalidModelException if the model is not valid
        """    
        if len(variant) == 0:
            raise InvalidModelException("Variant " + variant_name + " has no images")
        for image in variant:
            if not os.path.isfile(os.path.join(path, image)):
                raise InvalidModelException("Image " + os.path.join(path, image) + " not found")




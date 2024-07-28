from _typeshed import FileDescriptorOrPath
import json
import os

from livepng import constants
from livepng.constants import FilepathOutput
from livepng.exceptions import NotFoundException, NotLoadedException
from .validator import ModelValidator


class Variant:
    name = ""
    images = []
    def __init__(self, name: str, images: list) -> None:
        self.name = name
        self.images = images

    def get_images(self):
        return self.images
    
    def __str__(self) -> str:
        return self.name
 
class Expression:
    name = ""
    variants = {}
                             
    def __init__(self, name: str, variants: dict) -> None:
        self.name = name
        self.variants = variants

    def get_variants(self) -> dict:
        return self.variants

    def get_default_variant(self) -> Variant:
        return self.variants[list(self.variants.keys())[0]]
    
    def __str__(self) -> str:
        return self.name
 
class Style:
    name = ""
    expressions = {}
    def __init__(self, name: str, expressions: dict) -> None:
       self.name = name
       for expression in expressions:
            self.expressions[expression] = Expression(expression, expressions[expression])

    def get_expressions(self) -> dict:
        return self.expressions

    def get_default_expression(self) -> Expression:
        if "idle" in self.expressions:
            return self.expressions["idle"]
        else:
            return self.expressions[list(self.expressions.keys())[0]]
    
    def __str__(self) -> str:
        return self.name


class LivePNG:
    styles : dict[str, Style] = {}
    current_style : Style
    current_expression : Expression
    current_variant : Variant
    output_type : FilepathOutput
    path : str

    def __init__(self, path: str, output_type=FilepathOutput.LOCAL_PATH) -> None:
        self.output_type = output_type
        self.path = path
        with open(path, "r") as f:
            self.model_info = json.loads(f.read())
        ModelValidator.validate_json(self.model_info, os.path.dirname(path))
        self.load_model()
        self.load_defaults()

    def load_model(self):
        for style in self.model_info["style"]:
            stl = Style(style, self.model_info["style"][style])
            self.styles[style] = stl
                
    def load_defaults(self):
        self.current_style = self.get_default_style()
        self.current_expression = self.current_style.get_default_expression()
        self.current_variant = self.current_expression.get_default_variant()
    
    def get_default_style(self):
        return self.styles[list(self.styles.keys())[0]]

    def get_model_info(self):
        return self.model_info

    def get_current_style(self) -> Style:
        if self.current_style is None:
            raise NotLoadedException("The model has not been loaded correctly")
        return self.current_style

    def set_current_style(self, style: str | Style):
        style = str(style)   
        if style in self.styles:
            self.current_style = self.styles[style]
        else:
            raise NotFoundException("The given style does not exist") 
        
    def get_expressions(self) -> dict[str, Expression]:
        return self.current_style.get_expressions()

    def get_file_path(self, style : str | Style, expression: str | Expression, variant: str | Variant, image: str, output_type: FilepathOutput | None = None) -> str:
        if output_type is None:
            output_type = self.output_type

        model_path = os.path.join(constants.ASSETS_DIR_NAME, str(style), str(expression), str(variant), image)
        match output_type:
            case FilepathOutput.MODEL_PATH:
                return model_path
            case FilepathOutput.LOCAL_PATH:
                return os.path.join(self.path, model_path)
            case FilepathOutput.FULL_PATH:
                return os.path.abspath(os.path.join(self.path, model_path))
            case FilepathOutput.IMAGE_DATA:
                return open(os.path.join(self.path, model_path), "r").read()
            case _:
                raise NotFoundException("The provided output type is not valid")



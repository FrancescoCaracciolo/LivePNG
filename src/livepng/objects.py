from livepng.constants import MOUTH_OPEN_THRESHOLD, MOUTH_CLOSED_THRESHOLD


class Variant:
    name : str
    images : list
    def __init__(self, name: str, images: list) -> None:
        self.name = name
        self.images = []
        for image in images:
            self.images.append(image.replace(" ", " "))
    def get_images(self):
        return self.images
    
    def __str__(self) -> str:
        return self.name

    def get_thresholds(self):
        images = self.get_images()
        # if there is only one image always return it
        if len(images) == 1:
            return [{images[0] : (0, 1)}]
        # If there are multiple images calculate the thresholds
        thresholds = {}
        thresholds[images[0]] = (0, MOUTH_CLOSED_THRESHOLD) 
        thresholds[images[-1]] = (MOUTH_OPEN_THRESHOLD, 1)
        # If there are more than 2 images calculate intermediate values
        if (len(images) > 2):
            mouth_unit = (MOUTH_OPEN_THRESHOLD - MOUTH_CLOSED_THRESHOLD)/(len(images)-2)
            for i in range(1, len(images)-1):
                thresholds[images[i]] = (MOUTH_CLOSED_THRESHOLD + (mouth_unit * (i-1)), 
                                          MOUTH_CLOSED_THRESHOLD + (mouth_unit * i))
        return thresholds


class Expression:
    name : str
    variants : dict[str, Variant]
                             
    def __init__(self, name: str, variants: dict) -> None:
        self.name = name
        self.variants = {}
        for variant in variants:
            self.variants[variant] = Variant(variant, variants[variant])

    def get_variants(self) -> dict:
        return self.variants

    def get_default_variant(self) -> Variant:
        return self.variants[list(self.variants.keys())[0]]
    
    def __str__(self) -> str:
        return self.name
 
class Style:
    name : str
    expressions : dict[str, Expression]
    def __init__(self, name: str, expressions: dict) -> None:
       self.name = name
       self.expressions = {}
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




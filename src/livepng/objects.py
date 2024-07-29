from livepng.constants import MOUTH_OPEN_THRESHOLD, MOUTH_CLOSED_THRESHOLD
import random

from livepng.exceptions import NotFoundException

class Variant:
    """Rapresents a variant of an expression"""
    name : str
    images : list
    def __init__(self, name: str, images: list) -> None:
        self.name = name
        self.images = []
        for image in images:
            self.images.append(image.replace(" ", " "))
    
    def get_images(self) -> list[str]:
        """Returns the list of images for the expression

        Returns:
            list[str]: list of the images
        """
        return self.images
    
    def __str__(self) -> str:
        return self.name

    def get_thresholds(self) -> dict[str, tuple[float]]:
        """Returns the thresholds for every image given an amplitude

        Returns:
            dict[str, tuple[float]]: dict that associates to each image the amplitude range
        """
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
    """Rapresents the expression of a model"""
    name : str
    variants : dict[str, Variant]
                             
    def __init__(self, name: str, variants: dict) -> None:
        self.name = name
        self.variants = {}
        for variant in variants:
            self.variants[variant] = Variant(variant, variants[variant])

    def get_variants(self) -> dict[str, Variant]:
        """Get the list of variants for the given expression

        Returns:
            dict[str, Variant]: variant name -> variant
        """
        return self.variants

    def get_default_variant(self) -> Variant:
        """Get the default variant for the expression

        Returns:
            Variant: default variant
        """
        return self.variants[list(self.variants.keys())[0]]
    
    def __str__(self) -> str:
        return self.name

    def get_random_variant(self, weights: dict[str | Variant, int] | None = None) -> Variant:
        """Get a random variant for the given weights

        Args:
            weights (dict[str  |  Variant, int] | None, optional): The dict that maps variants to their weights.
                Wrights are supposed to be integers, the higher is the weight, the higher is the probability. If None,
                 every expression has the same probability. Defaults to None.

        Raises:
            NotFoundException: if there is an expression not found in the weights

        Returns:
            Variant: the chosen Variant
        """
        if weights is None:
            weights = {}
            for variant in self.get_variants():
                weights[variant] = 1
        weights_sum = sum(weights.values())
        elements = []
        probabilities = []
        for variant in weights:
            if not str(variant) in self.get_variants():
                raise NotFoundException("Variant not found: " + str(variant))
            elements.append(str(variant))
            probabilities.append(weights[str(variant)]/weights_sum)
        
        return self.variants[random.choices(elements, weights=probabilities, k=1)[0]]



class Style:
    """Rapresents the style of a model"""
    name : str
    expressions : dict[str, Expression]

    def __init__(self, name: str, expressions: dict) -> None:
       self.name = name
       self.expressions = {}
       for expression in expressions:
            self.expressions[expression] = Expression(expression, expressions[expression])

    def get_expressions(self) -> dict[str, Expression]:
        """Get the list of expressions for the given style

        Returns:
            dict: expression name -> Expression
        """
        return self.expressions

    def get_default_expression(self) -> Expression:
        """Get the default expression. If idle is available, it is chosen

        Returns:
            Expression: The default expression
        """
        if "idle" in self.expressions:
            return self.expressions["idle"]
        else:
            return self.expressions[list(self.expressions.keys())[0]]
    
    def __str__(self) -> str:
        return self.name




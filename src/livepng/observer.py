from abc import ABC, abstractmethod

from livepng.objects import Expression, Style, Variant


class LivePNGModelObserver(ABC):
    @abstractmethod 
    def on_frame_update(self, image: str):
        pass

    @abstractmethod 
    def on_style_change(self, style: Style):
        pass

    @abstractmethod 
    def on_expression_change(self, expression : Expression):
        pass

    @abstractmethod 
    def on_variant_change(self, variant: Variant):
        pass

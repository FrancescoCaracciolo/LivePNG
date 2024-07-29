from abc import ABC, abstractmethod

from livepng.objects import Expression, Style, Variant


class LivePNGModelObserver(ABC):
    @abstractmethod 
    def on_frame_update(self, image: str):
        """Called when the model must show a new frame

        Args:
            image (str): path of the frame
        """
        pass

    @abstractmethod 
    def on_style_change(self, style: Style):
        """Called when the model has changed its style

        Args:
            style (Style): new style
        """
        pass

    @abstractmethod 
    def on_expression_change(self, expression : Expression):
        """Called when the model has changed its expression

        Args:
            expression (Expression): new expression
        """
        pass

    @abstractmethod 
    def on_variant_change(self, variant: Variant):
        """Called when the model has changed its variatn

        Args:
            variant (Variant): new variant
        """
        pass

    @abstractmethod
    def on_start_speaking(self, audio_file: str):
        """Called when the model starts speaking

        Args:
            audio_file (str): Path to the audio file
        """
        pass

    @abstractmethod
    def on_finish_speaking(self, audio_file: str):
        """Called when the model finishes speaking

        Args:
            audio_file (str): Path to the audio file
        """
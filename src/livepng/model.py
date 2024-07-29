from collections.abc import Callable
import os, json, random, sys, io
from threading import Semaphore
import threading
from pydub import AudioSegment
from time import sleep
import pyaudio

from livepng import constants
from livepng.constants import FilepathOutput 
from livepng.exceptions import NotFoundException, NotLoadedException
from livepng.observer import LivePNGModelObserver
from livepng.objects import Variant, Style, Expression
from .validator import ModelValidator

class LivePNG:
    """Main class rapresenting a LivePNG model"""
    observers : list[LivePNGModelObserver]
    callbackfunctions : list[Callable]

    styles : dict[str, Style] = {}
    current_style : Style
    current_expression : Expression
    current_variant : Variant
    output_type : FilepathOutput
    path : str
    __speak_lock : Semaphore
    __request_interrupt : bool

    def __init__(self, path: str, output_type:FilepathOutput=FilepathOutput.LOCAL_PATH) -> None:
        """Initialize a LivePNG model

        Args:
            path (str): path to the json file of the model
            output_type (FilepathOutput, optional): What type of output to give for the images. Defaults to FilepathOutput.LOCAL_PATH.
        """
        
        self.output_type = output_type
        self.path = path
        # Initialize observers list
        self.observers = []
        self.callbackfunctions = []
        # Initialize locks for playback
        self.__speak_lock = Semaphore(1)
        self.__request_interrupt = False
        # Load the model
        with open(path, "r") as f:
            self.model_info = json.loads(f.read())
        self.path = os.path.dirname(self.path)
        ModelValidator.validate_json(self.model_info, os.path.dirname(path))
        self.load_model()
        self.load_defaults()

    def load_model(self):
        """Load the model"""
        for style in self.model_info["styles"]:
            stl = Style(style, self.model_info["styles"][style]["expressions"])
            self.styles[style] = stl
                
    def load_defaults(self):
        """Set the default style, expression and variant"""
        self.current_style = self.get_default_style()
        self.current_expression = self.current_style.get_default_expression()
        self.current_variant = self.current_expression.get_default_variant()
    
    # Main getters and setters

    def get_default_style(self) -> Style:
        """Get the default style for the model

        Returns:
            Style: default style
        """
        if "default" in self.styles:
            return self.styles["default"]
        else:
            return self.styles[list(self.styles.keys())[0]]

    def get_model_info(self) -> dict:
        """Extracted information from the model.json file

        Returns:
            dict: extracted information
        """
        return self.model_info

    def get_current_style(self) -> Style:
        """Get the current style of the model

        Raises:
            NotLoadedException: if the model is not loaded

        Returns:
            Style: current style
        """
        if self.current_style is None:
            raise NotLoadedException("The model has not been loaded correctly")
        return self.current_style

    def set_current_style(self, style: str | Style):
        """Set the current style for the model

        Args:
            style (str | Style): style to set

        Raises:
            NotFoundException: if the model does not have the specified style
        """
        style = str(style)   
        if style in self.styles:
            self.current_style = self.styles[style]
            self.set_current_expression()
        else:
            raise NotFoundException("The given style does not exist") 
        self.__update_frame()
        self.__update_style()

    def get_expressions(self) -> dict[str, Expression]:
        """Get the expressions for the current style

        Returns:
            dict[str, Expression]: expressions for the current style
        """
        return self.current_style.get_expressions()
    
    def get_current_expression(self) -> Expression:
        """Get the current expression

        Returns:
            Expression: current expression
        """
        return self.current_expression

    def set_current_expression(self, expression : str | Expression | None = None):
        """Set the current expression for the given style

        Args:
            expression (str | Expression | None, optional): expression to set, if omitted the default one is chosen. Defaults to None.

        Raises:
            NotFoundException: if the expression is not found
        """
        if expression is None:
            self.current_expression = self.current_style.get_default_expression()
        else:
            expression = str(expression)
            if expression in self.current_style.get_expressions():
                self.current_expression = self.current_style.get_expressions()[expression]
            else:
                raise NotFoundException("Expression not found")
        self.set_current_variant()
        self.__update_expression()

    def set_current_variant(self, variant : str | Variant | None = None):
        """Set the current variant

        Args:
            variant (str | Variant | None, optional): Variant to set, if omitted the default one is chosen. Defaults to None.

        Raises:
            NotFoundException: if the variant is not found
        """
        if variant is None:
            self.current_variant = self.current_expression.get_default_variant()
        else:
            variant = str(variant)
            if variant in self.current_expression.get_variants():
                self.current_variant = self.current_expression.get_variants()[variant]
            else:
                raise NotFoundException("Variant not found")
        self.__update_frame()
        self.__update_variant()

    def randomize_variant(self, weights : dict[str | Variant, int] | None = None):
        """Set a random variant from the current expression

        Args:
            weights (dict[str  |  Variant, int] | None, optional): The dict that maps variants to their weights.
                Wrights are supposed to be integers, the higher is the weight, the higher is the probability. If None,
                 every expression has the same probability. Defaults to None.. Defaults to None.
        """
        variant = self.current_expression.get_random_variant(weights)
        self.set_current_variant(variant)

    def get_current_variant(self) -> Variant:
        """Get the current variant

        Returns:
            Variant: current variant
        """
        return self.current_variant

    # Get file path
    def get_file_path(self, style : str | Style, expression: str | Expression, variant: str | Variant, image: str, output_type: FilepathOutput | None = None) -> str:
        """Get the path of a file

        Args:
            style (str | Style): style of the mod
            expression (str | Expression): expression of the model
            variant (str | Variant): variant of the model
            image (str): image name
            output_type (FilepathOutput | None, optional): The output type. Defaults to None.

        Raises:
            NotFoundException: if one of the arguments does not exist

        Returns:
            str: the specified path for the output type
        """
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

    def get_image_path(self, img: str, output_type: FilepathOutput | None = None) -> str:
        """Quickly return an image from the current style, expression and variant

        Args:
            img (str): file name of the image
            output_type (FilepathOutput | None, optional): output type. Defaults to None.

        Returns:
            str: file path
        """
        return self.get_file_path(self.current_style, self.current_expression, self.current_variant, img, output_type)

    # Speaking

    def speak(self, wavfile: str, random_variant: bool = True, play_audio: bool = False, frame_rate:int = 10, interrupt_others:bool = True):
        """Play an audio file with lipsync. Not started on another thread.

        Args:
            wavfile (str): path to the .wav file
            random_variant (bool, optional): Randomize variant when start speaking. Defaults to True.
            play_audio (bool, optional): Play the audio. Defaults to False.
            frame_rate (int, optional): FPS to play. Defaults to 10.
            interrupt_others (bool, optional): If interrupt the speak function or wait for it. Defaults to True.
        """
        # Interrupt others and take the lock
        if interrupt_others:
            self.__request_interrupt = True
        self.__speak_lock.acquire()
        self.__request_interrupt = False
        
        if random_variant:
            self.randomize_variant()
        
        audio = AudioSegment.from_file(wavfile)
        # Calculate frames
        sample_rate = audio.frame_rate
        audio_data = audio.get_array_of_samples()
        frames = self.calculate_frames( sample_rate, audio_data, frame_rate=frame_rate)
        # Start lipsync
        frames_thread = threading.Thread(target=self.__update_images, args=(frames, ))
        # Start audio
        stream = None
        p = None
        audio_thread = None
        if play_audio:
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(audio.sample_width),
                        channels=audio.channels,
                        rate=audio.frame_rate,
                        output=True)
            audio_thread = threading.Thread(target=stream.write, args=(audio.raw_data, ))
        # Start threads and notify the observers
        self.__notify_speak_start(wavfile)
        frames_thread.start()
        audio_thread.start() if audio_thread is not None else ""
        frames_thread.join()

        # handle interruption
        if self.__request_interrupt:
            self.__request_interrupt = False
            # Interrupt audio stream
            if play_audio and stream is not None and p is not None and audio_thread is not None:
                stream.stop_stream()
                stream.close()
                p.terminate()
                audio_thread.join()
        # Speaking finished
        # Notify the threads and release the lock
        self.__notify_speak_finish(wavfile)
        self.__speak_lock.release()

    def __update_images(self, frames: list[str], frame_rate:int = 10):
        """Update the frames while speaking

        Args:
            frames (list): list of the frames
            frame_rate (int, optional): frame rate. Defaults to 10.
        """
        for frame in frames:
            if self.__request_interrupt:
                break 
            self.__update_frame(frame)
            sleep(1/frame_rate)
        
    def calculate_frames(self, sample_rate, audio_data, frame_rate=10) -> list[str]:
        """Precalculate every frame for the model

        Args:
            sample_rate (_type_): Sample rate for the audio file
            audio_data (_type_): Audio data
            frame_rate (int, optional): Frame rate. Defaults to 10.

        Returns:
            list[str]: List of the frames
        """
        indexes = []
        for i in range(0, len(audio_data), sample_rate // frame_rate):
            segment = audio_data[i:i + sample_rate // frame_rate]
            absolute_segment = [abs(sample) for sample in segment]
            mean = (sum(absolute_segment)/len(absolute_segment))
            # Normalize the amplitude
            amplitude = mean / 32768
            # Get the frame from the given amplitude
            mouth_image = self.__get_mouth_position(amplitude)
            indexes.append(mouth_image)
        return indexes
    
    def __get_mouth_position(self, amplitude: float) -> str:
        """Get the speaking frame for the given amplitude

        Args:
            amplitude (float): amplitude of the wave

        Returns:
            str: Image path
        """
        images = self.current_variant.get_images()
        thresholds = self.current_variant.get_thresholds()
        for image in images:
            if self.__in_threshold(amplitude, thresholds[image]):
                return self.get_image_path(image)
    
    def __in_threshold(self, value: float, threshold: tuple) -> bool:
        """Check if a given float is in an interval

        Args:
            value (float): the float value
            threshold (tuple): the interval

        Returns:
            bool: if the value is in the interval
        """
        return value >= threshold[0] and value  < threshold[1]
    
    # observers

    def subscribe_observer(self, observer : LivePNGModelObserver):
        """Subscribe a model observer

        Args:
            observer (LivePNGModelObserver): model observer to subscribe
        """
        self.observers.append(observer)

    def unsubscribe_observer(self, observer : LivePNGModelObserver):
        """Unsubscribe a model observer

        Args:
            observer (LivePNGModelObserver): model observer to unsubscribe
        """
        self.observers.remove(observer)

    def subscribe_callback(self, callbackfunction : Callable):
        """Subscribe a callback function to be called at every frame change

        Args:
            callbackfunction (Callable): function to subscribe
        """
        self.callbackfunctions.append(callbackfunction)

    def unsubscribe_callback(self, callbackfunction : Callable):
        """Unsubscribe a callback function

        Args:
            callbackfunction (Callable): function to unsubscribe
        """
        self.callbackfunctions.remove(callbackfunction)

    def __update_frame(self, frame : str | None = None):
        """Called when a new frame is generated

        Args:
            frame (str | None, optional): generated frame. Defaults to None.
        """
        if frame is None:
            frame = self.get_image_path(self.get_current_variant().get_images()[0])
        # Notify observers
        for observer in self.observers:
            observer.on_frame_update(frame)
        # Notify callback functions
        for callbackfunction in self.callbackfunctions:
            callbackfunction(frame)

    def __update_expression(self):
        """Notify the observers that the expression changed"""
        for observer in self.observers:
            observer.on_expression_change(self.current_expression)

    def __update_variant(self):
        """Notify the observers that the variant changed"""
        for observer in self.observers:
            observer.on_variant_change(self.current_variant)
    
    def __update_style(self):
        """Notify the observers that the variant changed"""
        for observer in self.observers:
            observer.on_style_change(self.current_style)
    
    def __notify_speak_start(self, audio : str):
        """Notify the observers that the model started speaking

        Args:
            audio (str): audio file
        """
        for observer in self.observers:
            observer.on_start_speaking(audio)
    
    def __notify_speak_finish(self, audio:str):
        """Notify the observers that the model finished speaking

        Args:
            audio (str): audio file
        """
        for observer in self.observers:
            observer.on_finish_speaking(audio)
    

    def get_images_list(self) -> list[str]:
        """Return a list of all the images in the model

        Returns:
            list[str]: list of all the images
        """
        images = []
        for style in self.styles:
            for expression in self.styles[style].get_expressions():
                for variant in self.styles[style].get_expressions()[expression].get_variants():
                    for image in self.styles[style].get_expressions()[expression].get_variants()[variant].get_images():
                        images.append(self.get_file_path(style, expression, variant, image))
        return images

from collections.abc import Callable
import os, json, sys, io
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

    def __init__(self, path: str, output_type=FilepathOutput.LOCAL_PATH) -> None:
        self.output_type = output_type
        self.path = path
        
        self.observers = []
        self.callbackfunctions = []
        self.__speak_lock = Semaphore(1)
        self.__request_interrupt = False
        with open(path, "r") as f:
            self.model_info = json.loads(f.read())
        self.path = os.path.dirname(self.path)
        ModelValidator.validate_json(self.model_info, os.path.dirname(path))
        self.load_model()
        self.load_defaults()

    def load_model(self):
        for style in self.model_info["styles"]:
            stl = Style(style, self.model_info["styles"][style]["expressions"])
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
    
    def get_current_expression(self) -> Expression:
        return self.current_expression

    def get_current_variant(self) -> Variant:
        return self.current_variant

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

    def get_image_path(self, img: str, output_type: FilepathOutput | None = None):
        return self.get_file_path(self.current_style, self.current_expression, self.current_variant, img, output_type)

    def speak(self, wavfile: str, play_audio: bool = False, frame_rate:int = 10, interrupt_others:bool = True):
        if interrupt_others:
            self.__request_interrupt = True
        self.__speak_lock.acquire()
        self.__request_interrupt = False
        audio = AudioSegment.from_file(wavfile)
        # Calculate frames
        sample_rate = audio.frame_rate
        audio_data = audio.get_array_of_samples()
        frames = self.calculate_frames( sample_rate, audio_data, frame_rate=frame_rate)
        # Start lipsync
        t1 = threading.Thread(target=self.__update_images, args=(frames, ))
        # Start audio
        stream = None
        p = None
        t2 = None
        if play_audio:
            # Prevent pyaudio from printing in console
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(audio.sample_width),
                        channels=audio.channels,
                        rate=audio.frame_rate,
                        output=True)
            t2 = threading.Thread(target=stream.write, args=(audio.raw_data, ))
        # Start threads
        t1.start()
        t2.start() if t2 is not None else ""
        t1.join()

        # handle interruption
        if self.__request_interrupt:
            self.__request_interrupt = False
            # Interrupt audio stream
            if play_audio and stream is not None and p is not None and t2 is not None:
                stream.stop_stream()
                stream.close()
                p.terminate()
                t2.join()
        self.__speak_lock.release()

    def __update_images(self, frames: list, frame_rate:int = 10):
        for frame in frames:
            # Handle interruption
            if self.__request_interrupt:
                break 
            self.__update_frame(frame)
            sleep(1/frame_rate)
        
    def calculate_frames(self, sample_rate, audio_data, frame_rate=10) -> list[str]:
        indexes = []
        for i in range(0, len(audio_data), sample_rate // frame_rate):  # 10x per second
            segment = audio_data[i:i + sample_rate // frame_rate]
            absolute_segment = [abs(sample) for sample in segment]
            mean = (sum(absolute_segment)/len(absolute_segment))
            amplitude = mean / 32768  # Normalizzazione
            mouth_image = self.__get_mouth_position(amplitude)
            indexes.append(mouth_image)
        return indexes
    
    def __get_mouth_position(self, amplitude: float):
        images = self.current_variant.get_images()
        thresholds = self.current_variant.get_thresholds()
        for image in images:
            if self.__in_threshold(amplitude, thresholds[image]):
                return self.get_image_path(image)

    def subscribe_observer(self, observer : LivePNGModelObserver):
        self.observers.append(observer)

    def unsubscribe_observer(self, observer : LivePNGModelObserver):
        self.observers.remove(observer)

    def subscribe_callback(self, callbackfunction : Callable):
        self.callbackfunctions.append(callbackfunction)

    def unsubscribe_callback(self, callbackfunction : Callable):
        self.callbackfunctions.remove(callbackfunction)
    
    def __in_threshold(self, value: float, threshold: tuple):
        return value >= threshold[0] and value  < threshold[1]

    def __update_frame(self, frame : str):
        for observer in self.observers:
            observer.on_frame_update(frame)

        for callbackfunction in self.callbackfunctions:
            callbackfunction(frame)

    def get_images_list(self) -> list[str]:
        images = []
        for style in self.styles:
            for expression in self.styles[style].get_expressions():
                for variant in self.styles[style].get_expressions()[expression].get_variants():
                    for image in self.styles[style].get_expressions()[expression].get_variants()[variant].get_images():
                        images.append(self.get_image_path(image))
        return images

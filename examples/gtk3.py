from livepng.objects import Expression, Style, Variant
from livepng.observer import LivePNGModelObserver
from livepng import LivePNG
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import threading, os, random

# Create the observer
class ModelObserver(LivePNGModelObserver):

    def __init__(self, window):
        self.window = window
    def on_expression_change(self, expression: Expression):
        self.window.label_expression.set_label("Expression: " + str(expression))

    def on_finish_speaking(self, audio_file: str):
        pass
    
    def on_frame_update(self, image: str):
        pass
    
    def on_start_speaking(self, audio_file: str):
        pass
    
    def on_style_change(self, style: Style):
        self.window.label_style.set_label("Style: " + str(style))

    
    def on_variant_change(self, variant: Variant):
        self.window.label_variant.set_label("Variant: " + str(variant))
    
class LipSyncApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="LipSync Application")
        self.set_border_width(10)
        self.set_default_size(1000, 1800)
        
        # Main vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)
        
        # Top horizontal box for labels
        hbox_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.pack_start(hbox_top, False, False, 0)
        
        # Labels
        self.label_style = Gtk.Label(label="Style: ")
        self.label_expression = Gtk.Label(label="Expression: ")
        self.label_variant = Gtk.Label(label="Variant: ")
        
        hbox_top.pack_start(self.label_style, True, True, 0)
        hbox_top.pack_start(self.label_expression, True, True, 0)
        hbox_top.pack_start(self.label_variant, True, True, 0)
        
        # Image showing the LivePNG model
        self.image = Gtk.Image()
        vbox.pack_start(self.image, True, True, 0)
        
        # Bottom horizontal box for buttons
        hbox_bottom = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.pack_start(hbox_bottom, False, False, 0)
        
        # Buttons
        self.button_change_style = Gtk.Button(label="Change Style")
        self.button_change_style.connect("clicked", self.change_style)
        self.button_change_expression = Gtk.Button(label="Change Expression")
        self.button_change_expression.connect("clicked", self.change_expression)
        self.button_change_variant = Gtk.Button(label="Change Variant")
        self.button_change_variant.connect("clicked", self.change_variant)
        self.button_speak = Gtk.Button(label="Speak")
        self.button_speak.connect("clicked", self.speak)
        
        hbox_bottom.pack_start(self.button_change_style, True, True, 0)
        hbox_bottom.pack_start(self.button_change_expression, True, True, 0)
        hbox_bottom.pack_start(self.button_change_variant, True, True, 0)
        hbox_bottom.pack_start(self.button_speak, True, True, 0)
        

        # Load the model and the images
        self.__load_model("models/kurisu/model.json")

    def __load_model(self, path: str):
        # Load LivePNG Model
        self.model = LivePNG(path)
        # Load every image in the model
        self.precache_images()
        # Subscribe the callback to get frame updates
        self.model.subscribe_callback(self.update_image)
        self.observer = ModelObserver(self)
        self.model.subscribe_observer(self.observer)
        # Set initial values for the gui
        self.update_image(self.model.get_current_image())
        self.observer.on_style_change(self.model.get_current_style())
        self.observer.on_expression_change(self.model.get_current_expression())
        self.observer.on_variant_change(self.model.get_current_variant())

    def change_style(self, event):
        style = self.cycle_dict_values(self.model.get_styles(), str(self.model.get_current_style()))
        self.model.set_current_style(style)

    def change_expression(self, event):
        expression = self.cycle_dict_values(self.model.get_expressions(), str(self.model.get_current_expression()))
        self.model.set_current_expression(expression)
    
    def change_variant(self, event):
        variant = self.cycle_dict_values(self.model.get_current_expression().get_variants(), str(self.model.get_current_variant()))
        self.model.set_current_variant(variant)
    
    def speak(self, event):
        audios = os.listdir("audio")
        audio = os.path.join("audio", random.choice(audios))
        t = threading.Thread(target=self.model.speak, args=(audio, True, True))
        t.start()

    def update_image(self, image: str):
        GLib.idle_add(self.image.set_from_pixbuf, self.cachedpixbuf[image]) 
        return True

    def precache_images(self):
        self.cachedpixbuf = {}
        for image in self.model.get_images_list():
            self.cachedpixbuf[image] = GdkPixbuf.Pixbuf.new_from_file_at_scale(filename=image, width=1200,height=1200, preserve_aspect_ratio=True)

    @staticmethod
    def cycle_dict_values(dictionary, current_key):
        keys = list(dictionary.keys())
        return keys[(keys.index(current_key) + 1) % len(keys)]

def main():
    app = LipSyncApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

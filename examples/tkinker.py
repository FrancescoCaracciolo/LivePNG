import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
from livepng import LivePNG
import threading

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer")
        self.image_label = Label(root)
        self.image_label.pack()

    def update_image(self, image_path):
        # Open the image file
        image = Image.open(image_path)
        # Resize the image to fit the label
        image = image.resize((400, 400))
        # Convert the image to PhotoImage
        self.photo = ImageTk.PhotoImage(image)
        # Update the label with the new image
        self.image_label.config(image=self.photo)
        # Keep a reference to avoid garbage collection
        self.image_label.image = self.photo

# Create the main window
root = tk.Tk()
app = ImageApp(root)

# Example usage to update the image
model = LivePNG("models/basic/model.json")
app.update_image(model.get_current_image())
model.subscribe_callback(app.update_image)
t = threading.Thread(target=model.speak, args=("audio/kuri.wav",True, True))
t.start()
# Run the application
root.mainloop()

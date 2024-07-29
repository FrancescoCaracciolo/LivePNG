from livepng import ModelInspector
import os

for f in os.listdir("models"):
    path = os.path.join("models", f)
    if os.path.isdir(path):
        model_name = f
        inspector = ModelInspector(model_name)
        inspector.analyze_directory(path)
        inspector.save_model()
        print("Model {} saved".format(model_name))
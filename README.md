# LivePNG
LivePNG is a format to create avatars based on PNG images.

## Demo
https://github.com/user-attachments/assets/efdddbcf-2850-4325-ab2c-0381f46072f1

## Examples
The easiest way to understand the format is by looking at the `examples` folder.

## Models structure
Every model is described by a JSON file called `model.json` inside its folder.
Its properties are:
- `name`: Name of the model
- `version`: Version of LivePNG (for now only 1 is available)
- `styles`: The list of [styles](#Styles) a model has.


### Styles
A style is supposed to be a different style for a model, for example a clothes change or a different state.
Every style has a name `style_name`, and is contained in the `assets/style_name` folder.
Every style has at least one [expression](#Expressions).

![livepng drawio](https://github.com/user-attachments/assets/fcfc6975-7cf7-44e1-a55b-c34d6765095f)


### Expressions
An expression is supposed to be a different expression for a model, for example a different face expression based on the mood or the emotions of a character.
Every expression has an `expression_name`, and is contained in the `assets/style_name/expression_name`.
Expressions might be different for each style.
If you want a default expression, name it `idle`, otherwise the first expression in alphabetic order is taken.
Every expression has at least one [variant](#Variants)

### Variants
Variants are different variants of an expression. Their objective is to make the character appear more lively, and show different images for each expression. 
Every variant has a `variant_name` and is contained in the `assets/style_name/expression_name/variant_name`.
The variant_name folder must contain the image files that show different states of the lips.

## Python Examples
### Installing
To install and update the package, you can user pip:
```
pip install -U livepng
```
### Quick start

```Python
from livepng import LivePNG

model = LivePNG("path/to/model.json")
# Setting the second style
styles = model.get_styles()
model.set_current_style(styles[list(styles.keys())[1]])
# Setting an happy expression
model.set_current_expression("happy")
# Add a function as a callback
# we are setting a stub function `update_image` as callback
# this function will be called every time there is a frame update
# You can subscribe to more events implementing th Live2DModelObserver interface
model.subscribe_callback(update_iamge)
# Start speaking with lipsync
# It will play audio and set a random variant before starting to speak
# It will call update_image every 0.1s passing the frame to show
model.speak("file.wav", random_variant=True, play_audio=True, frame_rate=10, interrupt_others=True, start_thread=True)
```

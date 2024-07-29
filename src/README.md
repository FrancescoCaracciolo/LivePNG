# LivePNG
LivePNG is a format to create avatars based on PNG images.

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


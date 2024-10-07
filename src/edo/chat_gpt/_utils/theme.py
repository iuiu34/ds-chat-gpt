"""App config."""
from importlib.resources import files

from edo import chat_gpt

font_family = 'Roboto'
package_path = files(chat_gpt)
filename = package_path.joinpath('_utils', 'theme.css')
with open(filename) as f:
    theme_css = f.read()

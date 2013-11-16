import sys

if sys.platform == 'win32':
    from .windows import App, Window
else:
    from .x11 import App, Window

import sys

if sys.platform == 'win32':
    from .windows import Clipboard
else:
    from .x11 import Clipboard
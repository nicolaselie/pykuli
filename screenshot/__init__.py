import sys

if sys.platform == 'win32':
    from .windows import Screenshot
else:
    from .x11 import Screenshot

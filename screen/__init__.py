import sys

if sys.platform == 'win32':
    from .windows import Screen
else:
    from .x11 import Screen
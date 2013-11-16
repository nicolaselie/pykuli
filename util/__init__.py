import sys

TIMEOUT = 3
FOREVER = -1

def set_timeout(timeout):
    TIMEOUT = timeout
    
def do_until_timeout():
    pass

if sys.platform == 'win32':
    from .windows import *
else:
    from .x11 import *

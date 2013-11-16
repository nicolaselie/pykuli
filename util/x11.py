import sys
from Xlib.display import Display

class XObject(object):
    def __init__(self, display=None):        
        if display != None:
            self.display = display
        else:
            self.display = self._getDisplay()
    
    def _getDisplay(self):
        stdout = sys.stdout
        with open('/dev/null', 'w') as sys.stdout:
            display = Display()
        sys.stdout = stdout
        return display 

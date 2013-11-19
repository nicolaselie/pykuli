import sys
import os
import glob

from Xlib.display import Display

import xdg.BaseDirectory
from xdg.DesktopEntry import DesktopEntry

def list_startmenu_applications ():
    for p in xdg.BaseDirectory.xdg_data_dirs:
        for filename in glob.glob(os.path.join(p, "applications", "*.desktop")):
            yield DesktopEntry(filename)

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

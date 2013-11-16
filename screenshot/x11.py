#coding: utf-8
import ctypes
import os
from PIL import Image

import time
from ..util import *

class Screenshot(XObject):
    def __init__(self, display=None):
        XObject.__init__(self, display=display)
        
        LIB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prtscn.so')
        self.prtscn = ctypes.CDLL(LIB_PATH)
        
        self.prtscn.getScreenSize.argtypes = []
        self.prtscn.getScreenSize.restype = ctypes.POINTER(ctypes.c_int)
        self.prtscn.getScreen.argtypes = []

    def grab(self, x=0, y=0, width=None, height=None):
        if not width or not height: 
            result = self.prtscn.getScreenSize()
            if not width:
                width = result[0]
            if not height:
                height = result[1]
                
        buf = ctypes.create_string_buffer(width*height*3)
        self.prtscn.getScreen(x, y, width, height, buf)
        return Image.frombuffer('RGB', (width, height), buf, 'raw', 'RGB', 0, 1)     
            
if __name__ == '__main__':
    import time
    t1 = time.time()
    grabber = Screenshot()
    im = grabber.grab()
    print(time.time() - t1)
    im.show()

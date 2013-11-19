#coding: utf-8
import win32gui
import win32api
import win32ui
import win32con

import numpy
import Image

from ..screen import Screen

class Screenshot:
    def __init__(self):
        self._screen = Screen()
    
    def grab(self, x=None, y=None, width=None, height=None):
        hWnd = win32gui.GetDesktopWindow()
        hDC = win32gui.GetWindowDC(hWnd)
        dcObj  = win32ui.CreateDCFromHandle(hDC)
        cDC = dcObj.CreateCompatibleDC()

        sc = self._screen.get_screen_size()
        if not x:
            x = sc.x1
        if not y:
            y = sc.y1
        if not width:
            width = sc.width
        if not height:
            height = sc.height

        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0,0), (width, height), dcObj, (x, y), win32con.SRCCOPY)
        
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hWnd, hDC)

        bmpinfo = dataBitMap.GetInfo()

        bmpstr = dataBitMap.GetBitmapBits(True)
        win32gui.DeleteObject(dataBitMap.GetHandle())
        
        return Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

if __name__ == '__main__':
    import time
    t1 = time.time()
    grabber = Screenshot()
    im = grabber.grab()
    print(time.time() - t1)
    im.show()

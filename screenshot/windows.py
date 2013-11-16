#coding: utf-8
import win32gui
import win32api
import win32ui
import win32con

import numpy
import Image

class Screenshot:
    def grab(self, x=None, y=None, width=None, height=None):
        hWnd = win32gui.GetDesktopWindow()
        hDC = win32gui.GetWindowDC(hWnd)
        dcObj  = win32ui.CreateDCFromHandle(hDC)
        cDC = dcObj.CreateCompatibleDC()

        if not x:
            x = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        if not y:
            y = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        if not width:
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        if not height:
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

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

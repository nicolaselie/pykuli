#Copyright 2013 Paul Barton
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ctypes import *
import win32api, win32con
from .base import PyMouseMeta, PyMouseEventMeta, ScrollSupportError
import pythoncom
from time import sleep

class POINT(Structure):
    _fields_ = [("x", c_ulong),
                ("y", c_ulong)]

class PyMouse(PyMouseMeta):
    """MOUSEEVENTF_(button and action) constants
    are defined at win32con, buttonAction is that value"""

    def press(self, x=None, y=None, button=1):
        self.move(x, y)
        
        buttonAction = 2 ** ((2 * button) - 1)
        win32api.mouse_event(buttonAction, 0, 0, 0, 0)

    def release(self, x=None, y=None, button=1):
        self.move(x, y)
        
        buttonAction = 2 ** (2 * button)
        win32api.mouse_event(buttonAction, 0, 0, 0, 0)

    def scroll(self, vertical=None, horizontal=None, depth=None):
        #Windows supports only vertical and horizontal scrolling
        if depth is not None:
            raise ScrollSupportError('PyMouse cannot support depth-scrolling \
in Windows. This feature is only available on Mac.')

        #Execute vertical then horizontal scrolling events
        if vertical is not None:
            vertical = int(vertical)
            if vertical == 0:  # Do nothing with 0 distance
                pass
            elif vertical > 0:  # Scroll up if positive
                for _ in range(vertical):
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120, 0)
            else:  # Scroll down if negative
                for _ in range(abs(vertical)):
                    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120, 0)
        if horizontal is not None:
            horizontal = int(horizontal)
            if horizontal == 0:  # Do nothing with 0 distance
                pass
            elif horizontal > 0:  # Scroll right if positive
                for _ in range(horizontal):
                    win32api.mouse_event(MOUSEEVENTF_HWHEEL, 0, 0, 120, 0)
            else:  # Scroll left if negative
                for _ in range(abs(horizontal)):
                    win32api.mouse_event(MOUSEEVENTF_HWHEEL, 0, 0, -120, 0)

    def move(self, x, y):
        if (x, y) != self.position() and (x, y) != (None, None):
            root_x, root_y, width, height = self.virtual_screen_size()
            x = int(x * 65535.0 / (root_x+width-1) )
            y = int(y * 65535.0 / (root_y+height-1))
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, x, y)

    def drag(self, x, y):
        self.move(x, y)

    def position(self):
        pt = POINT()
        windll.user32.GetCursorPos(byref(pt))
        return pt.x, pt.y
        
    def virtual_screen_size(self):
        x = windll.user32.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        y = windll.user32.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        width = windll.user32.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = windll.user32.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        return x, y, width, height

    def screen_size(self):
        width = windll.user32.GetSystemMetrics(win32con.SM_CXSCREEN)
        height = windll.user32.GetSystemMetrics(win32con.SM_CYSCREEN)
        return width, height

class PyMouseEvent(PyMouseEventMeta):
    def __init__(self, capture=False, capture_move=False):
        import pyHook

        PyMouseEventMeta.__init__(self, capture=capture, capture_move=capture_move)
        self.hm = pyHook.HookManager()

    def run(self):
        self.hm.MouseAll = self._action
        self.hm.HookMouse()
        while self.state:
            sleep(0.01)
            pythoncom.PumpWaitingMessages()

    def stop(self):
        self.hm.UnhookMouse()
        self.state = False

    def _action(self, event):
        import pyHook
        x, y = event.Position

        if event.Message == pyHook.HookConstants.WM_MOUSEMOVE:
            self.move(x,y)

        elif event.Message == pyHook.HookConstants.WM_LBUTTONDOWN:
            self.click(x, y, 1, True)
        elif event.Message == pyHook.HookConstants.WM_LBUTTONUP:
            self.click(x, y, 1, False)
        elif event.Message == pyHook.HookConstants.WM_RBUTTONDOWN:
            self.click(x, y, 2, True)
        elif event.Message == pyHook.HookConstants.WM_RBUTTONUP:
            self.click(x, y, 2, False)
        elif event.Message == pyHook.HookConstants.WM_MBUTTONDOWN:
            self.click(x, y, 3, True)
        elif event.Message == pyHook.HookConstants.WM_MBUTTONUP:
            self.click(x, y, 3, False)
            
        elif event.Message == pyHook.HookConstants.WM_MOUSEWHEEL:
            # event.Wheel is -1 when scrolling down, 1 when scrolling up
            self.scroll(x,y,event.Wheel)
        
        return not self.capture

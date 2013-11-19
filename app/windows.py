import win32gui
import win32con
import win32api
import win32process
import subprocess
import time

from ..core import *
from ..util import *
from ..screenshot import Screenshot

APP_LIST = list_startmenu_applications()

class Window(object):
    def __init__(self, win=None, display=None):
        object.__init__(self)
        
        self._screengrabber = Screenshot()
        self._screen = Screen()
        
        self._window = None
        if type(win) == int or type(win) == long:
            self._window = win

    def get_root(self):
        return win32gui.GetDesktopWindow()
        
    def focus(self):
        if self._window != None:
            win32gui.ShowWindow(self._window, win32con.SW_SHOWNOACTIVATE)
            win32gui.SetForegroundWindow(self._window)
        
    def iconify(self):
        if self._window != None:
            win32gui.CloseWindow(self._window)

    def restore(self, vert=True, horz=True):
        if self._window != None:
            win32gui.ShowWindow(self._window, win32con.SW_RESTORE)
            
    def maximize(self, vert=True, horz=True):
        if self._window != None:
            win32gui.ShowWindow(self._window, win32con.SW_SHOWMAXIMIZED)

    def close(self):
        if self._window != None:
            win32api.SendMessage(self._window,
                                 win32con.WM_SYSCOMMAND,
                                 win32con.SC_CLOSE, 0)
            
    def set_size(self, width, height):
        if self._window != None:
            x, y = self.get_pos()
            win32gui.MoveWindow(self._window, x, y, width, height, True)
            
    def get_size(self):
        if self._window != None:
            geom = self.get_geometry()
            return geom[2:4]
            
    def set_pos(self, x, y):
        if self._window != None:
            width, height = self.get_size()
            win32gui.MoveWindow(self._window, x, y, width, height, True)

    def get_pos(self):
        if self._window != None:
            geom = self.get_geometry()
            return geom[0:2]
            
    def get_geometry(self):
        if self._window != None:
            x1, y1, x2, y2 = win32gui.GetWindowRect(self._window)
            x1, y1 = win32gui.ClientToScreen(self.get_root(), (x1, y1))
            x2, y2 = win32gui.ClientToScreen(self.get_root(), (x2, y2))
            width = x2 - x1
            height = y2 - y1
            return x1, y1, width, height
            
    def grab(self):
        if self._window != None:
            self.focus()
            time.sleep(0.1)
            x, y = self.get_pos()
            width, height = self.get_size()
            sc = self._screen.get_screen_size()
            if x + width > sc.x1 + sc.width:
                width = sc.x1 + sc.width - x
            if y + height > sc.y1 + sc.height:
                height = sc.y1 + sc.height - y
            if x < sc.x1:
                width -= abs(abs(sc.x1) - abs(x))
                x = sc.x1
            if y < sc.y1:
                height -= abs(abs(sc.y1) - abs(y))
                y = sc.y1
            return self._screengrabber.grab(x=x,
                                            y=y,
                                            width=width,
                                            height=height)
        
    def get_title(self):
        if self._window != None:
            return win32gui.GetWindowText(self._window)
        
    def get_pid(self):
        if self._window != None:
            return win32process.GetWindowThreadProcessId(self._window)[1]

class App(Window):
    def __init__(self, name=None, win=None, display=None):
        Window.__init__(self, win=win, display=display)
        
        if type(name) == str or type(name) == unicode:
            self.set_window(name)
            
            #Get command to launch the program and clean up the paramaters
            commands = self._get_commands_from_name(name)
            if len(commands) > 0:
                self._command = commands[0] #Use the first result as default
                #Try to find a better match
                for cmd in commands:
                    if cmd.split()[0].lower() == name.lower():
                        self._command = cmd
                        break
            else:
                self._command = None
        else:
            self._command = None
            
    def _get_commands_from_name(self, name):
        commands = []
        for appname, appcmd in APP_LIST:
            if name in appname:
                commands.append(appcmd)
        return commands
            
    def list_windows(self):
        win_list = []
        
        def handler(hWnd, win_list):
            if win32gui.IsWindowVisible(hWnd):
                win_list.append(Window(win=hWnd))
                
        win32gui.EnumWindows(handler, win_list)
        return win_list
    
    def set_window(self, name):
        self._name = name
        for window in self.list_windows():
            if name in window.get_title():
                self._window = window._window
                return True
        return False
                    
    def get_window(self):
        if self._window != None:
            return Window(win=self._window)
            
    def open(self, timeout=TIMEOUT):
        if self._command != None:
            p = subprocess.Popen(self._command)
            time.sleep(2)
            self.wait(timeout=timeout, pid=p.pid)
                
    def wait(self, timeout=TIMEOUT, name=None, pid=None):
        t0 = time.time()
        if type(pid) == int:
            while time.time()-t0<timeout:
                for window in self.list_windows():
                    if window.get_pid() == pid:
                        self._window = window._window
                        return True
        elif type(name) == str or type(name) == unicode:
            while time.time()-t0<timeout:
                if self.set_window() == True:
                    return True
        return False
        
    def get_focused_window(self):
        return win32gui.GetForegroundWindow()


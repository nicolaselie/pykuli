import sys
import os
import re
import subprocess
import time

from Xlib import X, Xatom, Xutil, protocol, error

import xdg.Menu
import xdg.DesktopEntry

from ..screen import *
from ..util import *
from ..screenshot import Screenshot

APP_LIST = list_startmenu_applications()

class Window(XObject):
    def __init__(self, win=None, display=None):
        XObject.__init__(self, display=display)
        
        self._screengrabber = Screenshot()
        self._screen = Screen()

        self.NET_ACTIVE_WINDOW_ATOM = self.display.intern_atom('_NET_ACTIVE_WINDOW', False)
        self.NET_CLIENT_LIST_ATOM = self.display.intern_atom('_NET_CLIENT_LIST', False)
        self.NET_WM_NAME_ATOM = self.display.intern_atom('_NET_WM_NAME', False)
        self.NET_WM_PID_ATOM = self.display.intern_atom('_NET_WM_PID', False)
        self.NET_WM_STATE_ATOM = self.display.intern_atom('_NET_WM_STATE', False)
        self.NET_WM_STATE_MAXIMIZED_VERT_ATOM = self.display.intern_atom('_NET_WM_STATE_MAXIMIZED_VERT', False)
        self.NET_WM_STATE_MAXIMIZED_HORZ_ATOM = self.display.intern_atom('_NET_WM_STATE_MAXIMIZED_HORZ', False)
        self.NET_FRAME_EXTENTS_ATOM = self.display.intern_atom('_NET_FRAME_EXTENTS', False)

        self.WM_CHANGE_STATE_ATOM = self.display.intern_atom('WM_CHANGE_STATE', False)

        self.UTF8_STRING_ATOM = self.display.intern_atom('UTF8_STRING', True)
        
        self._window = None
        if win.__class__ == "Xlib.display.Window":
            self._window = win
        elif type(win) == int or type(win) == long:
            try:
                self._window = self.display.create_resource_object('window', win)
            except error.BadWindow :
                self._window = None

    def get_root(self):
        return self.display.screen().root

    def _send_client_message(self, data, event_type, mask):
        #http://code.google.com/p/pywo/source/browse/trunk/pywo/core/xlib.py
        event = protocol.event.ClientMessage(
                    window=self._window,
                    sequence_number=0,
                    client_type=event_type,
                    data=(32, (data)))
        self.get_root().send_event(event, event_mask=mask)
        self.display.sync()
        
    def focus(self):
        if self._window != None:                
            self._send_client_message([0, 0, 0, 0, 0],
                            self.NET_ACTIVE_WINDOW_ATOM,
                            X.SubstructureRedirectMask)
            #self._window.configure(stack_mode = X.Above)
        
    def iconify(self):
        if self._window != None:
            self._send_client_message([Xutil.IconicState, 0, 0, 0, 0],
                            self.WM_CHANGE_STATE_ATOM,
                            X.SubstructureRedirectMask)
            #self._window.configure(stack_mode = X.Below)

    def restore(self, vert=True, horz=True):
        self.maximize(mode=Xutil.DontCareState, vert=vert, horz=horz)
            
    def maximize(self, mode=None, vert=True, horz=True):
        """Maximize window.

        If you want to maximize only horizontally use ``vert=False``
        If you want to maximize only vertically use ``horz=False``

        """
        if self._window != None:
            if mode == None:
                mode = self._window.get_wm_state().state
            
            if horz == True:
                horz = self.NET_WM_STATE_MAXIMIZED_HORZ_ATOM
            else:
                horz = 0
                
            if vert == True:   
                vert = self.NET_WM_STATE_MAXIMIZED_VERT_ATOM
            else:
                vert = 0
                
            self._send_client_message([mode, horz, vert, 0, 0],
                                self.NET_WM_STATE_ATOM,
                                X.SubstructureRedirectMask)

    def close(self):
        if self._window != None:
            self._window.destroy()
            self.display.sync()
            
    def set_size(self, width, height):
        if self._window != None:
            self._window.configure(width=width, height=height)
            self.display.sync()
            
    def get_size(self):
        if self._window != None:
            geom = self.get_geometry()
            return geom["width"], geom["height"]
            
    def set_pos(self, x, y):
        if self._window != None:
            self._window.configure(x=x, y=y)
            self.display.sync()

    def get_pos(self):
        if self._window != None:
            geom = self.get_geometry()
            return geom["x"], geom["y"]
            
    def get_geometry(self):
        if self._window != None:
            win = self._window
            root = self.get_root()
            while(win.query_tree().parent.id != root.id):
                win = win.query_tree().parent
                
            return win.get_geometry()._data
        
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
            wmname = self._window.get_wm_name()
            if wmname == "":
                prop =  self._window.get_full_property(self.NET_WM_NAME_ATOM,
                                              self.UTF8_STRING_ATOM)
                if prop == None:
                    prop =  self._window.get_full_property(self.NET_WM_NAME_ATOM,
                                                  Xatom.STRING)
                if prop != None:
                    wmname = prop.value
            return wmname
        
    def get_transient_for(self):
        if self._window != None:
            return self._window.get_wm_transient_for()
        
    def get_full_property(self, atom, datatype=int):
        if datatype == int:
            data = self._window.get_full_property(atom,
                                                Xatom.CARDINAL)
            if data != None:
                    return int(data.value[0])
        
    def get_pid(self):
        if self._window != None:
            return self.get_full_property(self.NET_WM_PID_ATOM)

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
        
    def _get_commands_from_name(self, name, menu=None, commands=[]):
        commands = []
        for entry in APP_LIST:
            if name in entry.getName() or name in entry.getGenericName():
                command = entry.getExec()
                if command == '':
                    continue
                
                #Fill up special fields
                #http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html
                command = command.replace("%i",
                                    entry.getIcon())
                command = command.replace("%c",
                                    entry.getName())
                command = command.replace("%k",
                                    entry.getPath())
                
                #Clean up
                params = command.split()
                for param in params:
                    if param in ['%f', '%u', '%F', '%U', '%d', '%D',
                            '%n', '%N', '%v', '%m']:
                        params.pop()
                    if params[-1].startswith("-"):
                        params.pop()
                command = " ".join(params)
                commands.append(command)
                
        return commands
        
    def list_windows(self):
        root = self.get_root()
        winid_list = root.get_full_property(self.NET_CLIENT_LIST_ATOM,
                                            X.AnyPropertyType).value

        win_list = []
        for winid in winid_list:
            win = Window(win=winid)
            transient_for = win.get_transient_for()
            wmname = win.get_title()
            wmpid = win.get_pid()
                
            if transient_for == None and wmname != None:
                win_list.append(win)     
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
            return Window(win=self._window, display=self.display)
            
    def open(self, timeout=TIMEOUT):
        if self._command != None:
            p = subprocess.Popen(self._command, shell=True)
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
            print "timeout", pid
        elif type(name) == str or type(name) == unicode:
            while time.time()-t0<timeout:
                if self.set_window() == True:
                    return True
        return False
        
    def get_focused_window(self):
        root = self.display.screen().root
        winid = root.get_full_property(self.NET_ACTIVE_WINDOW_ATOM,
                                       X.AnyPropertyType).value[0]       
        return Window(win=wind, display=self.display)

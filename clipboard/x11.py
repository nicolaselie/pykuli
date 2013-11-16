#coding: utf-8
from Xlib.display import Display
from Xlib.error import ConnectionClosedError
from Xlib import X, protocol, Xatom

import struct
import daemon
from multiprocessing import Process, Event
import sys
import time

from ..util import *

PRIMARY = "PRIMARY"
CLIPBOARD = "CLIPBOARD"

class Clipboard(XObject):
    def __init__(self, display=None):
        XObject.__init__(self, display=display)
        self.event = None
        
        self.display = self._getdisplay()
                       
        self.targets_atom = self.display.intern_atom("TARGETS", False)
        self.delete_atom = self.display.intern_atom("DELETE", False)
        self.text_atom = self.display.intern_atom( "TEXT", False)
        self.utf8_atom = self.display.intern_atom("UTF8_STRING", True)
    
        self.supported_targets = [self.targets_atom, 
                                  self.delete_atom, 
                                  self.text_atom, 
                                  Xatom.STRING]
        
        if self.utf8_atom != None:
            self.supported_targets.append(self.utf8_atom)
        else:
            self.utf8_atom = Xatom.STRING
            
        self.WM_DELETE_WINDOW = self.display.intern_atom('WM_DELETE_WINDOW')
        self.WM_PROTOCOLS = self.display.intern_atom('WM_PROTOCOLS')
            
    def _getdisplay(self):
        stdout = sys.stdout
        with open('/dev/null', 'w') as sys.stdout:
            display = Display()
        sys.stdout = stdout
        
        return display

    def get(self, name=CLIPBOARD):        
        #Get selection atom from atom name
        selection_atom = self.display.intern_atom(name, True)
        if not selection_atom:
            return ''

        #Get owner of the selection
        owner = self.display.get_selection_owner(selection_atom)
        if not owner:
            owner = self.display.screen().root
        
        self.display.sync()

        value = self._getselection(owner, selection_atom, self.utf8_atom)
        if value:
            return value.decode('utf8')
        
        value = self._getselection(owner, selection_atom, Xatom.STRING)
        if value:
            return value
            
        return ''
        
    def _getselection(self, window, selection_atom, atom):
        #Convert the selection
        prop = self.display.intern_atom("XSEL_DATA", False)
        window.convert_selection(selection_atom, atom, prop, X.CurrentTime)
        
        #Get selection length
        data = window.get_property(prop, atom, 0, 0)
        if not data:
            return None
        
        #Get selection
        data = window.get_property(prop, atom, 0, data.bytes_after)

        return data.value

    
    def _set(self, text, name=CLIPBOARD):
        self.display = self._getdisplay()
        
        screen = self.display.screen()
        window = screen.root.create_window(
                0, 0, 1, 1, 1,
                screen.root_depth,
                background_pixel = screen.white_pixel,
                event_mask = X.NoEventMask)
                  
        if isinstance(text, unicode):
            text = text.encode('utf8')
             
        #Get selection atom from atom name
        selection_atom = self.display.intern_atom(name, True)
        if not selection_atom:
            return False
      
        window.set_selection_owner(selection_atom, X.CurrentTime)
        
        self.display.sync()
        if self.event != None:
            self.event.set()
            
        while True:
            try:
                event = self.display.next_event()
            except ConnectionClosedError:
                break
            if event.type == X.SelectionClear:
                #Can come from any display
                break
            elif event.type == X.DestroyNotify:
                break
            elif event.type == X.ClientMessage:
                if event.client_type == self.WM_PROTOCOLS:
                    fmt, data = event.data
                    if fmt == 32 and data[0] == self.WM_DELETE_WINDOW:
                        break
            elif event.type == X.SelectionRequest:                    
                #Comes from the requestor display           
                new_event = protocol.event.SelectionNotify(
                    time = 0,
                    requestor = event.requestor,
                    selection = event.selection,
                    target = event.target,
                    property = event.property,
                    sequence_number = event.sequence_number)
                
                if event.target == self.targets_atom:
                    new_event.property = event.property
                    data = struct.pack('l' * len(self.supported_targets),
                                       *self.supported_targets)
                    event.requestor.change_property(event.property,
                                                    Xatom.ATOM,
                                                    32,
                                                    data)
                elif event.target == Xatom.STRING:
                    new_event.property = event.property
                    event.requestor.change_property(event.property,
                                                    Xatom.STRING,
                                                    8,
                                                    text)
                elif event.target == self.text_atom:
                    new_event.property = event.property
                    event.requestor.change_property(event.property,
                                                    self.text_atom,
                                                    8,
                                                    text)
                elif event.target == self.utf8_atom:
                    new_event.property = event.property
                    event.requestor.change_property(event.property,
                                                    self.utf8_atom,
                                                    8,
                                                    text)
                elif event.target == self.delete_atom:
                    new_event.property = event.property
                    event.requestor.change_property(event.property,
                                                    self.delete_atom,
                                                    0,
                                                    None) 
                else: #Refuse connection
                    new_event.property = None

                event.requestor.send_event(new_event)
                self.display.sync()
        return True
    
    def _set_daemon(self, text, name=CLIPBOARD):
        with daemon.DaemonContext(detach_process=True,
                                  stdout=sys.stdout,
                                  stderr=sys.stderr):
            self._set(text, name)
                
    def set(self, text, name=CLIPBOARD):
        self.event = Event()
        worker = Process(target=self._set_daemon, args=[text, name])
        worker.start()
        self.event.wait()
        time.sleep(0.1)
        
        return True
        
    def clear(self, name=CLIPBOARD):
        #Get selection atom from atom name
        selection_atom = self.display.intern_atom(name, True)
        if not selection_atom:
            return False

        #Get owner of the selection
        owner = self.display.get_selection_owner(selection_atom)
        if not owner:
            owner = self.display.screen().root
        
        protocol.request.SetSelectionOwner(display = owner.display,
                                  window = 0,
                                  selection = selection_atom,
                                  time = X.CurrentTime)
        self.display.sync()
        
        return True

if __name__ == '__main__':
    text = u'azertyuiop^$*µù¤'
    clip = Clipboard()
    print clip.get()
    clip.set(text)
    assert(clip.get().decode('utf8') == text)
    clip.clear()
    print clip.get()

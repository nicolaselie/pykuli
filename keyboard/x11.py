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

from Xlib.display import Display
from Xlib import X, XK, protocol
from Xlib.XK import string_to_keysym, load_keysym_group
from Xlib.ext import record

from .base import KeyboardMeta, KeyboardEventMeta

import time

SPECIAL_X_KEYSYMS = {
    ' ': "space",
    '\t': "Tab",
    '\n': "Return",  # for some reason this needs to be cr, not lf
    '\r': "Return",
    '\e': "Escape",
    '!': "exclam",
    '#': "numbersign",
    '%': "percent",
    '$': "dollar",
    '&': "ampersand",
    '"': "quotedbl",
    '\'': "apostrophe",
    '(': "parenleft",
    ')': "parenright",
    '*': "asterisk",
    '=': "equal",
    '+': "plus",
    ',': "comma",
    '-': "minus",
    '.': "period",
    '/': "slash",
    ':': "colon",
    ';': "semicolon",
    '<': "less",
    '>': "greater",
    '?': "question",
    '@': "at",
    '[': "bracketleft",
    ']': "bracketright",
    '\\': "backslash",
    '^': "asciicircum",
    '_': "underscore",
    '`': "grave",
    '{': "braceleft",
    '|': "bar",
    '}': "braceright",
    '~': "asciitilde"
    }

MODIFIERS = ['Control_L',
             'Alt_L',
             'ISO_Level3_Shift',
             'Shift_L',
             'Super_L',
             'Hyper_L',
             'Meta_L',
             'Caps_Lock',
             'Num_Lock']

MASK_INDEXES = [
               (X.ShiftMapIndex, X.ShiftMask),
               (X.ControlMapIndex, X.ControlMask),
               (X.LockMapIndex, X.LockMask),
               (X.Mod1MapIndex, X.Mod1Mask),
               (X.Mod2MapIndex, X.Mod2Mask),
               (X.Mod3MapIndex, X.Mod3Mask),
               (X.Mod4MapIndex, X.Mod4Mask),
               (X.Mod5MapIndex, X.Mod5Mask),
               ]

class Keyboard(KeyboardMeta):
    """
    The PyKeyboard implementation for X11 systems (mostly linux). This
    allows one to simulate keyboard input.
    """
    def __init__(self, display=None):
        PyKeyboardMeta.__init__(self)
        self.display = Display(display)
        self.root = self.display.screen().root
        
        XK.load_keysym_group('xkb')
        
        altList = self.display.keysym_to_keycodes(XK.XK_ISO_Level3_Shift)
        self.__usable_modifiers = (0, 1)
        for code, offset in altList:
            if code == 108 and offset == 0:
                self.__usable_modifiers += (4, 5)
                break
            
        mapping = self.display.get_modifier_mapping()
        self.modmasks = {}
        for keyname in MODIFIERS:
            keysym = XK.string_to_keysym(keyname)
            keycodes = self.display.keysym_to_keycodes(keysym)
            
            found = False
            for keycode, lvl in keycodes:
                for index, mask in MASK_INDEXES:
                    if keycode in mapping[index]:
                        self.modmasks[keycode] = mask
                        found = True
                    
                if found:
                    break
 
        self.flags = {        
            'Shift': X.ShiftMask,
            'Lock': X.LockMask,
            'Ctrl': X.ControlMask,
            'Alt': 0,
            'AltGr': self.modmasks[altList[0][0]],
            'Hankaku': 0}
        
        self.special_key_assignment()

    def __findUsableKeycode(self, keycodes):
        for code, mask in keycodes:
            if mask in self.__usable_modifiers:
                return code, mask

        return None, None

    def press_key(self, character='', modifier=0):
        """
        Press a given character key. Also works with character keycodes as
        integers, but not keysyms.
        """
        window = self.display.get_input_focus().focus
        
        char_val, char_mask = self.lookup_character_value(character)
        if char_val == None or char_mask == None:
            return False
        char_mask ^= modifier
        
        print character, char_mask, modifier
        
        event = protocol.event.KeyPress(
            detail = char_val,
            time = X.CurrentTime,
            root = self.root,
            window = window,
            child = X.NONE,
            root_x = 0,
            root_y = 0,
            event_x = 0,
            event_y = 0,
            state = char_mask,
            same_screen = 0)
        window.send_event(event)
        self.display.sync()

    def release_key(self, character='', modifier=0):
        """
        Release a given character key. Also works with character keycodes as
        integers, but not keysyms.
        """
        window = self.display.get_input_focus().focus
        
        char_val, char_mask = self.lookup_character_value(character)
        if char_val == None or char_mask == None:
            return False
        char_mask ^= modifier
        
        event = protocol.event.KeyRelease(
            detail = char_val,
            time = X.CurrentTime,
            root = self.root,
            window = window,
            child = X.NONE,
            root_x = 0,
            root_y = 0,
            event_x = 0,
            event_y = 0,
            state = char_mask,
            same_screen = 0)
        window.send_event(event)
        self.display.sync()

    def special_key_assignment(self):
        """
        Determines the keycodes for common special keys on the keyboard. These
        are integer values and can be passed to the other key methods.
        Generally speaking, these are non-printable codes.
        """
        #This set of keys compiled using the X11 keysymdef.h file as reference
        #They comprise a relatively universal set of keys, though there may be
        #exceptions which may come up for other OSes and vendors. Countless
        #special cases exist which are not handled here, but may be extended.
        #TTY Function Keys
        self.backspace_key = self.lookup_character_value('BackSpace')[0]
        self.tab_key = self.lookup_character_value('Tab')[0]
        self.linefeed_key = self.lookup_character_value('Linefeed')[0]
        self.clear_key = self.lookup_character_value('Clear')[0]
        self.return_key = self.lookup_character_value('Return')[0]
        self.enter_key = self.return_key  # Because many keyboards call it "Enter"
        self.pause_key = self.lookup_character_value('Pause')[0]
        self.scroll_lock_key = self.lookup_character_value('Scroll_Lock')[0]
        self.sys_req_key = self.lookup_character_value('Sys_Req')[0]
        self.escape_key = self.lookup_character_value('Escape')[0]
        self.delete_key = self.lookup_character_value('Delete')[0]
        #Modifier Keys
        self.shift_l_key = self.lookup_character_value('Shift_L')[0]
        self.shift_r_key = self.lookup_character_value('Shift_R')[0]
        self.shift_key = self.shift_l_key  # Default Shift is left Shift
        self.alt_l_key = self.lookup_character_value('Alt_L')[0]
        self.alt_r_key = self.lookup_character_value('Alt_R')[0]
        self.alt_key = self.alt_l_key  # Default Alt is left Alt
        self.alt_gr_key = self.lookup_character_value('ISO_Level3_Shift')[0]
        self.control_l_key = self.lookup_character_value('Control_L')[0]
        self.control_r_key = self.lookup_character_value('Control_R')[0]
        self.control_key = self.control_l_key  # Default Ctrl is left Ctrl
        self.caps_lock_key = self.lookup_character_value('Caps_Lock')[0]
        self.capital_key = self.caps_lock_key  # Some may know it as Capital
        self.shift_lock_key = self.lookup_character_value('Shift_Lock')[0]
        self.meta_l_key = self.lookup_character_value('Meta_L')[0]
        self.meta_r_key = self.lookup_character_value('Meta_R')[0]
        self.super_l_key = self.lookup_character_value('Super_L')[0]
        self.windows_l_key = self.super_l_key  # Cross-support; also it's printed there
        self.super_r_key = self.lookup_character_value('Super_R')[0]
        self.windows_r_key = self.super_r_key  # Cross-support; also it's printed there
        self.hyper_l_key = self.lookup_character_value('Hyper_L')[0]
        self.hyper_r_key = self.lookup_character_value('Hyper_R')[0]
        #Cursor Control and Motion
        self.home_key = self.lookup_character_value('Home')[0]
        self.up_key = self.lookup_character_value('Up')[0]
        self.down_key = self.lookup_character_value('Down')[0]
        self.left_key = self.lookup_character_value('Left')[0]
        self.right_key = self.lookup_character_value('Right')[0]
        self.end_key = self.lookup_character_value('End')[0]
        self.begin_key = self.lookup_character_value('Begin')[0]
        self.page_up_key = self.lookup_character_value('Page_Up')[0]
        self.page_down_key = self.lookup_character_value('Page_Down')[0]
        self.prior_key = self.lookup_character_value('Prior')[0]
        self.next_key = self.lookup_character_value('Next')[0]
        #Misc Functions
        self.select_key = self.lookup_character_value('Select')[0]
        self.print_key = self.lookup_character_value('Print')[0]
        self.print_screen_key = self.print_key  # Seems to be the same thing
        self.snapshot_key = self.print_key  # Another name for printscreen
        self.execute_key = self.lookup_character_value('Execute')[0]
        self.insert_key = self.lookup_character_value('Insert')[0]
        self.undo_key = self.lookup_character_value('Undo')[0]
        self.redo_key = self.lookup_character_value('Redo')[0]
        self.menu_key = self.lookup_character_value('Menu')[0]
        self.apps_key = self.menu_key  # Windows...
        self.find_key = self.lookup_character_value('Find')[0]
        self.cancel_key = self.lookup_character_value('Cancel')[0]
        self.help_key = self.lookup_character_value('Help')[0]
        self.break_key = self.lookup_character_value('Break')[0]
        self.mode_switch_key = self.lookup_character_value('Mode_switch')[0]
        self.script_switch_key = self.lookup_character_value('script_switch')[0]
        self.num_lock_key = self.lookup_character_value('Num_Lock')[0]
        #Keypad Keys: Dictionary structure
        keypad = ['Space', 'Tab', 'Enter', 'F1', 'F2', 'F3', 'F4', 'Home',
                  'Left', 'Up', 'Right', 'Down', 'Prior', 'Page_Up', 'Next',
                  'Page_Down', 'End', 'Begin', 'Insert', 'Delete', 'Equal',
                  'Multiply', 'Add', 'Separator', 'Subtract', 'Decimal',
                  'Divide', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.keypad_keys = {k: self.lookup_character_value('KP_'+str(k)[0]) for k in keypad}
        self.numpad_keys = self.keypad_keys
        #Function Keys/ Auxilliary Keys
        #FKeys
        self.function_keys = [None] + [self.lookup_character_value('F'+str(i)[0]) for i in xrange(1,36)]
        #LKeys
        self.l_keys = [None] + [self.lookup_character_value('L'+str(i)[0]) for i in xrange(1,11)]
        #RKeys
        self.r_keys = [None] + [self.lookup_character_value('R'+str(i)[0]) for i in xrange(1,16)]

        #Unsupported keys from windows
        self.kana_key = None
        self.hangeul_key = None # old name - should be here for compatibility
        self.hangul_key = None
        self.junjua_key = None
        self.final_key = None
        self.hanja_key = None
        self.kanji_key = None
        self.convert_key = None
        self.nonconvert_key = None
        self.accept_key = None
        self.modechange_key = None
        self.sleep_key = None

    def lookup_character_value(self, character):
        """
        Looks up the keysym for the character then returns the keycode mapping
        and modifier for that keysym.
        """
        ch_keysym = XK.string_to_keysym(character)
        ch_mask = 0
        if ch_keysym == 0:
            if character in SPECIAL_X_KEYSYMS:
                ch_keysym = XK.string_to_keysym(SPECIAL_X_KEYSYMS[character])
            elif len(character) == 1:
                ch_keysym = ord(character)
        ch_keycodes = self.display.keysym_to_keycodes(ch_keysym)
        
        if len(ch_keycodes) == 0 and len(character) == 1:
            ch_keycodes = self.display.keysym_to_keycodes(ord(character.lower()))
            ch_mask ^= X.LockMask
            
        if len(ch_keycodes) > 0:
            ch_keycode, mask = self.__findUsableKeycode(ch_keycodes)
            if ch_keycode == None or mask == None:
                return None, None
            else:
                ch_mask ^= mask
        else:
            return None, None
        
        if ch_mask ^ 4 < 4:
            ch_mask ^= 4
            ch_mask ^= self.modmasks[self.alt_gr_key]
        
        return ch_keycode, ch_mask

class KeyboardEvent(KeyboardEventMeta):
    """
    The PyKeyboardEvent implementation for X11 systems (mostly linux). This
    allows one to listen for keyboard input.
    """
    def __init__(self, display=None):
        PyKeyboardEventMeta.__init__(self)
        self.display = Display(display)
        self.display2 = Display(display)
        self.ctx = self.display2.record_create_context(
            0,
            [record.AllClients],
            [{
                    'core_requests': (0, 0),
                    'core_replies': (0, 0),
                    'ext_requests': (0, 0, 0, 0),
                    'ext_replies': (0, 0, 0, 0),
                    'delivered_events': (0, 0),
                    'device_events': (X.KeyPress, X.KeyRelease),
                    'errors': (0, 0),
                    'client_started': False,
                    'client_died': False,
            }])
        self.shift_state = 0  # 0 is off, 1 is on
        self.alt_state = 0  # 0 is off, 2 is on
        self.mod_keycodes = self.get_mod_keycodes()

    def run(self):
        """Begin listening for keyboard input events."""
        self.state = True
        if self.capture:
            self.display2.screen().root.grab_keyboard(True, X.KeyPressMask | X.KeyReleaseMask, X.GrabModeAsync, X.GrabModeAsync, 0, 0, X.CurrentTime)

        self.display2.record_enable_context(self.ctx, self.handler)
        self.display2.record_free_context(self.ctx)

    def stop(self):
        """Stop listening for keyboard input events."""
        self.state = False
        self.display.record_disable_context(self.ctx)
        self.display.ungrab_keyboard(X.CurrentTime)
        self.display.flush()
        self.display2.record_disable_context(self.ctx)
        self.display2.ungrab_keyboard(X.CurrentTime)
        self.display2.flush()

    def handler(self, reply):
        """Upper level handler of keyboard events."""
        data = reply.data
        while len(data):
            event, data = protocol.rq.EventField(None).parse_binary_value(data, self.display.display, None, None)
            if event.type == X.KeyPress:
                if self.escape_code(event):  # Quit if this returns True
                    self.stop()
                else:
                    self._key_press(event.detail)
            elif event.type == X.KeyRelease:
                self._key_release(event.detail)
            else:
                print('WTF: {0}'.format(event.type))

    def _key_press(self, keycode):
        """A key has been pressed, do stuff."""
        #Alter modification states
        if keycode in self.mod_keycodes['Shift'] or keycode in self.mod_keycodes['Lock']:
            self.toggle_shift_state()
        elif keycode in self.mod_keycodes['Alt']:
            self.toggle_alt_state()
        else:
            self.key_press(keycode)

    def _key_release(self, keycode):
        """A key has been released, do stuff."""
        #Alter modification states
        if keycode in self.mod_keycodes['Shift']:
            self.toggle_shift_state()
        elif keycode in self.mod_keycodes['Alt']:
            self.toggle_alt_state()
        else:
            self.key_release(keycode)

    def escape_code(self, event):
        if event.detail == self.lookup_character_value('Escape'):
            return True
        return False

    def lookup_char_from_keycode(self, keycode):
        keysym =self.display.keycode_to_keysym(keycode, self.shift_state + self.alt_state)
        if keysym:
            char = self.display.lookup_string(keysym)
            return char
        else:
            return None

    def get_mod_keycodes(self):
        """
        Detects keycodes for modifiers and parses them into a dictionary
        for easy access.
        """
        modifier_mapping = self.display.get_modifier_mapping()
        modifier_dict = {}
        nti = [('Shift', X.ShiftMapIndex),
               ('Control', X.ControlMapIndex), ('Mod1', X.Mod1MapIndex),
               ('Alt', X.Mod1MapIndex), ('Mod2', X.Mod2MapIndex),
               ('Mod3', X.Mod3MapIndex), ('Mod4', X.Mod4MapIndex),
               ('Mod5', X.Mod5MapIndex), ('Lock', X.LockMapIndex)]
        for n, i in nti:
            modifier_dict[n] = list(modifier_mapping[i])
        return modifier_dict

    def lookup_character_value(self, character):
        """
        Looks up the keysym for the character then returns the keycode mapping
        for that keysym.
        """
        ch_keysym = XK.string_to_keysym(character)
        if ch_keysym == 0:
            ch_keysym = XK.string_to_keysym(SPECIAL_X_KEYSYMS[character])
        return self.display.keysym_to_keycode(ch_keysym)

    def toggle_shift_state(self):
        '''Does toggling for the shift state.'''
        if self.shift_state == 0:
            self.shift_state = 1
        elif self.shift_state == 1:
            self.shift_state = 0
        else:
            return False
        return True

    def toggle_alt_state(self):
        '''Does toggling for the alt state.'''
        if self.alt_state == 0:
            self.alt_state = 2
        elif self.alt_state == 2:
            self.alt_state = 0
        else:
            return False
        return True

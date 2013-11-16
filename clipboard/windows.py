#coding: utf-8
import win32clipboard
import win32gui, win32con

class Clipboard:
    def get(self):
        win32clipboard.OpenClipboard()
        
        format = 0
        formats = []
        while 1:
            format = win32clipboard.EnumClipboardFormats(format)
            if not format:
                break
            formats.append(format)
            
        if win32con.CF_UNICODETEXT in formats:
            data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        elif win32con.CF_TEXT in formats:
            data = win32clipboard.GetClipboardData(win32con.CF_TEXT)
        else:
            data = u''

        win32clipboard.CloseClipboard()
        
        return data

    def set(self, text):
        win32clipboard.OpenClipboard() 
        win32clipboard.EmptyClipboard()

        if isinstance(text, unicode):
            result = win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        elif isinstance(text, str):
            result = win32clipboard.SetClipboardData(win32con.CF_TEXT, text)
        else:
            result = False
        
        win32clipboard.CloseClipboard()
        
        return result
        
    def clear(self):
        win32clipboard.OpenClipboard() 
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()

if __name__ == '__main__':    
    text = u'azertyuiop^$*µù'
    clip = Clipboard()
    print clip.get()
    clip.set(text)
    assert(clip.get() == text)
    clip.clear()
    print clip.get()
    assert(clip.get() == u'')

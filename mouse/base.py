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

"""
The goal of PyMouse is to have a cross-platform way to control the mouse.
PyMouse should work on Windows, Mac and any Unix that has xlib.

As the base file, this provides a rough operational model along with the
framework to be extended by each platform.
"""

import time
from threading import Thread

class ScrollSupportError(Exception):
    pass


class PyMouseMeta(object):

    def press(self, x=None, y=None, button=1):
        """
        Press the mouse on a given x, y and button.
        Button is defined as 1 = left, 2 = right, 3 = middle.
        """

        raise NotImplementedError

    def release(self, x=None, y=None, button=1):
        """
        Release the mouse on a given x, y and button.
        Button is defined as 1 = left, 2 = right, 3 = middle.
        """

        raise NotImplementedError

    def click(self, x=None, y=None, button=1, n=1, interval=0):
        """
        Click a mouse button n times on a given x, y.
        Button is defined as 1 = left, 2 = right, 3 = middle.
        """
        
        for i in range(n):
            self.press(x, y, button)
            self.release(x, y, button)
            time.sleep(interval)

    def scroll(self, vertical=None, horizontal=None, depth=None):
        """
        Generates mouse scrolling events in up to three dimensions: vertical,
        horizontal, and depth (Mac-only). Values for these arguments may be
        positive or negative numbers (float or int). Refer to the following:
            Vertical: + Up, - Down
            Horizontal: + Right, - Left
            Depth: + Rise (out of display), - Dive (towards display)

        Dynamic scrolling, which is used Windows and Mac platforms, is not
        implemented at this time due to an inability to test Mac code. The
        events generated by this code will thus be discrete units of scrolling
        "lines". The user is advised to take care at all times with scrolling
        automation as scrolling event consumption is relatively un-standardized.

        Float values will be coerced to integers.
        """

        raise NotImplementedError

    def move(self, x, y):
        """Move the mouse to a given x and y"""

        raise NotImplementedError

    def drag(self, x, y):
        """Drag the mouse to a given x and y.
        A Drag is a Move where the mouse key is held down."""

        raise NotImplementedError

    def position(self):
        """
        Get the current mouse position in pixels.
        Returns a tuple of 2 integers
        """

        raise NotImplementedError

    def screen_size(self):
        """
        Get the current screen size in pixels.
        Returns a tuple of 2 integers
        """

        raise NotImplementedError


class PyMouseEventMeta(Thread):
    def __init__(self, capture=False, capture_move=False):
        Thread.__init__(self)
        self.daemon = True
        self.capture = capture
        self.capture_move = capture_move
        self.state = True

    def stop(self):
        self.state = False

    def click(self, x, y, button, press):
        """Subclass this method with your click event handler"""
        pass

    def move(self, x, y):
        """Subclass this method with your move event handler"""
        pass
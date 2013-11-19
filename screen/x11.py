from ..util import Rect, Point, XObject

class Screen(XObject):
    def __init__(self, display=None):
        XObject.__init__(self, display=display)
        
    def get_screen_size(self):
            root = self.display.screen().root
            geom = root.get_geometry()._data
            
            return Rect(Point(geom["x"], geom["y"]),
                        width=geom["width"],
                        height=geom["height"])
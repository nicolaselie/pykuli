import sys

TIMEOUT = 3
FOREVER = -1

def set_timeout(timeout):
    TIMEOUT = timeout
    
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def to_tuple(self):
        return self.x, self.y

class Rect(object):
    def __init__(self, p1, p2=None, width=None, height=None, delta=(0,0)):
        #http://codereview.stackexchange.com/questions/31352/overlapping-rectangles-interview-question
        if width != None and height != None:
           p2 = Point(p1.x + width, p1.y + height)
                       
        self.x1 = min(p1.x, p2.x) #left
        self.y1 = min(p1.y, p2.y) #bottom
        self.x2 = max(p1.x, p2.x) #right
        self.y2 = max(p1.y, p2.y) #top
        
        self.width = abs(self.x2 - self.x1)
        self.height = abs(self.y2 - self.y1)
        
        self.center = Point(self.x1 + int(self.width/2),
                            self.y1 + int(self.height/2))
        
    def intersect(self, rect):
        #http://www.nerdparadise.com/tech/interview/intersectrectangles/
        separate = self.x2 < rect.x1 \
                or self.x1 > rect.x2 \
                or self.y2 < rect.y1 \
                or self.y1 > rect.y2

        return not separate

class Match(object):
    def __init__(self, rect, score):
        self.rect = rect
        self.score = score
    
    def __repr__(self):
        return "M[{x},{y} {width}x{height}]@S(S(0)[0,0 1920x1080]) " \
               "S:{score:0.2f} Center:{center_x},{center_y}".format(
                   x=self.rect.x1, y=self.rect.y1,
                   width=self.rect.width, height=self.rect.height,
                   score=self.score,
                   center_x=self.rect.center.x, center_y=self.rect.center.y) 

if sys.platform == 'win32':
    from .windows import *
else:
    from .x11 import *

from ..mouse import PyMouse as Mouse
from ..keyboard import PyKeyboard as Keyboard
from ..clipboard import Clipboard
from ..screenshot import Screenshot

import numpy
import cv2
from PIL import Image

class Pykuli(object):
    def __init__(self):
        self.keyboard = Keyboard()       
        self.mouse = Mouse()
        self.clipboard = Clipboard()
        self.screenshot = Screenshot()
        
    def click(self, *args, **kwargs):
        if len(args) == 1:
            arg = args[0]
            if type(arg) == tuple:
                x, y = arg
            elif type(arg) == Point:
                x, y = arg.x, arg.y
        elif len(args) == 2:
            for arg in args:
                assert(type(arg) == int)
            x, y = args
        else:
            raise TypeError("%s receives wrong number of arguments." \
                % sys._getframe().f_code.co_name)
        self.mouse.click(x=x, y=y, **kwargs)
        
    def doubleClick(self, *args, **kwargs):
        kwargs['n'] = 2
        self.click(*args, **kwargs)
        
    def rightClick(self, *args, **kwargs):
        kwargs['button'] = 2
        self.click(*args, **kwargs)
    
    def move(self, *args):
        if len(args) == 1:
            arg = args[0]
            if type(arg) == tuple:
                x, y = arg
            elif type(arg) == Point:
                x, y = arg.x, arg.y
        elif len(args) == 2:
            for arg in args:
                assert(type(arg) == int)
            x, y = args
        else:
            raise TypeError("%s receives wrong number of arguments." \
                % sys._getframe().f_code.co_name)
        self.mouse.move(x, y)
    
    def hover(self, *args):
        self.move(*args)
        
    def press(self, *args):
        self.keyboard.press(*args)
        
    def release(self, *args):
        self.keyboard.release(*args)
        
    def tap_key(self, *args):
        self.keyboard.tap_key(*args)
        
    def type_string(self, *args):
        self.keyboard.type_string(*args)
        
    def dragDrop(self, *args):
        if len(args) == 2:
            p1, p2 = args
            for i in range(len(args)):
                if type(args[i]) == Point:
                    args[i] = args[i].to_tuple()
                
            if type(p1) == tuple:
                x1, y1 = p1
            if type(p2) == tuple:
                x2, y2 = p2
        elif len(args) == 4:
            for arg in args:
                assert(type(arg) == int)
            x1, y1, x2, y2 = args
        else:
            raise TypeError("%s receives wrong number of arguments." \
                % sys._getframe().f_code.co_name)
        self.press(x=x1, y=y1, button=1)
        self.move(x2, y2)
        time.sleep(0.1)
        self.release(button=1)
    
    def type(self, text, interval=0, modifier=0):
        self.type_string(text.replace('\n', '\r\n'), interval, modifier)
        
    def paste(self, text):
        self.clipboard.set(text)
        self.tap_key('v', modifier=FLAG_CTRL)
        
    def grabScreen(self, rect=None):
        if rect == None:
            screenshot = self.screenshot.grab()
        else:
            screenshot = self.screnshot.grab(rect.x(), rect.y(), rect.width(), rect.height())

        return self.__PILToCVImage(screenshot)
        
    def find(self, image, threshold=0.7, delta=(0,0)):
        '''
        Find a template image on the screen and return the coordinates of the best match
        '''
        if type(image) == str or type(image) == byte:
            image = cv2.imread(image)
        
        #Capture screen
        screen = self.grabScreen()
        
        if image == None or screen == None:
            return False
        
        #Try to find the template image on the screen
        result = cv2.matchTemplate(screen, image, cv2.TM_CCOEFF_NORMED)
        
        #Get the pixel with the highest
        _, max_score, _, coord = cv2.minMaxLoc(result)

        #Check if this highest score is higher than the threshold
        #If yes, we have a match
        if max_score >= threshold:
            #Calculate the coordinate of the template's center + a delta
            width, height, _ = image.shape
            coord = (coord[0] + int(width / 2) + int(delta[0]), \
                     coord[1] + int(height / 2) + int(delta[0]))
            
            return coord
        else:
            #No match
            return False
    
    def findAll(self, image, threshold=0.7, delta=(0,0)):
        '''
        Find a template image on the screen and return the coordinates
        of all the matches sorted with best matches first
        '''
        if type(image) == str or type(image) == byte:
            image = cv2.imread(image)
        
        #Capture screen
        screen = self.grabScreen()
        
        if image == None or screen == None:
            return []
        
        #Try to find the template image on the screen
        result = cv2.matchTemplate(screen, image, cv2.TM_CCOEFF_NORMED)
        
        #Get the pixels where score is higher than the threshold
        coords = numpy.where(result >= threshold)
        
        #If we have matches
        if len(coords) > 0:
            #Sort the matches by decreasing score
            coords = sorted(zip(*coords[::-1]), 
                            key=lambda coord: result[coord[1]][coord[0]],
                            reverse=True)
            
            
            #Calculate the coordinate of the template's center + a delta
            height, width, _ = image.shape
            matches = []
            for coord in coords:
                point = Point(coord[0], coord[1])
                rect = Rect(point, width=width, height=height, delta=delta)
                intersect = False
                for match in matches:
                    if match.rect.intersect(rect):
                        intersect = True
                        break
                if not intersect:
                    score = result[point.y][point.x]
                    m = Match(rect, score)
                    matches.append(m)
                
            #return found coordinates
            return matches
        else:
            #No match
            return []
        
    def __PILToCVImage(self, image):
        return cv2.cvtColor(numpy.asarray(image), cv2.COLOR_RGB2BGR)

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

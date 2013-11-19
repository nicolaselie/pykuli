import numpy
import cv2
from PIL import Image
import sys

from ..mouse import Mouse
from ..keyboard import Keyboard
from ..clipboard import Clipboard
from ..screen import Screen
from ..screenshot import Screenshot

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
    
    def hover(self, *args, **kwargs):
        self.move(*args, **kwargs)
        
    def press(self, *args, **kwargs):
        self.keyboard.press(*args, **kwargs)
        
    def release(self, *args, **kwargs):
        self.keyboard.release(*args, **kwargs)
        
    def tap_key(self, *args, **kwargs):
        self.keyboard.tap_key(*args, **kwargs)
        
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
        self.tap_key('v', modifier=self.keyboard.flags['Ctrl'])
        
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

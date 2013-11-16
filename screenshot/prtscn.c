#include <stdio.h>
#include <X11/X.h>
#include <X11/Xlib.h>
//Compile hint: gcc -shared -O3 -lX11 -fPIC -Wl,-soname,prtscn -o prtscn.so prtscn.c

int* getScreenSize(void);
void getScreen(const int, const int, const int, const int, unsigned char *);

int* getScreenSize(void) {
    static int result[2];
    XWindowAttributes attr;
    
    Display *display = XOpenDisplay(NULL);
    Window root = DefaultRootWindow(display);
    
    XGetWindowAttributes(display, root, &attr);
    result[0] = attr.width;
    result[1] = attr.height;
    
    XCloseDisplay(display);
    
    return result;
}

void getScreen(const int xx, const int yy, const int width, const int height, /*out*/ unsigned char *data) 
{   
   Display *display = XOpenDisplay(NULL);
   Window root = DefaultRootWindow(display);
   XImage *image = XGetImage(display, root, xx, yy, width, height, AllPlanes, ZPixmap);
   
   unsigned long red_mask = image->red_mask;
   unsigned long green_mask = image->green_mask;
   unsigned long blue_mask = image->blue_mask;
   int x, y;
   for (x = 0; x < width; x++) {
      for (y = 0; y < height; y++) {
         unsigned long pixel = XGetPixel(image, x, y);
         int ii = (x + width * y) * 3;

         unsigned char blue = pixel & blue_mask;
         unsigned char green = (pixel & green_mask) >> 8;
         unsigned char red = (pixel & red_mask) >> 16;

         data[ii + 2] = blue;
         data[ii + 1] = green;
         data[ii + 0] = red;
      }
   }
   
   XCloseDisplay(display);
}

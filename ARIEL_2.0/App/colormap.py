import math

def floatRgb(mag, cmin, cmax):
       """
       Return a tuple of floats between 0 and 1 for the red, green and
       blue amplitudes.
       """

       try:
              # normalize to [0,1]
              x = float(mag-cmin)/float(cmax-cmin)
       except:
              # cmax = cmin
              x = 0.5
       blue = min((max((4*(0.75-x), 0.)), 1.))
       red  = min((max((4*(x-0.25), 0.)), 1.))
       green= min((max((4*math.fabs(x-0.5)-1., 0.)), 1.))
       return (red, green, blue)


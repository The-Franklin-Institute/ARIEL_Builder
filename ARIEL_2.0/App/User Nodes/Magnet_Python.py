
#ARIEL plugin example

#This line must be here
from arielplugin import *

import arieltypes

import math
import time
import numpy

#Multiplier is the name of our node
class MagnetField(Node):

    #This is the label for our node in the builder"
    ARIELCLASS = "Magnetic Field"

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        #These are the connections to our node.
        #The first parameter e.g. inA, is the local variable name
        #we will use to access this input. i.e. self.inA
        #The second paramter is the type of input.
        #The various types of inputs are defined in node.py
        #The last parameter is the label for the input in the builder.
        self.connections.append(("gridsize", NumberInput,"grid size"))
        self.connections.append(("xgridpts", NumberInput,"x grid points"))
        self.connections.append(("ygridpts", EventInput, "y grid points"))
        self.connections.append(("length", NumberInput,"length"))
        self.connections.append(("width", NumberInput,"width"))
        self.connections.append(("separation", EventInput, "magnet separation"))
        self.connections.append(("angle1", NumberInput,"mag1 rotation"))
        self.connections.append(("angle2", NumberInput,"mag2 rotation"))
        self.connections.append(("Field", Scalar2DInput, "Magnetic Field Values"))
        self.connections.append(("fldlines", VectorListOutput,"Field Lines"))
        self.connections.append(("sumout", Scalar2DOutput,"Sum Field Lines"))

        #This is a simple description of the node that appears when double clicked.
        self.doSimplePropertyWindow("Magnetic Fields")

        self.initializeConnections()

    

    #This method is called from the player for the node to do whatever it does.
    def compute(self):
        tttt = time.time()

        def GetPolarB(InterpFld, x, y):

        #Returns angle of field InterpFld at point x, y
            theta = 0.
            r = math.sqrt(x * x + y * y)
            theta = math.atan2(InterpFld[1], InterpFld[0])
            
            return (theta)    


        def BinLinInterp(x, y, Field0):

            #zero out local field values

            InterpFldBL = [0, 0]

            #find integer values of closest grid point coordinates

            n = ((nmax) / 2) + x / grid
            m = ((mmax) / 2) + y / grid

            n = int(n)
            m = int(m)

            #shift to correct between axis and grid for edge check

            n1 = n + 1
            m1 = m + 1

            #print "binlininterp, nmax, mmax, n, m, n1, m1", nmax, mmax, n, m, n1, m1

            if n1 > nmax - 1 or m1 > mmax - 1 or n < 0 or m < 0:
                InterpFldBL[0] = 0
                InterpFldBL[1] = 0
                return (InterpFldBL)

            #define variables for interpoloation
            x00 = ((n - ((nmax) / 2)) * grid) # x-axis value of grid point
            y00 = ((m - ((mmax) / 2)) * grid) # y-axis value of grid point
            dx21 = grid
            dy21 = grid
            dx20 = (x00 + grid) - x
            dx01 = x - x00
            dy20 = (y00 + grid) - y
            dy01 = y - y00

            #calcualte the values

            InterpFldBL[0] = (Field0[n, m, 0] * dx20 * dy20 + Field0[n1, m, 0] * dx01 * dy20 + Field0[n, m1, 0] * dx20 * dy01 + Field0[n1, m1, 0] * dx01 * dy01) / (dx21 * dy21)
            InterpFldBL[1] = (Field0[n, m, 1] * dx20 * dy20 + Field0[n1, m, 1] * dx01 * dy20 + Field0[n, m1, 1] * dx20 * dy01 + Field0[n1, m1, 1] * dx01 * dy01) / (dx21 * dy21)
        

            return (InterpFldBL)
    
        def BinLinInterp2(x, y):

            #Zero out local field

            InterpFldBL2 = [0, 0]

            #find integer values of closest grid point coordinates. Note that grid 0,0 is lower left and axis 0,0 is upper left

            n = x / grid
            m = (y + ((grid * mmax /2) - 400.)) / grid

            n = int(n)
            m = int(m)


            n1 = n + 1
            m1 = m + 1

            #print "binlin n, m= ", n, m
            if (n1 > nmax - 1) or (m1 > mmax - 1) or (n < 0) or (m < 0):
                InterpFldBL2[0] = InterpFldBL2[1] = 0.
                return (InterpFldBL2)

            #define variables for interpoloation
            #Note: we need to account for the fact that there are two axes, the grid axis (n,m) and the view axis (x, y)
            x00 = ((n - ((nmax) / 2)) * grid) # x-axis value of grid point -- in grid axes
            y00 = ((m - ((mmax) / 2)) * grid) # y-axis value of grid point -- in grid axes
            dx21 = grid
            dy21 = grid
            dx20 = (x00 + grid) - (x - 520.) #axes shift
            dx01 = (x - 520.) - x00
            dy20 = (y00 + grid) - (y - 400.) #axes shift
            dy01 = (y - 400.) - y00

            #calcualte the values

            InterpFldBL2[0] = (SumFld[n, m, 0] * dx20 * dy20 + SumFld[n1, m, 0] * dx01 * dy20 + SumFld[n, m1, 0] * dx20 * dy01 + SumFld[n1, m1, 0] * dx01 * dy01) / (dx21 * dy21)
            InterpFldBL2[1] = (SumFld[n, m, 1] * dx20 * dy20 + SumFld[n1, m, 1] * dx01 * dy20 + SumFld[n, m1, 1] * dx20 * dy01 + SumFld[n1, m1, 1] * dx01 * dy01) / (dx21 * dy21)

            Br = math.sqrt(InterpFldBL2[0] * InterpFldBL2[0] + InterpFldBL2[1] * InterpFldBL2[1])

            if abs(Br) > 10.:
                #print "Br in Binlin", x00, y00, x, y, dx01, dy01
                InterpFldBL2[0] = InterpFldBL2[1] = 0.
            

            return (InterpFldBL2)

        print "time for stuff:", time.time() - tttt
        #Nodes should define reasonable default values if they receive no input data

        print "Main loop"


        if self.gridsize.value == None:
            self.gridsize.value = 1.
        if self.xgridpts.value == None:
            self.xgridpts.value = 50
        if self.ygridpts.value == None:
            self.ygridpts.value = 50
        if self.length.value == None:
            self.length.value = 0
        if self.width.value == None:
            self.width.value = 0
        if self.separation.value == None:
            self.separation.value = 0
        if self.angle1.value == None:
            self.angle1.value = 0
        if self.angle2.value == None:
            self.angle2.value = 0


        self.angle1.value = self. angle1.value/57.3
        self.angle2.value = self. angle2.value/57.3
        #print "Thetas are:", self.angle1.value, self.angle2.value

        magsep = self.separation.value

        grid = self.gridsize.value

        nmax = int(self.xgridpts.value)

        mmax = int(self.ygridpts.value)

        lgnth = self.length.value

        wdth = self.width.value

        magsep = self.separation.value

        InterpFld = [ 0, 0 ]
        TestFld = [0, 0]

        SumFld = numpy.zeros((nmax + 1, mmax + 1, 2))
        Field0 = numpy.zeros((nmax + 1, mmax + 1, 2))

        #print "nmax, mmax, zero Sum = ", nmax, mmax, Field0
        #print "<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>"

        if self.Field.value == None:
            self.Field.value = Field0

        Field0 = self.Field.value

        #print "nmax, mmax, zero Second = ", nmax, mmax, Field0
        #print "*******************************************"

        #Start by defining the field for the frame take the input separation value (distance between magent centers, magsep) and rotation (th1, th2) for each and build a summative field

        displace = magsep / 2.
        dangle = self.angle1.value

        print "Field loop"

        for nfield in range(2):

            #define field displacement as left (-magsep/2) for field 0 and right (magsep/2) for field 1

            if nfield > 0:
                displace = - magsep / 2.
                dangle = self.angle2.value

            #Note: need to watch grid 0, 0 and AREIL 0, 0

            Brmax2 = 0.

            for ngrd in range (nmax + 1):
                for mgrd in range (mmax + 1):

                    nx = ngrd - ((nmax) / 2)
                    nx = int(nx)

                    my = mgrd - ((mmax) / 2)
                    my = int(my)

                    #change the frame of reference displace field, change to polar and rotate
                    
                    x0 = nx * grid + displace
                    y0 = my * grid


                    r0 = math.sqrt(x0 * x0 + y0 * y0)
                    theta0 = math.atan2(y0, x0)

                    theta = theta0 - dangle

                    x = r0 * math.cos(theta)
                    y = r0 * math.sin(theta)

                    #print "ngrid, mgrid", ngrd, mgrd

                    InterpFld = BinLinInterp(x, y, Field0)

                    #Now rotate field back to reference coordinate system

                    Br = math.sqrt(InterpFld[0] * InterpFld[0] + InterpFld[1] * InterpFld[1])
                    ThetaB = math.atan2(InterpFld[1], InterpFld[0])
                    ThetaB = ThetaB + dangle
                    Bx = Br * math.cos(ThetaB)
                    By = Br * math.sin(ThetaB)

                    if Br > Brmax2:
                        Brmax2 = Br

                    SumFld[ngrd, mgrd, 0] = SumFld[ngrd, mgrd, 0] + Bx
                    SumFld[ngrd, mgrd, 1] = SumFld[ngrd, mgrd, 1] + By

                    #print ngrd, mgrd, SumFld[ngrd, mgrd, 0], SumFld[ngrd, mgrd, 1]
           
        #print "max sum field", Brmax2

        self.sumout.value = SumFld

        #print "Summary Field is >>>>>>>>>>>>>>>>>>>>>>>>", self.sumout.value
        #print "End of field"

        #Set the vector array                    

        vectors = []

        v = arieltypes.Vector()

        # Set fixed line parameters, white, no arrows

        v.r1 = 1
        v.g1 = 1
        v.b1 = 1

        v.r2 = 1
        v.g2 = 1
        v.b2 = 1

        v.hasArrowhead = 0                    

        #With the field defined for the rotation, loop through points. Assume seven from each pole

        #Define grid boundaries

        xmin = 520. - grid * nmax / 2.
        xmax = xmin + nmax * grid

        ymin = 400. - grid * mmax / 2.
        ymax = ymin + mmax * grid

        print "Line loop"

        for nmag in range(2):

            dangle = self.angle2.value

            displace = - magsep / 2.

            if nmag > 0:
                dangle = self.angle1.value
                displace = - displace

            for npole in range(2):
    
                xstart = lgnth / 2.
                isign = -1

                if npole > 0:
                    xstart = - lgnth / 2.
                    isign = 1
            
                for nline in range (-1, 2):
                    
                    offfield = 0
                    
                    ystart = 0.0 + nline * wdth / 8.

                    rstart = math.sqrt(xstart * xstart + ystart * ystart)
                    thstart = math.atan2(ystart, xstart)

                    thstart = thstart + dangle

                    # Assume that the magnets are symetrically centered on screen center 520, 400

                    x0 = rstart * math.cos(thstart) - displace + 520.0
                    y0 = rstart * math.sin(thstart) + 400.0

                    #print "Starting Values:", displace, xstart, ystart, x0, y0
                    

                    dt = 4.5

                    x = x0
                    y = y0

                    #print "line data (x,y,wdth,nline) is:", x, y, xstart, ystart, nline
            
                    for n in range (100):
    
                        v.x1 = x
                        v.y1 = y
    
                        v.hasArrowhead = 0

                        #check to see if point is nearing grid boundaries and if so stop line
                        #print "Range check", nmax, mmax, grid, x, y
                        if x > (xmax - grid) or x < (xmin + grid) or y > (ymax - grid) or y < (ymin + grid):
                            #print "Fails range check", nmag, npole, nline, n, x, y
                            break
    
    
                        #Since we are integrating along a line we need the slope at each location which is the theta defined by By/Bx at location x, y
                        #We need to account for lines starting at +/- so use isign

                        InterpFld = BinLinInterp2(x, y)
                        
                        InterpFld[0] = InterpFld[0]*isign
                        InterpFld[1] = InterpFld[1]*isign

                        theta = GetPolarB(InterpFld, x, y) + 3.14159

                        if n < 10:
                            #TestFld = BinLinInterp(x, y)
                            ptheta = theta
                            #if theta > 3.14159:
                             #   ptheta = (theta - 3.14159) * 57.3
                            #print "in RK routine:", nline, n, x, y, InterpFld[0], InterpFld[1], ptheta
                            

                        kx1 = dt * math.cos(theta)
                        ky1 = dt * math.sin(theta)

                        xk1 = x + dt/2.0 * math.cos(theta)
                        yk1 = y + dt/2.0 * math.sin(theta)

                        InterpFld = BinLinInterp2(xk1, yk1)
                        InterpFld[0] = InterpFld[0]*isign
                        InterpFld[1] = InterpFld[1]*isign

                        theta = GetPolarB(InterpFld, x, y)
                    
                        xk2 = x + .5 * dt * math.cos(theta)
                        yk2 = y + .5 * dt * math.sin(theta)

                        kx2 = dt * math.cos(theta)
                        ky2 = dt * math.sin(theta)
                    
    
                        InterpFld = BinLinInterp2(xk2, yk2)
                        InterpFld[0] = InterpFld[0]*isign
                        InterpFld[1] = InterpFld[1]*isign

                        theta = GetPolarB(InterpFld, x, y)
                    
                        xk3 = x + .5 * dt * math.cos(theta)
                        yk3 = y + .5 * dt * math.sin(theta)

                        kx3 = dt * math.cos(theta)
                        ky3 = dt * math.sin(theta)
    
                        InterpFld = BinLinInterp2(xk3, yk3)
                        InterpFld[0] = InterpFld[0]*isign
                        InterpFld[1] = InterpFld[1]*isign

                        theta = GetPolarB(InterpFld, x, y)
                    
                        xk4 = x + .5 * dt * math.cos(theta)
                        yk4 = y + .5 * dt * math.sin(theta)

                        kx4 = dt * math.cos(theta)
                        ky4 = dt * math.sin(theta)
                    
                        xf = x + (dt/6.0) * (kx1 + 2.*kx2 + 2.*kx3 + kx4)
                        yf = y + (dt/6.0) * (ky1 + 2.*ky2 + 2.*ky3 + ky4)

            
                        v.x2 = xf
                        v.y2 = yf
                        #if xf == 0 and yf == 0:
                            #print "Integration start stop = ", x, y, xf, yf

                        vectors.append(v)

                        v = arieltypes.Vector()
            
                        x = xf
                        y = yf

                        
                        

                        

        #v.x1 = 560.
        #v.x2 = 580.
        #v.y1 = 400.
        #v.y2 = 440
        #v.hasArrowhead = 1

        #vectors.append(v)


        #Here we send it all back
        
        self.fldlines.value = vectors


#ARIEL plugin example

#This line must be here
from arielplugin import *

import arieltypes

import math

import numpy

#Multiplier is the name of our node
class ShowMagnetField(Node):

    #This is the label for our node in the builder"
    ARIELCLASS = "Show Field"

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        #These are the connections to our node.
        #The first parameter e.g. inA, is the local variable name
        #we will use to access this input. i.e. self.inA
        #The second paramter is the type of input.
        #The various types of inputs are defined in node.py
        #The last parameter is the label for the input in the builder.
        self.connections.append(("Field", Scalar2DInput, "Magnetic Field Values"))
        self.connections.append(("griddim", NumberInput, "Number of grid points"))        
        self.connections.append(("gridsz", NumberInput, "Grid Scale"))
        self.connections.append(("fldlines", VectorListOutput,"Field Lines"))

        #This is a simple description of the node that appears when double clicked.
        self.doSimplePropertyWindow("Show Fields")

        self.initializeConnections()

    

    #This method is called from the player for the node to do whatever it does.
    def compute(self):

        print "Show Field"
        
        #This node sends a vector list represeting the direction of the magnetic field at all grid locations

        #Nodes should define reasonable default values if they receive no input data
    
        #use 50 x 50 as default grid dimension

        if self.griddim.value == None:
            self.griddim.value = 50

        nmmax = self.griddim.value

        if self.gridsz.value == None:
            self.gridsz.value = 1.

        nmmax = self.griddim.value    

        #print "nm max = ", nmmax
        Fld = numpy.zeros((nmmax + 1, nmmax + 1, 2))

        grid = self.gridsz.value

        #calculate x, y offsets based on field center at 520, 400

        nmcntr = nmmax / 2. #center grid point
        llft00 = nmcntr * grid  #location of origion in grid axes

        x00 = 520. - llft00  # x origion in view axes
        y00 = 400. - llft00  # y origion in view axes


        if self.Field.value == None:
            #print "EMPTY"
            self.Field.value = Fld


        #Fld = self.Field.value

        #Set the vector array                    

        vectors = []

        v = arieltypes.Vector()

        # Set fixed line parameters, white, no arrows

        v.r1 = 1
        v.g1 = 1
        v.b1 = 1

        v.r2 = 1
        v.g2 = 0
        v.b2 = 0

        v.hasArrowhead = 0                    

        maxfield = 0.
        nxmax = 0
        nymax = 0

        #loop through each grid point

        for nx in range(nmmax):

            x = nx * grid + x00

            for ny in range(nmmax):
    
                y = ny * grid + y00
 
    
                v.x1 = x
                v.y1 = y
                v.x2 = v.x1
                v.y2 = v.y1
                
                #Commented out section displays relative field size scaled and limited
                #scale = 0.
                
                #if math.fabs(Field[nx, ny, 0]) < 1. and math.fabs(Field[nx, ny, 1]) < 1.:
                #    scale = 10.
                

                #v.x2 = x + Field[nx, ny, 0] * 10. * scale
                #v.y2 = y + Field[nx, ny, 1] * 10. * scale

                #print "Field values,", nx, ny

                Br = math.sqrt(self.Field.value[nx, ny, 0] * self.Field.value[nx, ny, 0] + self.Field.value[nx, ny, 1] * self.Field.value[nx, ny, 1])

                #Find direction of field at all locations

                theta = math.atan2(self.Field.value[nx, ny, 1], self.Field.value[nx, ny, 0])
                xdir = .75 * grid * math.cos(theta)
                ydir = .75 * grid * math.sin(theta)

                v.x2 = x + xdir
                v.y2 = y + ydir

                #if nx == 25.:
                #    print Br

                if maxfield < Br:
                    maxfield = Br
                    nxmax =  nx
                    nymax = ny

                vectors.append(v)

                v = arieltypes.Vector()
                v.r1 = 1
                v.g1 = 1
                v.b1 = 1

                v.r2 = 1
                v.g2 = 0
                v.b2 = 0

                v.hasArrowhead = 0  
 
        #Here we send it all back

        #print "Max Field = ", nxmax, nymax, maxfield
        
        self.fldlines.value = vectors

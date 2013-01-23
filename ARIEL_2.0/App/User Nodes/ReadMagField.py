from arielplugin import *

import arieltypes

import os
import numpy

from psl import util

#Multiplier is the name of our node
class ReadMagField(Node):

    #This is the label for our node in the builder"
    ARIELCLASS = "Read Mag Field"

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        #These are the connections to our node.
        #The first parameter e.g. inA, is the local variable name
        #we will use to access this input. i.e. self.inA
        #The second paramter is the type of input.
        #The various types of inputs are defined in node.py
        #The last parameter is the label for the input in the builder.
        self.connections.append(("Start", EventInput,"sketch start")) 
        self.connections.append(("griddim", NumberInput, "Number of grid points")) 
        self.connections.append(("field", Scalar2DOutput,"Field Lines"))

        #This is a simple description of the node that appears when double clicked.
        self.doSimplePropertyWindow("Read Field from file")

        self.initializeConnections()


    #This method is called from the player for the node to do whatever it does.
    def compute(self):

        print "Start Check", self.Start.value

        #check to see if this is the first time

        if self.Start.value == 0:
            print "Next time!"
            return

        print "First Time!"

        #set default grid 50 x 50, note all grids are assumed square

        if self.griddim.value == None:
            self.griddim.value = 50
            
        nmgrid = self.griddim.value

        magfile = util.currentDir + "/User Nodes/magfield.txt"

        infile = open(magfile, 'r')

        
        n = 0
        m = 0
        F = numpy.zeros((nmgrid + 1, nmgrid + 1, 2))

        nt = 1
        #print "<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>"
        for line in infile:

            #strip the header line (y dim, x dim, grid size, nx, ny)
            if nt == 0:
                line = line.strip()
                nt = 1
                continue
            
            line = line.strip()
            sline = line.split()
            F[n, m, 0] = sline[2]
            F[n, m, 1] = sline[3]


            # Note that we need to change the sign of By to account for the ARIEL positive y axis pointing down
            F[n, m, 1] = - F[n, m, 1]
        


            #print "Read Field", F[n, m, 0], F[n, m, 1]
            n = n + 1
            if n > (nmgrid - 1):
                n = 0
                m = m + 1
    
        infile.close()


        self.field.value = F

        #print self.field.value

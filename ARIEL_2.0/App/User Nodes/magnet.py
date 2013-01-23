
#ARIEL plugin example

#This line must be here
from arielplugin import *

from arieltypes import Vector

import math
import os

from psl import util

#Multiplier is the name of our node
class MagnetSimulation(Node):

    #This is the label for our node in the builder"
    ARIELCLASS = "magnet sim."

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        #These are the connections to our node.
        #The first parameter e.g. inA, is the local variable name
        #we will use to access this input. i.e. self.inA
        #The second paramter is the type of input.
        #The various types of inputs are defined in node.py
        #The last parameter is the label for the input in the builder.
        self.connections.append(("mag1r", NumberInput,"magnet 1 rotation"))
        self.connections.append(("mag2r", NumberInput,"magnet 2 rotation"))
        self.connections.append(("vectorListOut", VectorListOutput,"field lines"))

        #This is a simple description of the node that appears when double clicked.
        self.doSimplePropertyWindow("magnetic field simulation - takes as input the rotations of two magnets and outputs their field lines.")

        self.initializeConnections()

        self.simInitialized = 0

    def initializeSim(self):
        self.vectorListOut.value = []

        import magmaps

        magfile = util.currentDir + "/userscripts/magfield.txt"

        print "using file",magfile
        try:
            f = open(magfile)
            f.close()
        except:
            print "unable to load file",magfile
            return
        self.mag = magmaps.MagMap(magfile)
        self.simInitialized = 1


    #This method is called from the player for the node to do whatever it does.
    def compute(self):

        if not self.simInitialized:
            self.initializeSim()

        if self.mag1r.value == None:
            self.mag1r.value = 0

        if self.mag2r.value == None:
            self.mag2r.value = 0

        a = self.mag1r.value #* math.pi / 180
        b = self.mag2r.value #* math.pi / 180

#        print "angles",a,b
        self.mag.setAngles(a,b)
        self.mag.draw() #doesn't really draw anything

        v = []

        mf = self.mag.masterField;
#        print mf.getNumLines()

        for n in range(mf.getNumLines()):
            v.append(mf.getLine(n))
        
        self.vectorListOut.value = v

        




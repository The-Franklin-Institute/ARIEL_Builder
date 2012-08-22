
#ARIEL plugin example

#This line must be here
from arielplugin import *

import arieltypes

#Multiplier is the name of our node
class VectorDemo(Node):

    #This is the label for our node in the builder"
    ARIELCLASS = "Vector Demo"

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        #These are the connections to our node.
        #The first parameter e.g. inA, is the local variable name
        #we will use to access this input. i.e. self.inA
        #The second paramter is the type of input.
        #The various types of inputs are defined in node.py
        #The last parameter is the label for the input in the builder.
        self.connections.append(("out", VectorListOutput,"output"))

        #This is a simple description of the node that appears when double clicked.
        self.doSimplePropertyWindow("this node generates a simple test pattern of vector data.")

        self.initializeConnections()

    #This method is called from the player for the node to do whatever it does.
    def compute(self):

        vectors = []

        v = arieltypes.Vector()
        v.x1 = 300
        v.y1 = 300

        v.x2 = 600
        v.y2 = 300

        v.r2 = 1
        v.g2 = 0
        v.b2 = 0

        v.hasArrowhead = 1
        
        vectors.append(v)

        v = arieltypes.Vector()
        v.x1 = 600
        v.y1 = 350

        v.x2 = 600
        v.y2 = 600

        v.r1 = 1
        v.g1 = 0
        v.b1 = 0

        v.r2 = 0
        v.g2 = 0
        v.b2 = 1        

        v.hasArrowhead = 0

        vectors.append(v)

        self.out.value = vectors

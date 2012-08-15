
#ARIEL plugin example

#This line must be here
from arielplugin import *
from openframeworks import *

#Multiplier is the name of our node
class ScreenSize(Node):

    #This is the label for our node in the builder"
    ARIELCLASS = "ScreenSize"

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        #These are the connections to our node.
        #The first parameter e.g. inA, is the local variable name
        #we will use to access this input. i.e. self.inA
        #The second paramter is the type of input.
        #The various types of inputs are defined in node.py
        #The last parameter is the label for the input in the builder.
        self.connections.append(("screenwidth", NumberOutput,"screen width"))
        self.connections.append(("screenheight", NumberOutput, "screen height"))
        

        #This is a simple description of the node that appears when double clicked.
        self.doSimplePropertyWindow("outputs the current screen width and height")

        self.initializeConnections()

    #This method is called from the player for the node to do whatever it does.
    def compute(self):

        #Nodes should define reasonable default values if they receive no input data
        self.screenwidth.value = ofGetWidth()
        self.screenheight.value = ofGetHeight()
        

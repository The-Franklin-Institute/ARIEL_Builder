#ARIEL User Node template

# This file shows you how to get started developing your own nodes.
# There are two main sections: __init__(), which initializes the node
# and declares any inputs and outputs that will be present.

#This line must be here
from arielplugin import *

#This is the class name, which the program will refer to internally.
#It can't contain spaces or dashes.
class TemplateNode(Node):

    #This is the label for the node that we will see when we're using it in the ARIEL environment.
    #This name can contain spaces and special characters.
    ARIELCLASS = "Template Node"

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        #These are the connections to our node.
        #The first parameter e.g. inA, is the local variable name
        #we will use to access this input. i.e. self.inA
        #The second paramter is the type of input.
        #The various types of inputs are defined in node.py
        #The last parameter is the label for the input in the builder.
        self.connections.append(("inA", NumberInput,"input a"))
        self.connections.append(("inB", NumberInput,"input b"))
        self.connections.append(("out", NumberOutput,"output"))

        #This is a simple description of the node that appears when double clicked.
        # self.doSimplePropertyWindow("Template Node - this node serves no function... yet.")

        self.initializeConnections()

    #This method is called from the player for the node to do whatever it does.
    def compute(self):

        #Nodes should define reasonable default values if they receive no input data
        if self.inA.value == None:
            self.inA.value = 1

        if self.inB.value == None:
            self.inB.value = 1            

        #Here we perform the actual work, i.e. multiplication
        self.out.value = self.inA.value * self.inB.value


#This shows how to get a 4x4 GL matrix from ARTK if you want to do some
#additional matrix math before drawing

#This line must be here
from arielplugin import *

import arieltypes

#needed for ofMatrix4x4
from openframeworks import *

class MatrixDemo(Node):

    #This is the label for our node in the builder"
    ARIELCLASS = "Matrix Demo"

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        #These are the connections to our node.
        #The first parameter e.g. inA, is the local variable name
        #we will use to access this input. i.e. self.inA
        #The second paramter is the type of input.
        #The various types of inputs are defined in node.py
        #The last parameter is the label for the input in the builder.
        self.connections.append(("matrix", MatrixInput,"matrix"))

        #This is a simple description of the node that appears when double clicked.
        self.doSimplePropertyWindow("this node shows how to obtain the GL matrix data from a glyph.")

        self.initializeConnections()

    #This method is called from the player for the node to do whatever it does.
    def compute(self):

        if self.matrix.value:
            artk = self.matrix.value[1]  #We pass around a handle to the artk object
            artk.applyModelMatrix(self.matrix.value[0]) #This makes artk load the model matrix for a given tag
            mat = ofMatrix4x4(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0) #Create a new matrix
            p = mat.getPtr() #Get a C pointer to its internal data structure
            glGetFloatv(GL_MODELVIEW, p) #Pass that to OpenGL, and ask for the current matrix
            print "GL MATRIX", #print out the matrix
            for n in range(4):
                print mat.get(n,0),mat.get(n,1),mat.get(n,2),mat.get(n,3)
            

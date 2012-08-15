# ARIEL User Node example: Generate scalar data to be displayed by Simulator Data.

from arielplugin import *

import arieltypes

#Multiplier is the name of our node
class ScalarTest(Node):

    #This is the label for our node in the builder"
    ARIELCLASS = "scalar test"

    def __init__(self):
        Node.__init__(self)
        self.connections = []

        self.connections.append(("out", Scalar2DOutput,"output"))

        self.initializeConnections()

    def compute(self):

        count = 0

        ourArray = arieltypes.ScalarField(10,10)
        for n in range(10):
            for m in range(10):
                ourArray[n][m] = count
                count += 1
        self.out.value = ourArray

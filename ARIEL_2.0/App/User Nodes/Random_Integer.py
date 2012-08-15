# ARIEL User Node Example: Generate a Random Integer each frame.
# Two inputs specify the range of numbers to choose from.

from arielplugin import *
import random

class RandomInteger(Node):

    #This is the label for the node that we will see when we're using it.
    #This name can contain spaces and special characters.
    ARIELCLASS = "Random #"

    def __init__(self):
        Node.__init__(self)
        self.connections = []

        self.connections.append(("randomMin", NumberInput,"minimum"))
        self.connections.append(("randomMax", NumberInput,"maximum"))
        self.connections.append(("out", NumberOutput,"output"))

        self.initializeConnections()

    def compute(self):

        if self.randomMin.value == None:
            self.randomMin.value = 0

        if self.randomMax.value == None:
            self.randomMax.value = 100            

        self.out.value = random.randint(self.randomMin.value, self.randomMax.value)

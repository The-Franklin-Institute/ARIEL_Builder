# ARIEL User Node example: Scale an input from one number range to another.

from arielplugin import *

class MathScale(Node):

    ARIELCLASS = "Math Scale"

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        self.connections.append(("userInput", NumberInput,"input"))
        self.connections.append(("oldMin", NumberInput,"old minimum"))
        self.connections.append(("oldMax", NumberInput,"old maximum"))
        self.connections.append(("newMin", NumberInput,"new minimum"))
        self.connections.append(("newMax", NumberInput,"new maximum"))

        self.connections.append(("out", NumberOutput,"output"))

        self.initializeConnections()

    def compute(self):

        if self.userInput.value == None:
            self.userInput.value = 50
        
        if self.oldMin.value == None:
            self.oldMin.value = 0

        if self.oldMax.value == None:
            self.oldMax.value = 100
            
        if self.newMin.value == None:
            self.newMin.value = 0

        if self.newMax.value == None:
            self.newMax.value = 1000

        self.out.value = ( (self.userInput.value - self.oldMin.value) / (self.oldMax.value - self.oldMin.value) ) * (self.newMax.value - self.newMin.value) + self.newMin.value

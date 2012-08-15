# ARIEL User Node example: Keep track of how many frames have passed since the sketch started.

from arielplugin import *

class FrameCount(Node):

    ARIELCLASS = "Frame Count"

    def __init__(self):
        Node.__init__(self)
        self.connections = []
        
        self.connections.append(("count", NumberOutput,"output"))

        self.initializeConnections()

    def compute(self):

        if self.count.value == None:
            self.count.value = 0

        self.count.value = self.count.value + 1

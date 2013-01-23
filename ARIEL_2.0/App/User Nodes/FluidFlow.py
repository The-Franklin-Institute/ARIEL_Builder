#ARIEL User Node
from arielplugin import *

import arieltypes
import math
import time

class FluidFlow(Node):

    #This is the label for our node in the builder"
    ARIELCLASS = "Fluid Flow"

    def __init__(self):
        Node.__init__(self)

        self.connections = []

        #These are the connections to our node.
        #The first parameter e.g. inA, is the local variable name
        #we will use to access this input. i.e. self.inA
        #The second paramter is the type of input.
        #The various types of inputs are defined in node.py
        #The last parameter is the label for the input in the builder.
        self.connections.append(("inA", NumberInput,"input x"))
        self.connections.append(("inB", NumberInput,"input y"))
        self.connections.append(("Radius", NumberInput, "input R"))
        self.connections.append(("xfunnel", NumberInput, "Funnel x"))
        self.connections.append(("yfunnel", NumberInput, "Funnel y"))
        self.connections.append(("thfunnel", NumberInput, "Funnel theta"))
        self.connections.append(("wfunnel", NumberInput, "Funnel width"))
        self.connections.append(("out", VectorListOutput,"output"))

        #This is a simple description of the node that appears when double clicked.
        self.doSimplePropertyWindow("Fluid flow around 2d Cylinder")

        self.initializeConnections()

    #This method is called from the player for the node to do whatever it does.
    def compute(self):

        #Nodes should define reasonable default values if they receive no input data
        if self.inA.value == None:
            self.inA.value = 20000
            self.Radius.value = 0.

        if self.inB.value == None:
            self.inB.value = 20000
            self.Radius.value = 0.

        if self.Radius.value == None:
            self.Radius.value = 0.

        if self.xfunnel.value == None:
            self.xfunnel.value = 0.

        if self.yfunnel.value == None:
            self.yfunnel.value = 0.

        if self.thfunnel.value == None:
            self.thfunnel.value = 0.

        if self.wfunnel.value == None:
            self.wfunnel.value = 0.

        vectors = []

        v = arieltypes.Vector()

        U = 10.0

        v.r1 = 1
        v.g1 = 1
        v.b1 = 1

        v.r2 = 1
        v.g2 = 1
        v.b2 = 1

        v.hasArrowhead = 0

        xc = self.inA.value
        yc = self.inB.value

        #line loop, five evenly spaced lines

        nlines = 5

        dx = self.wfunnel.value / nlines
        dt = 1.

        #Test to see if ball is in the stream defined by xfunnel, yfunnel, thfunnel and wfunnel
        
        width = self.wfunnel.value + 2 * self.Radius.value

        xcc = xc - self.xfunnel.value
        ycc = yc - self.yfunnel.value

        xc = xcc * math.cos(self.thfunnel.value) - ycc * math.sin(self.thfunnel.value)
        yc = xcc * math.sin(self.thfunnel.value) + ycc * math.cos(self.thfunnel.value)


        RR = 0.

        if xc > 0.:
            if (- width / 2.0) < yc < (width / 2.0):
                RR = self.Radius.value * self.Radius.value
                

        for count in range (nlines):
            
            xs = 0.0
            ys = -.5 * self.wfunnel.value + count * dx + 1.0

            x = xs - xc
            y = yc - ys
            
            for n in range (150):

                v.x1 = xs * math.cos(self.thfunnel.value) + ys * math.sin(self.thfunnel.value) + self.xfunnel.value
                v.y1 = -xs * math.sin(self.thfunnel.value) + ys * math.cos(self.thfunnel.value) + self.yfunnel.value

                v.hasArrowhead = 0

                if (n - 10) % 30 == 0:
                    v.hasArrowhead = 1

                r = math.sqrt((x*x) + (y*y))
                th = math.atan2(y, x)
                vr1 = U * (1 - RR/(r*r)) * math.cos(th)
                vth1 = -U * (1 + RR/(r*r)) * math.sin(th)
                vx1 = vr1 * math.cos(th) - vth1 * math.sin(th)
                vy1 = vr1 * math.sin(th) + vth1 * math.cos(th)

                x2 = x + .5 * vx1 * dt
                y2 = y + .5 * vy1 * dt

                r2 = math.sqrt((x2*x2) + (y2*y2))
                th2 = math.atan2(y2, x2)
                vr2 = U * (1 - RR/(r2*r2)) * math.cos(th2)
                vth2 = -U * (1 + RR/(r2*r2)) * math.sin(th2)
                vx2 = vr2 * math.cos(th2) - vth2 * math.sin(th2)
                vy2 = vr2 * math.sin(th2) + vth2 * math.cos(th2)

                x3 = x + .5 * vx2 * dt
                y3 = y + .5 * vy2 * dt

                r3 = math.sqrt((x3*x3) + (y3*y3))
                th3 = math.atan2(y3, x3)
                vr3 = U * (1 - RR/(r3*r3)) * math.cos(th3)
                vth3 = -U * (1 + RR/(r3*r3)) * math.sin(th3)
                vx3 = vr3 * math.cos(th3) - vth3 * math.sin(th3)
                vy3 = vr3 * math.sin(th3) + vth3 * math.cos(th3)

                x4 = x + .5 * vx3 * dt
                y4 = y + .5 * vy3 * dt

                r4 = math.sqrt((x4*x4) + (y4*y4))
                th4 = math.atan2(y4, x4)
                vr4 = U * (1 - RR/(r4*r4)) * math.cos(th4)
                vth4 = -U * (1 + RR/(r4*r4)) * math.sin(th4)
                vx4 = vr4 * math.cos(th4) - vth4 * math.sin(th4)
                vy4 = vr4 * math.sin(th4) + vth4 * math.cos(th4)


                xf = x + (dt/6.0) * (vx1 + 2.*vx2 + 2.*vx3 + vx4)
                yf = y + (dt/6.0) * (vy1 + 2.*vy2 + 2.*vy3 + vy4)

                xs = xc + xf
                ys = yc - yf
            
                v.x2 = xs * math.cos(self.thfunnel.value) + ys * math.sin(self.thfunnel.value) + self.xfunnel.value
                v.y2 = -xs * math.sin(self.thfunnel.value) + ys * math.cos(self.thfunnel.value) + self.yfunnel.value
    
                vectors.append(v)

                v = arieltypes.Vector()
            
                x = xf
                y = yf
                
        self.out.value = vectors

        

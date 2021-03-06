"""
ARIEL Builder is a visual language for prototyping augmented reality interactive software.
It is licensed with a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
It makes use of OpenFrameworks, distributed under the MIT License.

Direct questions, comments, and bugs to kstetz@fi.edu

The Franklin Institute
Philadelphia, Pennsylvania, USA
www.fi.edu/ariel
Lead Programmer: Kyle Stetz
 
Patten Studio
Brooklyn, New York, USA
www.pattenstudio.com
Lead Programmer: James Patten

The ARIEL project received support from the National Science Foundation under Grant No. 0741659.
Any opinions, findings, and conclusions or recommendations expressed in this material are those
of the author(s) and do not necessarily reflect the views of the National Science Foundation.
"""

from openframeworks import *

import numpy

class Vector:

    def __init__(self):
        self.r1 = 1
        self.g1 = 1
        self.b1 = 1
        self.r2 = 1
        self.g2 = 1
        self.b2 = 1

        self.x1 = 1
        self.x2 = 1

        self.y1 = 1
        self.y2 = 1

        self.hasArrowhead = 0

        self.separator = 0

def ScalarField(height, width):
    return numpy.zeros((height,width),dtype=numpy.float32)
        
class VectorOLD:

    def __init__(self, x, y, x1,y1, color=None, width=None, arrow=None, displaytype=None):
        self.x = x
        self.y = y
        self.x1 = x1
        self.y1 = y1
        self.displayType = displaytype
        self.color = color
        self.width = width
        self.arrow = arrow

    def draw(self):
        apply(glColor3f,self.color)
        glLineWidth(self.width)
        glBegin(GL_LINES)
        glVertex3f(self.x, self.y, 0)
        glVertex3f(self.x1, self.y1, 0)
        glEnd()


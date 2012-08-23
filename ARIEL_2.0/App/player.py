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

from OpenGL.GL import *
from OpenGL.GLUT import *

import os
import time
import cPickle
import sys
import string
import math
import colorsys
import wavelen2rgb
import simpleOSC
import atexit
from operator import itemgetter

from arieltypes import Vector

runfullscreen = 0

if __name__ == "__main__":

    from openframeworks import *

    from psl import util
    from psl import geom
 
    # global runfullscreen

    import os
    util.currentDir = os.getcwd()

    import myfirmata as firmata

    f = open(sys.argv[1],"r")

    #print "ARGS", sys.argv

    if "fullscreen" in sys.argv:
        runfullscreen = 1

    data = cPickle.load(f)

    nodes, connections = data

    # for n in nodes:
    #     print n

    # for c in connections:
    #     print c
    

class Node:
    
    def __init__(self):
        self.inputs = []
        self.outputs = []
        self.zIndex = 0
    
    def __lt__(self, o):
        return self.zIndex < o.zIndex
    
    def doSimplePropertyWindow(self, *args):
        pass
    
    def addInput(self, i):
        self.inputs.append(i)
    
    def addOutput(self, o):
        self.outputs.append(o)
    
    def getInputByID(self, id):
        for i in self.inputs:
            if i.id == id:
                return i
    
    def getOutputByID(self, id):
        for i in self.outputs:
            if i.id == id:
                return i
    
    def getInput(self, label):
        #print "get input for",`label`
        for i in self.inputs:
            #print "checking",`i.label`
            if i.label == label:
                #print "found!"
                return i
    
    def getOutput(self, label):
        for i in self.outputs:
            if i.label == label:
                return i
    
    def setup(self):
        pass
    
    def compute(self):
        pass
    
    def update(self):
        for o in self.outputs:
            o.update()
    
    def draw(self):
        pass
    
    def initializeConnections(self):
        for c in self.connections:
            variableName, connType, label = c
            variableName = "self."+variableName
            conn = connType(label)
            exec variableName+" = conn"
            if connType ==  NodeInput:
                #print "add connection",variableName
                self.addInput(conn)
            if connType == NodeOutput:
                #print "add connection",variableName                
                self.addOutput(conn)
    

class NodeInput:
    
    def __init__(self, label):
        self.value = None
        self.label = label
        self.id = None
    
    def set(self, val):
        self.value = val
    

class NodeOutput:
    
    def __init__(self, label=""):
        self.value = None
        self.label = label
        self.connection = None
        self.id = None
    
    def update(self):
        if self.connection:
            self.connection.set(self.value)
    

class Parameter(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.value = 0
        self.inputs.append(NodeInput("value"))
        self.outputs.append(NodeOutput("value"))
    
    def compute(self):
        if self.inputs[-1].value:
            self.value = self.inputs[-1].value
        self.outputs[-1].value = self.value
    

class Delay(Node):

    def __init__(self):
        Node.__init__(self)
        self.inputs.append(NodeInput("data"))
        self.inputs.append(NodeInput("delay"))
        self.outputs.append(NodeOutput("data"))
        self.queue = []
    
    def compute(self):
        try:
#            print "delay saves",self.inputs[0].value
#            print "delay is",self.inputs[1].value
            self.queue.append((self.inputs[0].value, time.time()))
            while len(self.queue) and self.queue[0][1] < (time.time() - self.inputs[1].value):
                self.outputs[0].value = self.queue[0][0]
                del(self.queue[0])
        except:
            pass


class Splitter(Node):

   def __init__(self):
       Node.__init__(self)
       self.inputs.append(NodeInput("data"))
       self.outputs.append(NodeOutput("data1"))
       self.outputs.append(NodeOutput("data2"))
       self.outputs.append(NodeOutput("data3"))
       self.outputs.append(NodeOutput("data4"))
   
   def compute(self):
       self.outputs[0].value = self.inputs[0].value
       self.outputs[1].value = self.inputs[0].value
       self.outputs[2].value = self.inputs[0].value
       self.outputs[3].value = self.inputs[0].value


class Startup(Node):

    def __init__(self):
        Node.__init__(self)
        self.eventOut = NodeOutput("startup event")
        self.outputs.append(self.eventOut)
        self.eventHasBeenSent = 0
    
    def compute(self):
        if not self.eventHasBeenSent:
            print "SENDING STARTUP EVENT!"
            self.eventHasBeenSent = 1
            self.eventOut.value = 1
        else:
            self.eventOut.value = 0
    

class Conditional(Node):
	
    def __init__(self):
        Node.__init__(self)

        self.value1 = NodeInput("value1")
        self.inputs.append(self.value1)
        
        self.value2 = NodeInput("value2")
        self.inputs.append(self.value2)
        
        self.value = NodeOutput("value")
        self.outputs.append(self.value)
    
    def compute(self):

        if self.value1.value == None:
            self.value1.value = 0

        if self.value2.value == None:
            self.value2.value = 0

#        print self.value1.value, self.relation, self.value2.value
        if eval(`self.value1.value` + " " + self.relation + " " + `self.value2.value`):
            self.value.value = 1
        else:
            self.value.value = 0
    

class Mathematics(Node):
    
    def __init__(self):
        Node.__init__(self)
        
        self.a = NodeInput("a")
        self.inputs.append(self.a)
        
        self.b = NodeInput("b")
        self.inputs.append(self.b)
        
        self.value = NodeOutput("value")
        self.outputs.append(self.value)
    
    def compute(self):
        if self.a.value == None:
            self.a.value = 1
        if self.b.value == None:
            self.b.value = 1
        
        self.value.value = eval(`self.a.value` + " " + self.relation + " " + `self.b.value`)
    

class Velocity(Node):
	
    def __init__(self):
        Node.__init__(self)

        self.xhistory = []
        self.yhistory = []
        
        self.xpos = NodeInput("x position")
        self.inputs.append(self.xpos)
        
        self.ypos = NodeInput("y position")
        self.inputs.append(self.ypos)
        
        self.dxdt = NodeOutput("x velocity")
        self.outputs.append(self.dxdt)

        self.dydt = NodeOutput("y velocity")
        self.outputs.append(self.dydt)

        self.px, self.py = 0, 0
    
    # def compute(self):

    #     if self.xpos.value == None:
    #         self.xpos.value = 0

    #     if self.ypos.value == None:
    #         self.ypos.value = 0

    #     self.xhistory.append((self.xpos.value, time.time()))
    #     self.yhistory.append((self.ypos.value, time.time()))

    #     while len(self.xhistory) > 50:
    #         del(self.xhistory[0])

    #     while len(self.yhistory) > 50:
    #         del(self.yhistory[0])

    #     if len(self.xhistory) > 1:
    #         self.dxdt.value = (self.xhistory[-1][0] - self.xhistory[0][0]) /  (self.xhistory[-1][1] - self.xhistory[0][1])
    #         self.dydt.value = (self.yhistory[-1][0] - self.yhistory[0][0]) /  (self.yhistory[-1][1] - self.yhistory[0][1])
    #     else:
    #         self.dxdt.value = 0
    #         self.dydt.value = 0

    def compute(self):
        if self.xpos.value == None:
            self.xpos.value = 0
        if self.ypos.value == None:
            self.ypos.value = 0

        self.dxdt.value = self.xpos.value - self.px
        self.dydt.value = self.ypos.value - self.py

        self.px, self.py = self.xpos.value, self.ypos.value
    

class GlyphFilter(Node):

    def __init__(self):
        Node.__init__(self)

        self.glyphsIn = NodeInput("glyphs")
        self.inputs.append(self.glyphsIn)
        
        # self.glyphsOut = NodeOutput("filtered glyphs")
        # self.outputs.append(self.glyphsOut)

        self.xout = NodeOutput("x")
        self.outputs.append(self.xout)

        self.yout = NodeOutput("y")
        self.outputs.append(self.yout)

        self.zout = NodeOutput("z")
        self.outputs.append(self.zout)        

        self.rout = NodeOutput("angle")
        self.outputs.append(self.rout)

        self.present = NodeOutput("present")
        self.outputs.append(self.present)

        self.matrix = NodeOutput("matrix")
        self.outputs.append(self.matrix)                        

        self.desiredId = NodeInput("id")
        self.inputs.append(self.desiredId)

        self.xout.value = 0
        self.yout.value = 0
    
    def compute(self):

        if not self.glyphsIn.value:
            return
#        print "glyphs",self.glyphsIn.value
        self.present.value = 0
        artk = self.glyphsIn.value[1]
        # self.glyphsOut.value = [[],self.glyphsIn.value[1]]
        for idnum in self.glyphsIn.value[0]:
            if idnum == self.desiredId.value:

                i = artk.getMarkerIndex(idnum)
                if i < 0:
                    continue
                
                # self.glyphsOut.value[0].append(i)
                v = artk.getDetectedMarkerCenter(i)
                self.xout.value = v.x # * self.glyphsIn.value[2]
                self.yout.value = v.y # * self.glyphsIn.value[2]
                v = artk.getTranslation(i)
                self.zout.value = v.z
                self.rout.value = artk.get2Drotation(i)
                self.present.value = 1
                self.matrix.value = (i,artk)
                # print "set matrix",self.matrix.value
    

class Camera(Node):
    
    def __init__(self):
        
        self.autoAlign = 1
        self.mirrorImage = 0
        Node.__init__(self)
        self.vidGrabber = ofVideoGrabber()
        self.grayImage = ofxCvGrayscaleImage()
        self.grayBg = ofxCvGrayscaleImage()
        self.grayDiff = ofxCvGrayscaleImage()
        self.colorImg = ofxCvColorImage()
        self.artk = ofxARToolkitPlus()
        self.blobFinder = ofxCvContourFinder()
        self.fiducials = []
        
#	print dir(self.fidfinder)
	    
        self.bLearnBakground = 0
        self.backgroundSubOn = 0
        
        self.bsub = NodeInput("trigger: subtract background")
        self.inputs.append(self.bsub)
        
        self.threshold = NodeInput("threshold")
        self.inputs.append(self.threshold)
        
        self.minblob = NodeInput("min blob size")
        self.inputs.append(self.minblob)
        
        self.maxblob = NodeInput("max blob size")
        self.inputs.append(self.maxblob)        
        
        self.glyphsOut = NodeOutput("glyphs")
        self.blobsOut = NodeOutput("blobs")
        self.imageOut = NodeOutput("image")
        self.blobGeomOut = NodeOutput("blob geometry")
        self.outputs = [self.glyphsOut, self.blobsOut, self.imageOut, self.blobGeomOut]
    
    def setup(self):
    	self.vidGrabber.setVerbose(True)
        print "CAMERA INDEX", self.indexvalue
        self.vidGrabber.setDeviceID(int(self.indexvalue))
    	self.vidGrabber.initGrabber(640,480)
    	self.colorImg.allocate(640,480)
    	self.grayImage.allocate(640,480)
    	self.grayBg.allocate(640,480)
    	self.grayDiff.allocate(640,480)
        
        print "about to setup artk"
        ofSetDataPathRoot(util.currentDir+"/")
        
        self.autoScale = max(ofGetWidth() / self.vidGrabber.getWidth(), ofGetHeight() / self.vidGrabber.getHeight())
        
        screenAspect = ofGetWidth()/float(ofGetHeight())
        
        self.artkX = 640
        self.artkY = 480
        
        if screenAspect > 1.334:
            self.artkY = int(self.artkX / screenAspect)
        
        if screenAspect < 1.332:
            self.artkX = int(self.artkY * screenAspect)
        
        
        self.artkROI = ofRectangle((640 - self.artkX)/2,(480 - self.artkY) / 2, self.artkX, self.artkY)
#        self.artkROI = ofRectangle(0,0,480,480)
        
        print "ROI",(640 - self.artkX)/2,(480 - self.artkY) / 2, self.artkX, self.artkY
        self.artk.setup(self.artkX, self.artkY)
        print "artk setup done",self.artkX, self.artkY
        
        self.imageOut.value = [self.colorImg, False] #False == is the image new
	    
        self.artk.setThreshold(85)
    	self.bLearnBakground = False
    	self.backgroundSubOn = False
    
    def compute(self):
        
        print "bsub:", self.bsub.value
        
        if self.bsub.value:
            print "learning background for subtraction"
            self.bLearnBakground = True
            self.bsub.value = 0
        
        if self.minblob.value == None:
            self.minblob.value = 0.01
        
        if self.maxblob.value == None:
            self.maxblob.value = 0.33
        
        if self.threshold.value == None:
            self.threshold.value = 85
        self.artk.setThreshold(int(self.threshold.value))
        
    	self.vidGrabber.grabFrame()
        self.imageOut.value = [self.colorImg, False]
        if self.vidGrabber.isFrameNew():
            self.colorImg.setFromPixels(self.vidGrabber.getPixels(), 640,480)
            
#            print "mirror",self.mirrorImage
            
            if self.mirrorImage:
                self.colorImg.mirror(0,1)
            
            
            self.imageOut.value = [self.colorImg, True] #True == is the image new
            self.grayImage.assign(self.colorImg)
		    
            if (self.bLearnBakground == True):
                self.grayBg.assign(self.grayImage)	
                self.bLearnBakground = False
                self.backgroundSubOn = True
		    
            #take the abs value of the difference between background and incoming and then threshold:
            if (self.backgroundSubOn):
                print "sub on"
                self.grayDiff.absDiff( self.grayBg, self.grayImage )
            else:
                self.grayDiff.assign(self.grayImage)
#            self.imageOut.value = [self.grayDiff, True]
            self.grayImage.setROI(self.artkROI)
            self.artk.update(self.grayImage.getRoiPixels())
            self.grayImage.resetROI()
            self.grayDiff.threshold(int(self.threshold.value))
#            self.fidfinder.findFiducials( self.grayDiff )
            self.blobFinder.findContours(self.grayDiff, int(640*480*self.minblob.value), int(640*480*self.maxblob.value),5,0)
#            print "found blobs:",self.blobFinder.nBlobs
            blobs = []
            blobGeom = []
            for n in range(self.blobFinder.nBlobs):
                b = self.blobFinder.getBlob(n)
                g = []
                for n in range(b.nPts):
                    p = b.getPoint(n)
                    x,y = p.x, p.y
                    if self.autoAlign:
                        x *= self.autoScale
                        y *= self.autoScale         
                    g.append((x,y))
                blobGeom.append(g)
                x = b.centroid.x
                y = b.centroid.y
                w = b.boundingRect.width
                h = b.boundingRect.height
                if self.autoAlign:
                    x *= self.autoScale
                    y *= self.autoScale
                    w *= self.autoScale
                    h *= self.autoScale                    
                blobs.append((x,y,w,h))
            self.blobsOut.value = blobs
            self.fiducials = [[], self.artk, self.autoScale]
            count = self.artk.getNumDetectedMarkers()
            for i in range(count):
                self.fiducials[0].append(self.artk.getMarkerID(i))
            
#            print "tags",self.fiducials
            self.glyphsOut.value = self.fiducials[:]
            self.blobGeomOut.value = (blobGeom, self.autoScale)
    

class SimpleCamera(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.mirrorImage = 0
        self.vidGrabber = ofVideoGrabber()
        self.colorImg = ofxCvColorImage()
        self.imageOut = NodeOutput("image")
        self.outputs = [self.imageOut]
    
    def setup(self):
        self.vidGrabber.setVerbose(True)
        self.vidGrabber.setDeviceID(int(self.indexvalue))
        self.vidGrabber.initGrabber(640,480)
    	self.colorImg.allocate(640,480)
    	self.imageOut.value = [self.colorImg, False] #False == is the image new
    
    def compute(self):
        self.vidGrabber.grabFrame()
    	if self.vidGrabber.isFrameNew():
            self.colorImg.setFromPixels(self.vidGrabber.getPixels(), 640,480)
            if self.mirrorImage:
                self.colorImg.mirror(0,1)
            self.imageOut.value = [self.colorImg, True] #True == is the image new
        else:
            self.imageOut.value = [self.colorImg, False]
    

class BlobTracking(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.imageData = NodeInput("image data")
        self.inputs.append(self.imageData)
        self.minblob = NodeInput("min blob size")
        self.inputs.append(self.minblob)
        self.maxblob = NodeInput("max blob size")
        self.inputs.append(self.maxblob)
        self.thresholdIn = NodeInput("threshold")
        self.inputs.append(self.thresholdIn)
        #
        self.blobsOut = NodeOutput("blobs")
        self.blobGeomOut = NodeOutput("blob geometry")
        self.trackedImage = NodeOutput("image")
        self.videoSync = NodeOutput("video sync")
        self.outputs = [self.blobsOut, self.blobGeomOut, self.trackedImage, self.videoSync]
        #-------------
        self.colorImg = ofxCvColorImage()
        self.grayImg = ofxCvGrayscaleImage()
        self.blobFinder = ofxCvContourFinder()
    
    def setup(self):
        self.colorImg.allocate(640,480)
        self.grayImg.allocate(640, 480)
        self.trackedImage.value = [self.grayImg, False]
        self.videoSync.value = 0
        
    
    def compute(self):
        if self.minblob.value == None:
            self.minblob.value = 0.001
        
        if self.maxblob.value == None:
            self.maxblob.value = 0.33

        if self.thresholdIn.value == None:
            self.thresholdIn.value = 85

        # video sync sends out a 1 whenever there is a new frame;
        # when used with data collector (in a blob tracking program),
        # it prevents duplicate points from being created
        # in between new video frames
        self.videoSync.value = 0
        
        if self.imageData.value and self.imageData.value[1] == True:
            self.colorImg = self.imageData.value[0]
            self.grayImg.assign(self.colorImg)
            self.grayImg.threshold(int(self.thresholdIn.value))
            self.trackedImage.value = [self.grayImg, True]
            self.videoSync.value = 1
            
            self.blobFinder.findContours(self.grayImg, int(640*480*self.minblob.value), int(640*480*self.maxblob.value),5,0)
            blobs = []
            blobGeom = []
            for n in range(self.blobFinder.nBlobs):
                b = self.blobFinder.getBlob(n)
                g = []
                for n in range(b.nPts):
                    p = b.getPoint(n)
                    x,y = p.x, p.y
                    g.append((x,y))
                blobGeom.append(g)
                x = b.centroid.x
                y = b.centroid.y
                w = b.boundingRect.width
                h = b.boundingRect.height
                blobs.append((x,y,w,h))
            self.blobsOut.value = blobs
            self.blobGeomOut.value = (blobGeom, False)
            #print "blob out:",blobs
        else:
            # image is new True/False protocol!
            self.trackedImage.value = [self.grayImg, False]


class BlobFilter(Node):
    def __init__(self):
        Node.__init__(self)
        self.blobs = NodeInput("blobs")
        self.inputId = NodeInput("id")
        self.inputs = [self.blobs, self.inputId]

        self.xPos = NodeOutput("x")
        self.yPos = NodeOutput("y")
        self.bWidth = NodeOutput("width")
        self.bHeight = NodeOutput("height")
        self.outputs = [self.xPos, self.yPos, self.bWidth, self.bHeight]

    def setup(self):
        pass

    def compute(self):
        if self.inputId.value == None:
            self.inputId.value = 0
        
        if self.blobs.value != None:
            #create a new blob list
            newBlobList = []
            for b in self.blobs.value:
                #add a 5th field for w*h of blob (for sorting by size)
                b = (b[0], b[1], b[2], b[3], b[2]*b[3])
                newBlobList.append(b)
            #sort the blob by the field we just added
            sorted(newBlobList, key=itemgetter(4))
            #if the blob in question actually exists, output it
            try:
                theBlob = newBlobList[self.inputId.value]
                self.xPos.value = theBlob[0]
                self.yPos.value = theBlob[1]
                self.bWidth.value = theBlob[2]
                self.bHeight.value = theBlob[3]
            except IndexError:
                pass


class GlyphTracking(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.imageData = NodeInput("image data")
        self.glyphsOut = NodeOutput("glyphs")
        self.outputs = [self.glyphsOut]
        self.inputs.append(self.imageData)
        self.artk = ofxARToolkitPlus()
        self.colorImg = ofxCvColorImage()
        self.grayImg = ofxCvGrayscaleImage()
        self.fiducials = []
    
    def setup(self):
        self.colorImg.allocate(640,480)
        self.grayImg.allocate(640, 480)
        #
        print "about to setup artk"
        ofSetDataPathRoot(util.currentDir+"/")
        screenAspect = ofGetWidth()/float(ofGetHeight())
        self.artkX = 640
        self.artkY = 480
        if screenAspect > 1.334:
            self.artkY = int(self.artkX / screenAspect)
        if screenAspect < 1.332:
            self.artkX = int(self.artkY * screenAspect)
        self.artkROI = ofRectangle((640 - self.artkX)/2,(480 - self.artkY) / 2, self.artkX, self.artkY)
        self.artk.setup(self.artkX, self.artkY)
        self.artk.setThreshold(85)
        #
        self.autoScale = max(ofGetWidth() / self.colorImg.getWidth(), ofGetHeight() / self.colorImg.getHeight())
    
    def compute(self):
        if self.imageData.value and self.imageData.value[1] == True:
            self.colorImg = self.imageData.value[0]
            self.grayImg.assign(self.colorImg)
            
            self.grayImg.setROI(self.artkROI)
            self.artk.update(self.grayImg.getRoiPixels())
            self.grayImg.resetROI()
            
            self.fiducials = [[], self.artk, self.autoScale]
            count = self.artk.getNumDetectedMarkers()
            for i in range(count):
                self.fiducials[0].append(self.artk.getMarkerID(i))
            self.glyphsOut.value = self.fiducials[:]
    
    # def draw(self):
    #     self.artk.draw(0,0)


class BackgroundDifferencing(Node):

    def __init__(self):
        Node.__init__(self)
        self.imageData = NodeInput("image data")
        self.inputs.append(self.imageData)
        self.triggerEvent = NodeInput("trigger")
        self.inputs.append(self.triggerEvent)
        #
        self.imageOut = NodeOutput("image")
        self.outputs = [self.imageOut]
        #
        self.inputGrayImg = ofxCvGrayscaleImage()
        self.backgroundImg = ofxCvGrayscaleImage()
        self.bgDiff = ofxCvGrayscaleImage()

    def setup(self):
        self.inputGrayImg.allocate(640, 480)
        self.backgroundImg.allocate(640, 480)
        self.bgDiff.allocate(640, 480)

        self.imageOut.value = [self.bgDiff, False]

    def compute(self):
        # if there's a new image
        if self.imageData.value and self.imageData.value[1] == True:
            # grab the image (converting it to grayscale if it wasn't already)
            self.inputGrayImg.assign(self.imageData.value[0])
            # if the trigger input gets an event
            if self.triggerEvent.value:
                # save the background, to be subtracted from
                self.backgroundImg.assign(self.inputGrayImg)
            # actual subtraction
            self.bgDiff.absDiff(self.backgroundImg, self.inputGrayImg)
            self.imageOut.value = [self.bgDiff, True]
        else:
            # following the new image True/False protocol
            self.imageOut.value = [self.bgDiff, False]


class Kinect(Node):

    def __init__(self):
        self.autoAlign = 1
        self.mirrorImage = 0
        Node.__init__(self)
        self.vidGrabber = ofxKinect()
        self.grayImage = ofxCvGrayscaleImage()
        self.grayBg = ofxCvGrayscaleImage()
        self.grayDiff = ofxCvGrayscaleImage()
        self.colorImg = ofxCvColorImage()
	    
        self.artk = ofxARToolkitPlus()
        
        self.blobFinder = ofxCvContourFinder()
        
        self.fiducials = []

        self.bLearnBakground = 0
        self.backgroundSubOn = 0
        
        self.bsub = NodeInput("trigger: subtract background")
        self.inputs.append(self.bsub)
        
        self.threshold = NodeInput("threshold")
        self.inputs.append(self.threshold)
        
        self.minblob = NodeInput("min blob size")
        self.inputs.append(self.minblob)
        
        self.maxblob = NodeInput("max blob size")
        self.inputs.append(self.maxblob)    
        
        self.glyphsOut = NodeOutput("glyphs")
        self.blobsOut = NodeOutput("blobs")
        self.imageOut = NodeOutput("image")
        self.blobGeomOut = NodeOutput("blob geometry")
        self.outputs = [self.glyphsOut, self.blobsOut, self.imageOut, self.blobGeomOut]

        atexit.register(self.closeKinect)
    
    def setup(self):
        self.vidGrabber.init(False, True)
    	self.vidGrabber.setVerbose(True)
        self.vidGrabber.open()
        self.vidGrabber.setCameraTiltAngle(0)
        print "CAMERA INDEX", self.indexvalue
    	self.colorImg.allocate(640,480)
        self.grayImage.allocate(640,480)
        self.grayBg.allocate(640,480)
        self.grayDiff.allocate(640,480)
        
        print "about to setup artk"
        ofSetDataPathRoot(util.currentDir+"/")
        self.artk.setup(640, 480)
        print "artk setup done"
        
        self.imageOut.value = [self.colorImg, False] #False == is the image new
        
        self.artk.setThreshold(85)
        self.bLearnBakground = False
        self.backgroundSubOn = False
        
        self.autoScale = max(ofGetWidth() / self.vidGrabber.getWidth(), ofGetHeight() / self.vidGrabber.getHeight())
    
    def compute(self):
        
        if self.bsub.value == 1:
            print "learning background for subtraction"
            self.bLearnBakground = True
            self.bsub.value = 0
        
        if self.threshold.value == None:
            self.threshold.value = 85
        self.artk.setThreshold(int(self.threshold.value))
        
        if self.minblob.value == None:
            self.minblob.value = 0.01
        
        if self.maxblob.value == None:
            self.maxblob.value = 0.33
        
        
        self.vidGrabber.update()
        
        if self.vidGrabber.isFrameNew():
            self.grayImage.setFromPixels(self.vidGrabber.getDepthPixels(), 640,480)
            print self.vidGrabber.getDistanceAt(20, 20)
            
            if self.mirrorImage:
                self.grayImage.mirror(1,1)
            
            
            self.colorImg.assign(self.grayImage)
            
            self.imageOut.value = [self.colorImg, True] #True == is the image new
            
            if (self.bLearnBakground == True):
                self.grayBg.assign(self.grayImage)	
                self.bLearnBakground = False
                self.backgroundSubOn = True
            
            #take the abs value of the difference between background and incoming and then threshold:
            if (self.backgroundSubOn):
                print "sub on"
                self.grayDiff.absDiff( self.grayBg, self.grayImage )
            else:
                self.grayDiff.assign(self.grayImage)
            self.artk.update(self.grayImage.getPixels())
            self.grayDiff.threshold(int(self.threshold.value))
            self.blobFinder.findContours(self.grayDiff, int(640*480*self.minblob.value), int(640*480*self.maxblob.value),5,0)
            
            print "found blobs:",self.blobFinder.nBlobs
            blobs = []
            blobGeom = []
            for n in range(self.blobFinder.nBlobs):
                b = self.blobFinder.getBlob(n)
                g = []
                for n in range(b.nPts):
                    p = b.getPoint(n)
                    x,y = p.x, p.y
                    if self.autoAlign:
                        x *= self.autoScale
                        y *= self.autoScale         
                    g.append((x,y))
                blobGeom.append(g)
                x = b.centroid.x
                y = b.centroid.y
                w = b.boundingRect.width
                h = b.boundingRect.height
                if self.autoAlign:
                    x *= self.autoScale
                    y *= self.autoScale
                    w *= self.autoScale
                    h *= self.autoScale                    
                blobs.append((x,y,w,h))
            self.blobsOut.value = blobs
            self.fiducials = [[], self.artk, self.autoScale]
            count = self.artk.getNumDetectedMarkers()
            for i in range(count):
                self.fiducials[0].append(self.artk.getMarkerID(i))
            
            #print "tags",self.fiducials
            self.glyphsOut.value = self.fiducials[:]
            self.blobGeomOut.value = blobGeom   

    def closeKinect(self):
        self.vidGrabber.close()
        print "closed kinect before exit"


class SimpleKinect(Node):

    def __init__(self):
        Node.__init__(self)
        self.autoAlign = 1
        self.mirrorImage = 0
        self.vidGrabber = ofxKinect()
        self.colorImg = ofxCvGrayscaleImage()
        self.realColorImg = ofxCvColorImage()
        self.imageOut = NodeOutput("image")
        self.outputs = [self.imageOut]
        # atexit is a python module that allows us to run functions before a script
        # exits, assuming it hasn't crashed.
        atexit.register(self.closeKinect)
        self.mode = 2

    def setup(self):
        # to initialize: init(RGB image bool, IR image bool)

        if self.mode == 0: # RGB
            self.vidGrabber.init()
        elif self.mode == 1: # IR
            self.vidGrabber.init(True, False)
        else: # DEPTH
            self.vidGrabber.init(False, False)

        self.vidGrabber.setVerbose(True)
        self.vidGrabber.open()
        self.colorImg.allocate(640,480)
        self.realColorImg.allocate(640, 480)
        self.imageOut.value = [self.colorImg, False]
    
    def compute(self):
        self.vidGrabber.update()

        if self.vidGrabber.isFrameNew():
            # we use getDepthPixels if the Depth option has been specified.
            if self.mode == 2:
                self.colorImg.setFromPixels(self.vidGrabber.getDepthPixels(), 640, 480)
            # otherwise, getPixels will depend on the RGB and IR boolean values we initialized in setup()
            elif self.mode == 0:
                self.realColorImg.setFromPixels(self.vidGrabber.getPixels(), 640, 480)
                # self.colorImg.setFromPixels(self.vidGrabber.getDistancePixels(), 640, 480)
            else:
                self.colorImg.setFromPixels(self.vidGrabber.getPixels(), 640, 480)

            if self.mirrorImage:
                self.colorImg.mirror(0,1)

            if self.mode == 0:
                self.imageOut.value = [self.realColorImg, True]
            else:
                self.imageOut.value = [self.colorImg, True]

    def closeKinect(self):
        self.vidGrabber.close()

class ColladaAnimation(Node):

    def __init__(self):
        
        
        Node.__init__(self)
        self.filename = ""
        self.x = NodeInput("x position")  
        self.inputs.append(self.x)
        
        self.y = NodeInput("y position")  
        self.inputs.append(self.y)
        
        self.z = NodeInput("z position")  
        self.inputs.append(self.z)
        
        # self.drawingOrder = NodeInput("drawing order")
        # self.inputs.append(self.drawingOrder)
        
        self.r = NodeInput("rotation")
        self.inputs.append(self.r)
        
        self.s = NodeInput("scale")
        self.inputs.append(self.s)
        
        self.matrix = NodeInput("matrix")
        self.inputs.append(self.matrix)        
        
        self.drawFlag = NodeInput("to draw or not to draw")
        self.inputs.append(self.drawFlag)
        
        self.startFlag = NodeInput("start animation")
        self.inputs.append(self.startFlag)        
    
    def setup(self):
        ofDisableArbTex()
        self.model = ofxAssimpModelLoader()
        if(self.model.loadModel(self.filename,1)):
            print "loaded",self.filename
            self.model.setAnimation(0)
            self.model.setPosition(0, 0 , 0)
            
            self.normScale = self.model.getNormalizedScale()
            self.scale = self.model.getScale()
            # print self.scale,"SCALE"
            self.sceneCenter = self.model.getSceneCenter()
            self.material = self.model.getMaterialForMesh(0)
            self.tex = self.model.getTextureForMesh(0)
            self.mesh = self.model.getMesh(0)
            print self.mesh, dir(self.mesh)
            self.position = self.model.getPosition()
            
        else:
            print "FAILED TO LOAD",self.filename
        
        self.x.value = 0
        self.y.value = 0
        self.z.value = 0
        self.s.value = 1.0
        self.drawFlag.value = 1
        # self.drawingOrder.value = 10
        
        self.bAnimate		= 0
    	self.bAnimateMouse 	= 1
        self.animationTime	= 0.0
        #ofEnableArbTex()
        
        print "DEPTH",glIsEnabled(GL_DEPTH_TEST)
        ofDisableArbTex()
        ofEnableBlendMode(OF_BLENDMODE_ALPHA)
        
        
        #//some model / light stuff
        glShadeModel(GL_SMOOTH)
        #print self.x.value,self.y.value, self.z.value                
    
    def compute(self):
        pass
    
    def drawtest(self):
        ofPushMatrix()
        
        glTranslatef(400,400,0)
        ofEnableAlphaBlending()
        glRotatef(-80,1,0,0)

        self.model.drawFaces()
        
        ofPopMatrix()
    
    def draw(self):
        if not self.drawFlag.value:
            #print "NO DRAW"
            return
        
        if self.x.value == None:
            self.x.value = 0
        if self.y.value == None:
            self.y.value = 0
        if self.z.value == None:
            self.z.value = 0
        if self.s.value == None:
            self.s.value = 1
        if self.r.value == None:
            self.r.value = 0
        
        #if self.matrix.value:
        #print "matrix",self.matrix.value
        self.model.setScale(self.s.value, self.s.value, self.s.value)
        
        if self.startFlag.value:
            self.bAnimate = 1
        
        if( self.bAnimate ):
            self.animationTime += ofGetLastFrameTime()
            if( self.animationTime >= 1.0 ):
                self.animationTime = 0.0
            self.model.setNormalizedTime(self.animationTime)
        
    	if( self.bAnimateMouse ):
    	    self.model.setNormalizedTime(self.animationTime)

            self.zIndex = 10
            glEnable(GL_DEPTH_TEST)

            if self.matrix.value:
                glViewport(0,0,ofGetWidth(),ofGetHeight())
                # glViewport(0,0,640,480)
                artk = self.matrix.value[1]
                glMatrixMode(GL_PROJECTION)
                glPushMatrix()
                artk.applyProjectionMatrix(ofGetWidth(), ofGetHeight())
                # artk.applyProjectionMatrix(640, 480)
                glMatrixMode( GL_MODELVIEW )
                glPushMatrix()
                glLoadIdentity()
                artk.applyModelMatrix(self.matrix.value[0])

                glRotatef(-90, 1, 0, 0)
                self.model.drawFaces()
                glPopMatrix()
                glMatrixMode(GL_PROJECTION)
                glPopMatrix()
                glMatrixMode( GL_MODELVIEW )
            else:

                ofPushMatrix()
                glTranslatef(self.x.value,self.y.value, self.z.value)
                glScalef(self.s.value, self.s.value, 1)
                glRotatef(self.r.value, 0, 0, 1)
                self.model.drawFaces()
                ofPopMatrix()

            glDisable(GL_DEPTH_TEST)
            #ofEnableArbTex()
    

class Image(Node):

    def __init__(self):
        
        self.autoAlign = 0
        self.alignment = None
        self.anchor = 0
        
        Node.__init__(self)
        
        self.filename = ""
        self.imageIndex = NodeInput("index")
        self.inputs.append(self.imageIndex)
        
        self.x = NodeInput("x position")
        self.inputs.append(self.x)
        
        # self.drawingOrder = NodeInput("drawing order")
        # self.inputs.append(self.drawingOrder)
        
        self.y = NodeInput("y position")
        self.inputs.append(self.y)
        
        self.z = NodeInput("z position")
        self.inputs.append(self.z)
        
        self.r = NodeInput("rotation")
        self.inputs.append(self.r)
        
        self.s = NodeInput("scale")
        self.inputs.append(self.s)
        
        self.matrix = NodeInput("matrix")
        self.inputs.append(self.matrix)        
        
        self.imageData = NodeInput("image data")
        self.inputs.append(self.imageData)        
        
        self.t = NodeInput("transparency")
        self.inputs.append(self.t)

        self.mask = NodeInput("mask")
        self.inputs.append(self.mask)
        
        # IMAGE SIZE OUTPUT, added 2/29/12
        self.widthOut = NodeOutput("image width")
        self.outputs.append(self.widthOut)
        self.heightOut = NodeOutput("image height")
        self.outputs.append(self.heightOut)

        self.drawFlag = NodeInput("to draw or not to draw")
        self.inputs.append(self.drawFlag)
        self.imageList = []
        self.currentIndex = 0
    
    def setup(self):
        self.image = ofImage()
        if self.image.loadImage(self.filename):

            self.imageList = [self.filename]

        else:
            #maybe it is a list of images?
            try:
                f = open(self.filename)
                lines = f.readlines()
                for l in lines:
                    self.imageList.append(l[:-1])
                self.changeImage()
            except:
                pass
            
        self.x.value = 0
        self.y.value = 0
        self.z.value = 0
        # self.drawingOrder.value = 10
        self.s.value = 1.0
        self.drawFlag.value = 1

        self.colorCameraImg = []

        for n in range(5):
            self.colorCameraImg.append(ofxCvColorImage())
            self.colorCameraImg[n].allocate(640,480)
    
    def changeImage(self):
        if not self.image.loadImage(self.imageList[self.currentIndex]):
            from psl import gui
            gui.doPopupMessage("Failed to load image",self.imageList[self.currentIndex])
    
    def compute(self):
        if self.imageData.value and self.imageData.value[1] == True:
            for n in range(5):
                self.colorCameraImg[n].assign(self.imageData.value[0])
            self.image = self.colorCameraImg[0]

        if self.mask.value != None:
             for n in range(len(self.mask.value[0])):
                t = self.colorCameraImg[n].getTextureReference()
                t.useMask = 1
                t.clearMask()

                fac = self.image.getWidth()/float(self.mask.value[1])/640.0
                
                for p in self.mask.value[0][n]:
                    t.addPointToMask(ofVec3f(p[0]*fac,p[1]*fac))
        else:
            pass #self.image.getTextureReference().useMask = 0

        # self.image.draw(0, 0)
        # p = []
        # p = glReadPixelsf(0, 0, 640, 480, GL_RGB)
        # print p[0]
        # sys.exit()

        if self.imageIndex.value != None:
            if self.imageIndex.value > (len(self.imageList) - 1):
                self.imageIndex.value = len(self.imageList) - 1
            self.imageIndex.value = int(self.imageIndex.value)
            if self.imageIndex.value != self.currentIndex:
                self.currentIndex = self.imageIndex.value
                self.changeImage()
        
        if self.autoAlign and self.alignment == None and self.image.getWidth() > 0:
            scale = max(ofGetWidth() / self.image.getWidth(), ofGetHeight() / self.image.getHeight())
            # print "scale!",scale
            autoX = ofGetWidth()/2
            autoY = ofGetHeight()/2

            self.alignment = (scale, autoX, autoY)

            self.s.value = scale
            self.x.value = autoX
            self.y.value = autoY
        if self.s.value:
            self.widthOut.value = self.image.getWidth() * self.s.value
            self.heightOut.value = self.image.getHeight() * self.s.value
    
    
    def draw(self):
        #print self.x.value,self.y.value, self.z.value

        if not self.drawFlag.value:
            #print "NO DRAW"
            return
        
        if self.x.value == None:
            self.x.value = 0
        if self.y.value == None:
            self.y.value = 0
        if self.z.value == None:
            self.z.value = 0
        if self.s.value == None:
            self.s.value = 1
        if self.t.value == None:
            self.t.value = 1
        if self.r.value == None:
            self.r.value = 0

        # self.zIndex = self.drawingOrder.value
        self.zIndex = 0

        if self.matrix.value:
            glViewport(0,0,ofGetWidth(),ofGetHeight())
            artk = self.matrix.value[1]
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            artk.applyProjectionMatrix(ofGetWidth(), ofGetHeight())
            glMatrixMode( GL_MODELVIEW )
            glPushMatrix()
            glLoadIdentity()
            artk.applyModelMatrix(self.matrix.value[0])
            glScalef(self.s.value, self.s.value, 1)
            # self.image.mirror(0, 1)
            #DRAW here

            if self.t.value != 1:
                glColor4f(1,1,1, self.t.value)
            else:
                glColor3f(1,1,1)
            ofEnableAlphaBlending()
            if self.mask.value == None:
                if self.anchor == 0:
                    self.image.draw(0, 0, self.image.getWidth(), -self.image.getHeight())
                else:
                    self.image.draw(-self.image.getWidth()*0.5, self.image.getHeight()*0.5, self.image.getWidth(), -self.image.getHeight())
            else:
                for n in range(len(self.mask.value[0])):
                    self.colorCameraImg[n].draw(self.image.getWidth() * -0.5, self.image.getHeight() * -0.5)
            ofDisableAlphaBlending()

            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode( GL_MODELVIEW )
        else:

            glPushMatrix()
            if self.anchor == 0:
                glTranslatef(self.x.value,self.y.value, self.z.value)
            else:
                glTranslatef(self.x.value, self.y.value, self.z.value)
            glScalef(self.s.value, self.s.value, 1)
            glRotatef(self.r.value, 0, 0, 1)
            #glTranslatef(self.image.getWidth() * 0.5, self.image.getHeight() * 0.5, 0)
            if self.t.value != 1:
                glColor4f(1,1,1, self.t.value)
            else:
                glColor3f(1,1,1)
            ofEnableAlphaBlending()
            if self.mask.value == None:
                if self.anchor == 0:
                    self.image.draw(0, 0)
                else:
                    self.image.draw(self.image.getWidth() * -0.5, self.image.getHeight() * -0.5)
            else:
                for n in range(len(self.mask.value[0])):
                    self.colorCameraImg[n].draw(self.image.getWidth() * -0.5, self.image.getHeight() * -0.5)
            ofDisableAlphaBlending()

            glPopMatrix()
    

class Video(Image):
    def __init__(self):
        Image.__init__(self)
#        del(self.inputs[-4]) #image data
        
        self.rate = NodeInput("playback rate")
        self.inputs.append(self.rate)

        self.lastRate = 1
        self.lastIndex = 0
    
    def setup(self):

        class VideoHack(ofVideoPlayer):
            def __init__(self):
                ofVideoPlayer.__init__(self)

        print "load 1"
        self.image = VideoHack()
        print "load 2"
        self.image.loadMoviePlease(self.filename)
        print "load 3"
        self.image.play()
        print "DIR",dir(self.image)
        print "load 4"
        self.x.value = 0
        self.y.value = 0
        self.z.value = 0
        self.s.value = 1.0
        self.drawFlag.value = 1.0
        # self.drawingOrder.value = 10
    
    def compute(self):
        self.image.update()

        if self.mask.value != None:
            best = 0
            bestIndex = None
            for p in range(len(self.mask.value)):
                if len(self.mask.value[p]) > best:
                    best = self.mask.value[p]
                    bestIndex = p
            if bestIndex != None:
                t = self.image.getTextureReference()
                t.useMask = 1
                t.clearMask()
                for p in self.mask.value[bestIndex]:
                    t.addPointToMask(ofVec3f(p[0],p[1]))
            else:
                pass #self.image.getTextureReference().useMask = 0
        else:
            pass #self.image.getTextureReference().useMask = 0

        if self.rate.value != None and self.rate.value != self.lastRate:
            self.lastRate = self.rate.value
            self.image.setSpeed(self.lastRate)

        if self.imageIndex.value != None and self.imageIndex.value != self.lastIndex:
            self.lastIndex = self.imageIndex.value
            self.image.setPosition(self.lastIndex)
    

class Firmata(Node):

    def __init__(self):
        Node.__init__(self)
        
        files = os.listdir("/dev")
        files = filter(lambda f: "tty.usbmodem" in f, files)
        print "firmata candidates:",files
        print "choosing",files[0]
        
        self.portname = "/dev/" + files[0] #"/dev/tty.usbmodemfd3121"
        
        self.digital2out = NodeOutput("switch pin")
        self.outputs.append(self.digital2out)
        self.digital3out = NodeOutput("button pin one")
        self.outputs.append(self.digital3out)
        self.digital4out = NodeOutput("button pin two")
        self.outputs.append(self.digital4out)

        self.analog1out = NodeOutput("dial pin one")
        self.outputs.append(self.analog1out)
        self.analog2out = NodeOutput("dial pin two")
        self.outputs.append(self.analog2out)
        self.analog3out = NodeOutput("dial pin three")
        self.outputs.append(self.analog3out)
    
    def setup(self):
        self.firmata = firmata.Arduino(self.portname, 57600)
        self.firmata.pin_mode(2, firmata.INPUT)
        self.firmata.pin_mode(3, firmata.INPUT)
        self.firmata.pin_mode(4, firmata.INPUT)
        self.firmata.digital_write(2,1)
        self.firmata.digital_write(3,1)
        self.firmata.digital_write(4,1)
    
    def computeR(self, vo, r2=40, vin=1024.0):
        if vo == 0:
            vo = 1
        return r2 * vin / vo - r2
    
    def compute(self):
        self.firmata.poll()
        self.digital2out.value = self.firmata.digital_read(2)
        self.digital3out.value = self.firmata.digital_read(3)
        self.digital4out.value = self.firmata.digital_read(4)

        #self.analog1out.value = 300 - self.computeR(self.firmata.analog_read(1)) / 25.0 * 300
        self.analog1out.value = self.firmata.analog_read(1)
        #self.analog2out.value = 300 - self.computeR(self.firmata.analog_read(2)) / 25.0 * 300
        self.analog2out.value = self.firmata.analog_read(2)
        #self.analog3out.value = 300 - self.computeR(self.firmata.analog_read(3)) / 25.0 * 300
        self.analog3out.value = self.firmata.analog_read(3)

        print "firmata: ",self.digital2out.value, self.digital3out.value, self.digital4out.value,  self.analog1out.value, self.analog2out.value, self.analog3out.value
    

class Collision(Node):

    def __init__(self):
        Node.__init__(self)

        self.polysIn = NodeInput("polygons")
        self.inputs.append(self.polysIn)
        
        self.collide = NodeOutput("collision events")
        self.outputs.append(self.collide)
        self.myPolygon = None
    
    def setup(self):
            try:
                print "---------------"
                print "trying to load collision data"
                f = open(self.filename)
                print "file opened"
                d2 = f.readlines()
                print "data read",d2
                self.myPolygon = ofPolygon()
                for d in d2:
                    p = eval(d)
                    p = ofVec3f(p[0],p[1])
                    self.myPolygon.addPoint(p)
                    print "added",p.x,p.y
                print "Done!"
                print "---------------"
            except:
                pass
    
    def compute(self):

 #       print "check collide"
 #       print self.minx, self.maxx, self.miny, self.maxy

        self.collide.value = 0

        if self.polysIn.value == None:
            return

        if self.myPolygon:
            for p in self.polysIn.value[0]:
                for point in p:
                    if ofInsidePoly(point[0],point[1],self.myPolygon.points):
                        self.collide.value = 1
#                        print "COLLIDE (poly)"
                        return
            
        else:
          for p in self.polysIn.value[0]:
            for point in p:
                
                if point[0] > self.minx and point[0] < self.maxx and point[1] > self.miny and point[1] < self.maxy:
                    self.collide.value = 1
                    print "COLLIDE"
                    return
    

class OSCReceive(Node):
    def __init__(self):
        Node.__init__(self)
        self.oscOut = NodeOutput("OSC receive")
        self.outputs.append(self.oscOut)
        self.currentMessage = 0
        self.port = 6000
        self.tag = "/ariel"
    
    def setup(self):
        import simpleOSC
        simpleOSC.initOSCServer(ip='127.0.0.1', port=int(self.port))
        simpleOSC.setOSCHandler(self.tag, self.receiveMessage)
        # setOSCHandler("/int", self.receiveMessage)
    
    def compute(self):
        # print "curmess", self.currentMessage
        try:
            self.oscOut.value = self.currentMessage[0]
        except:
            self.oscOut.value = self.currentMessage
    
    def receiveMessage(addr, tags, data, source, *args):
        # print addr, tags, data, source, args
        addr.currentMessage = source
    

class OSCSend(Node):
    def __init__(self):
        Node.__init__(self)
        self.oscIn = NodeInput("OSC send")
        self.inputs.append(self.oscIn)
        self.server = "127.0.0.1"
        self.port = 6000
        self.tag = "/ariel"
    
    def setup(self):
        import simpleOSC
        # print self.server == '127.0.0.1', self.port
        simpleOSC.initOSCClient('127.0.0.1', int(self.port))
        # initOSCClient(port=6001)

    def compute(self):
        if self.oscIn.value != None:
            simpleOSC.sendOSCMsg(self.tag, [self.oscIn.value])
    

class OSCFilter(Node):
    def __init__(self):
        Node.__init__(self)
        self.oscIn = NodeInput("OSC message")
        self.inputs.append(self.oscIn)
        self.filterBy = NodeInput("message number")
        self.inputs.append(self.filterBy)
        
        self.itemOut = NodeOutput("item output")
        self.outputs.append(self.itemOut)
    
    def setup(self):
        pass
    
    def compute(self):
        if self.filterBy.value == None:
            self.filterBy.value = 0
        #self.itemOut.value = self.oscIn.value[0]
        if isinstance(self.oscIn.value, list):
            self.itemOut.value = self.oscIn.value[int(self.filterBy.value)]
    

class RotaryEncoders(Node):
    
    def __init__(self):
        Node.__init__(self)
        files = os.listdir("/dev")
        files = filter(lambda f: "tty.usbmodem" in f, files)
        print "firmata candidates:",files
        print "choosing",files[0]
        
        self.portname = "/dev/" + files[0] #"/dev/tty.usbmodemfd3121"
        
        self.mag1 = NodeOutput("rotary 1")
        self.outputs.append(self.mag1)
        self.mag2 = NodeOutput("rotary 2")
        self.outputs.append(self.mag2)
        
        #MAGNET STUFF
        # arrays to store pin readings (1 or 0)
        self.v1Pin = [0, 0, 0, 0, 0, 0, 0, 0]
        self.v2Pin = [0, 0, 0, 0, 0, 0, 0, 0]
        self.conv = [127, 63,62,58,56,184,152,24,8,72,73,77,79,15,47,175,191,\
            159,31,29,28,92,76,12,4,36,164,166,167,135,151,215,223,207,143,142,\
            14,46,38,6,2,18,82,83,211,195,203,235,239,231,199,71,7,23,19,3,1,9,\
            41,169,233,225,229,245,247,243,227,163,131,139,137,129,128,132,148,\
            212,244,240,242,250,251,249,241,209,193,197,196,192,64,66,74,106,122,\
            120,121,125,253,252,248,232,224,226,98,96,32,33,37,53,61,60,188,190,\
            254,126,124,116,112,113,49,48,16,144,146,154,158,30,94,95]
        self.pinThresh = 1000
        
        # actual angles
        self.v1read = 0
        self.v2read = 0
        self.v1angle = 0
        self.v2angle = 0
        self.mag1cal = 247
        self.mag2cal = 188
        
    
    def setup(self):
        self.firmata = firmata.Arduino(self.portname, 57600)
        for i in range(2, 13):
            self.firmata.pin_mode(i, firmata.INPUT)
    
    def compute(self):
        self.firmata.poll()
        
        self.readPins()
        self.angleFromPins()
        
        #print self.v1angle + 180, self.v2angle + 180
        self.mag1.value = self.v1angle + 180
        self.mag2.value = self.v2angle + 180
    
    def readPins(self):
        for i in range(len(self.v2Pin)):
            self.v2Pin[i] = 0
        
        for i in range(len(self.v1Pin)):
            self.v1Pin[i] = self.firmata.digital_read(i + 2)
        # split this up because of the analog pins
        #for i in range(3):
        #    self.v2Pin[i] = self.firmata.digital_read(i + 10)
        self.v2Pin[0] = self.firmata.digital_read(10)
        self.v2Pin[1] = self.firmata.digital_read(11)
        self.v2Pin[2] = self.firmata.digital_read(12)
        if self.firmata.analog_read(5) > self.pinThresh:
            self.v2Pin[3] = 1
        if self.firmata.analog_read(4) > self.pinThresh:
            self.v2Pin[4] = 1
        if self.firmata.analog_read(3) > self.pinThresh:
            self.v2Pin[5] = 1
        if self.firmata.analog_read(2) > self.pinThresh:
            self.v2Pin[6] = 1
        if self.firmata.analog_read(1) > self.pinThresh:
            self.v2Pin[7] = 1
        self.v2read = self.v1Pin[0]+self.v1Pin[1]*2+self.v1Pin[2]*4+self.v1Pin[3]*8+self.v1Pin[4]*16+self.v1Pin[5]*32+self.v1Pin[6]*64+self.v1Pin[7]*128
        self.v1read = self.v2Pin[0]+self.v2Pin[1]*2+self.v2Pin[2]*4+self.v2Pin[3]*8+self.v2Pin[4]*16+self.v2Pin[5]*32+self.v2Pin[6]*64+self.v2Pin[7]*128
    
    def angleFromPins(self):
        for i in range(len(self.conv)):
            if self.conv[i] == self.v1read:
                self.v1angle = (i*360 / 128-self.mag2cal) * math.pi/180
                #print self.v1angle
                xx = math.cos(self.v1angle)
                yy = math.sin(self.v1angle)
                self.v1angle = math.degrees( math.atan2(yy, xx) )
            if self.conv[i] == self.v2read:
                self.v2angle = (i*360 / 128-self.mag2cal) * math.pi/180
                xx = math.cos(self.v2angle)
                yy = math.sin(self.v2angle)
                self.v2angle = math.degrees( math.atan2(yy, xx) )
        
    

class Arduino(Node):
    
    def __init__(self):
        Node.__init__(self)
        # ins and outs are brought over from node.py...
        # they determine which pins we will actually set and read.
        self.ins = []
        self.outs = []
        # self.aPin is the number of digital pins,
        # used to determine when a pin is analog vs. digital
        self.aPin = 12
        #----
        for i in range(0, 12):
            # create the digital pin inputs and outputs
            self.inputs.append(NodeInput("pin"+str(i+2)))
            self.outputs.append(NodeOutput("pin"+str(i+2)))
        for i in range(0, 6):
            # create the analog outputs
            self.outputs.append(NodeOutput("a"+str(i)))
        #----
        files = os.listdir("/dev")
        files = filter(lambda f: "tty.usbmodem" in f, files)
        print "firmata candidates:",files
        print "choosing",files[0]
        self.portname = "/dev/" + files[0]
    
    def setup(self):
        self.firmata = firmata.Arduino(self.portname, 57600)
        for i in self.ins:
            # counterintuitive: ins are inputs to the node,
            #which are actually OUTPUTS to the arduino pins
            if i < self.aPin:
                self.firmata.pin_mode(i+2, firmata.OUTPUT)
                print "set pin",i+2,"to firmata.OUTPUT"
        for i in self.outs:
            if i < self.aPin:
                self.firmata.pin_mode(i+2, firmata.INPUT)
                print "set pin",i+2,"to firmata.INPUT"
        for i in self.ins:
            self.firmata.digital_write(i+2, firmata.LOW)
    
    def compute(self):
        self.firmata.poll()
        for i in self.ins:
            # self.ins are incoming messages, which go to the OUTPUTS
            if self.inputs[i].value > 0:
                self.firmata.digital_write(i+2, firmata.HIGH)
            else:
                self.firmata.digital_write(i+2, firmata.LOW)
        for i in self.outs:
            if i >= self.aPin:
                # read the analog pins (if they are hooked up to anything)
                self.outputs[i].value = self.firmata.analog_read(i - self.aPin)
            else:
                # then read the digital pins
                self.outputs[i].value = self.firmata.digital_read(i+2) 

colorMapBlue = {}
for n in range(101):
    colorMapBlue[n] = (n/100.0,n/100.0,1)

colorMapRainbow = {}
w = wavelen2rgb.wavelen2rgb
def getWave(f):
    return 390 + f * 290.0

for n in range(101):
    colorMapRainbow[n] = w(getWave(n/100.0))
    colorMapRainbow[n][0] /= 100.0
    colorMapRainbow[n][1] /= 100.0
    colorMapRainbow[n][2] /= 100.0

colorMapRedBlue = {}

for n in range(51):
    b = 0.8
    g = 0.8 * n / 50
    r = 0.8 * n / 50
    colorMapRedBlue[n] = (r,g,b)

for n in range(51,101):
    r = 0.8
    g = 0.8 * (100 - n) / 50
    b = 0.8 * (100 - n) / 50
    colorMapRedBlue[n] = (r,g,b)   

class DataDisplay(Node):

    def __init__(self):
        Node.__init__(self)
        self.vectorData = NodeInput("vector data")
        self.inputs.append(self.vectorData)

        self.scalarData = NodeInput("scalar data")
        self.inputs.append(self.scalarData)        

        self.x = NodeInput("x position")
        self.inputs.append(self.x)

        # self.drawingOrder = NodeInput("drawing order")
        # self.inputs.append(self.drawingOrder)


        self.y = NodeInput("y position")
        self.inputs.append(self.y)
        
        self.z = NodeInput("z position")
        self.inputs.append(self.z)
        
        self.r = NodeInput("rotation")
        self.inputs.append(self.r)
        
        self.s = NodeInput("scale")
        self.inputs.append(self.s)
        
        self.drawFlag = NodeInput("to draw or not to draw")
        self.inputs.append(self.drawFlag)

        global colorMapRainbow
        global colorMapRedBlue
        global colorMapBlue
        
        self.colorMaps = [colorMapRainbow, colorMapRedBlue, colorMapBlue]
        
        
    
    def setup(self):

        self.x.value = 0
        self.y.value = 0
        self.z.value = 0
        self.s.value = 1.0
        self.drawFlag.value = 1
        # self.drawingOrder.value = 10        
        
        print "using color map:",self.colorMapIndex

        self.colorMap = self.colorMaps[self.colorMapIndex]
    
    def draw(self):
        
        if not self.drawFlag.value:
            return
        
        #print self.__class__, self.x.value,self.y.value, self.z.value
        
        if self.x.value == None:
            self.x.value = 0
        if self.y.value == None:
            self.y.value = 0
        if self.z.value == None:
            self.z.value = 0
        if self.s.value == None:
            self.s.value = 1
        if self.r.value == None:
            self.r.value = 0       
        #self.zIndex = self.z.value
        self.zIndex = 0
        
        glPushMatrix()
        glTranslatef(self.x.value,self.y.value, self.z.value)
        glScalef(self.s.value, self.s.value, self.s.value)
        glRotatef(self.r.value, 0, 0, 1)
        
        square = 20
        
        if self.scalarData.value != None:
            xlen, ylen = self.scalarData.value.shape
            
            xindex = ofGetWidth()/2 - square / 2.0 * xlen
            yindex = ofGetHeight()/2 - square / 2.0 * ylen
            
            for x in range(xlen):
                for y in range(ylen):
                    apply(glColor3f,self.colorMap[int(self.scalarData.value[x][y])])
#                    print "color",colorMap[int(self.scalarData.value[x][y])]
#                    print "rect",xindex + x * square, yindex + y * square, xindex + (x + 1) * square, yindex + (y + 1) * square
                    glRectf(xindex + x * square, yindex + y * square, xindex + (x + 1) * square, yindex + (y + 1) * square)
        
        glLineWidth(3)
        glColor3f(1,1,1)
        glBegin(GL_LINES)
        
        if self.vectorData.value != None:
         
         for v in self.vectorData.value:
         
           try:
             glColor3f(v.r1, v.g1, v.b1)
           except:
             glColor3f(v.r, v.g, v.b)               
##            print v.x1, v.y1, v.x2, v.y2
           glVertex3f(v.x1, v.y1, 0)
           
           glColor3f(v.r2, v.g2, v.b2)
           glVertex3f(v.x2, v.y2, 0)
           
           if v.hasArrowhead:
               glEnd()
               a = geom.getGLDegreesFromRadians(geom.getAngle((v.x1,v.y1),(v.x2,v.y2)))
               glPushMatrix()
               glTranslatef(v.x2, v.y2, 0)
               glRotatef(-a,0,0,1)
               glBegin(GL_POLYGON)
               glVertex3f(0,0,0)
               glVertex3f(-6,-13,0)
               glVertex3f(6,-13,0)
               glEnd()
               glPopMatrix()
               glBegin(GL_LINES)
           
        glEnd()
        
        glPopMatrix()  
    

class DataCollector(Node):

    def __init__(self):
        Node.__init__(self)
        self.xPos = NodeInput("x")
        self.yPos = NodeInput("y")
        self.isCollecting = NodeInput("trigger")
        self.clearData = NodeInput("erase all")
        self.videoSync = NodeInput("video sync")
        self.inputs = [self.xPos, self.yPos, self.isCollecting, self.clearData, self.videoSync]

        self.vectors = []
        self.prevX = None
        self.prevY = None
        self.vectorOut = NodeOutput("vector list")
        self.outputs = [self.vectorOut]

    def compute(self):
        if self.clearData.value == 1:
            self.vectors = []
            self.vectorOut.value = self.vectors

        if self.isCollecting.value:
            if self.xPos.value == None:
                self.xPos.value = 0
            if self.yPos.value == None:
                self.yPos.value = 0

            # if the video sync input is not connected to anything...
            if self.videoSync.value == None:
                self.saveVector()
            # if video sync is connected, only record data when it reads 1
            elif self.videoSync.value == 1:
                self.saveVector()

        else:
            # if the trigger reads 0 and points have been recorded...
            if self.vectors:
                # and if a separator hasn't been added yet...
                if self.vectors[-1].separator == 0:
                    # add a 'separator' vector. in Curve Display,
                    # data will not be displayed for this vector
                    v = Vector()
                    v.separator = 1
                    self.vectors.append(v)
                    self.vectorOut.value = self.vectors

    def isDuplicate(self, v1, v2):
        # compare vectors to see if they have all the same values!
        old = (v1.x1, v1.y1, v1.x2, v1.y2)
        new = (v2.x1, v2.y1, v2.x2, v2.y2)
        if old == new:
            return True
        return False

    def saveVector(self):
        # if a previous point has been recorded
        if self.prevX and self.prevY:
            # make a new vector with the current & previous inputs
            v = Vector()
            v.x1, v.y1 = self.xPos.value, self.yPos.value
            v.x2, v.y2 = self.prevX, self.prevY
            v.r1, v.g1, v.b1 = 0.57, 0.77, 0.86
            v.r2, v.g2, v.b2 = 0.57, 0.77, 0.86
            # as an extra measure, prevent duplicate vectors
            # if self.vectors:
            #     if not self.isDuplicate(v, self.vectors[-1]):
            #         self.vectors.append(v)
            #         self.vectorOut.value = self.vectors
            # else:
            self.vectors.append(v)
            self.vectorOut.value = self.vectors

        self.prevX = self.xPos.value
        self.prevY = self.yPos.value

class CurveDisplay(Node):

    def __init__(self):
        Node.__init__(self)
        self.vectorsIn = NodeInput("vector list")
        self.inputs = [self.vectorsIn]
        self.color = "FFFFFF"

    def setup(self):
        pass

    def draw(self):
        if self.vectorsIn.value:
            ofSetHexColor(int(self.color, 16))
            # ofSetColor(255, 255, 255)
            ofSetLineWidth(2)
            ofNoFill()
            ofBeginShape()
            for v in self.vectorsIn.value:
                if v.separator == 1:
                    ofNextContour()
                else:
                    ofVertex(v.x1, v.y1)
            ofEndShape(False)
            ofFill()


class ExpressionBuilder(Node):

    def __init__(self):
        Node.__init__(self)
        self.expression = ""
        self.a = NodeInput("a")
        self.b = NodeInput("b")
        self.c = NodeInput("c")
        self.d = NodeInput("d")
        self.inputs = [self.a, self.b, self.c, self.d]
        self.result = NodeOutput("result")
        self.outputs = [self.result]

    def setup(self):
        pass

    def compute(self):
        self.result.value = self.evaluate(self.expression, self.a.value, self.b.value, self.c.value, self.d.value)

    def evaluate(self, expr, a, b, c, d):
        try:
            return eval(expr)
        except TypeError:
            return None


class MouseInput(Node):

    def __init__(self):
        Node.__init__(self)
        self.mX = NodeOutput("Mouse X")
        self.mY = NodeOutput("Mouse Y")
        self.left = NodeOutput("Left Click")
        self.right = NodeOutput("Right Click")
        self.outputs = [self.mX, self.mY, self.left, self.right]

    def mouseEvent(self, x, y, b=-1):
        self.mX.value = x
        self.mY.value = y
        self.left.value = 0
        self.right.value = 0
        if b == 0:
            self.left.value = 1
        elif b == 2:
            self.right.value = 1

    def mouseReleased(self):
        self.left.value = 0
        self.right.value = 0


class VariableGetter(Node):
    def __init__(self):
        Node.__init__(self)
        self.name = ""
        self.value = None
        self.out = NodeOutput("out")
        self.outputs = [self.out]
        self.callback = self.returnZero

    def compute(self):
        self.out.value = self.callback()

    def returnZero(self):
        return 0

    def setGetterCallback(self, c):
        self.callback = c


class VariableSetter(Node):
    def __init__(self):
        Node.__init__(self)
        self.zIndex = -1
        self.name = ""
        self.input = NodeInput("in")
        self.inputs = [self.input]

    def setterFunction(self):
        return self.input.value
    

class LogicButton(Node):
    def __init__(self):
        Node.__init__(self)
        self.input = NodeInput("in")
        self.inputs = [self.input]
        self.output = NodeOutput("out")
        self.outputs = [self.output]

        self.firstPositive = True

    def compute(self):
        if self.input.value:
            if self.firstPositive == True:
                self.firstPositive = False
                self.output.value = 1
            else:
                self.output.value = 0
        else:
            self.firstPositive = True
            self.output.value = 0


class LogicToggle(Node):
    def __init__(self):
        Node.__init__(self)
        self.input = NodeInput("in")
        self.inputs = [self.input]
        self.output = NodeOutput("out")
        self.outputs = [self.output]

        self.firstPositive = True
        self.toggle = False

    def compute(self):
        if self.input.value:
            if self.firstPositive == True:
                self.firstPositive = False
                self.toggle = not self.toggle
        else:
            self.firstPositive = True
        if self.toggle == True:
            self.output.value = 1
        else:
            self.output.value = 0


class LogicGate(Node):
    def __init__(self):
        Node.__init__(self)
        self.controlIn = NodeInput("control")
        self.inputOne = NodeInput("input 1")
        self.inputTwo = NodeInput("input 2")
        self.inputs = [self.controlIn, self.inputOne, self.inputTwo]
        self.output = NodeOutput("output")
        self.outputs = [self.output]

    def compute(self):
        if self.controlIn.value != None:
            if self.controlIn.value == 0 and self.inputOne.value:
                self.output.value = self.inputOne.value
            if self.controlIn.value == 1 and self.inputTwo.value:
                self.output.value = self.inputTwo.value

class PrintInput(Node):
    def __init__(self):
        Node.__init__(self)
        self.name = ""
        self.input = NodeInput("in")
        self.inputs = [self.input]
        self.output = NodeOutput("out (optional)")
        self.outputs = [self.output]

    def compute(self):
        if self.input.value != None:
            print self.name,"says:",self.input.value
        else:
            # print self.name,"says: not getting any data at the moment."
            pass
        self.output.value = self.input.value


class ImageMask(Node):
    def __init__(self):
        Node.__init__(self)
        self.filename = ""
        self.input = NodeInput("image")
        self.inputs = [self.input]
        self.output = NodeOutput("image")
        self.outputs = [self.output]

        self.maskImage = ofImage()
        self.scrGrab = ofImage()
        self.maskedOutput = ofxCvColorImage()

    def setup(self):
        self.maskImage.loadImage(self.filename)
        self.maskedOutput.allocate(640, 480)
        #self.scrGrab.allocate(640, 480, OF_IMAGE_COLOR)

    def compute(self):
        if self.input.value and self.input.value[1] == True:
            ofEnableAlphaBlending()
            self.input.value[0].draw(0,0)
            self.maskImage.draw(0,0)
            self.scrGrab.grabScreen(0, 0, 640, 480)
            self.maskedOutput.setFromPixels(self.scrGrab.getPixels(), 640, 480)
            self.output.value = [self.maskedOutput, True]
        else:
            # keeping with the image is new True/False protocol.
            self.output.value = [self.maskedOutput, False]


class ButtonDelay(Node):
    def __init__(self):
        Node.__init__(self)
        self.input = NodeInput("input")
        self.delay = NodeInput("delay (seconds)")
        self.inputs = [self.input, self.delay]

        self.output = NodeOutput("output")
        self.outputs = [self.output]

        self.prevTime = 0
        self.delaying = False

    def compute(self):
        if self.input.value != None and self.delay.value:
            if self.delaying == True:
                if time.time() - self.prevTime >= self.delay.value:
                    self.output.value = 1
                    self.delaying = False
            else:
                self.output.value = 0

            if self.input.value == 1:
                self.prevTime = time.time()
                self.delaying = True
            

class DrawCode(Node):
    def __init__(self):
        Node.__init__(self)
        self.expression = ""
        self.in1 = NodeInput("in1")
        self.in2 = NodeInput("in2")
        self.inputs = [self.in1, self.in2]

    def draw(self):
        in1, in2 = self.in1.value, self.in2.value
        try:
            eval(self.expression)
        except:
            pass


class KeyboardInput(Node):
    def __init__(self):
        Node.__init__(self)
        self.out = NodeOutput("key")
        self.outputs = [self.out]
        #
        self.keyBuffer = None
        self.newEvent = False

    def compute(self):
        if self.newEvent:
            self.out.value = self.keyBuffer 
            self.newEvent = False
        else:
            self.out.value = None

    def keyEvent(self, key):
        self.keyBuffer = key
        self.newEvent = True


class GUIButton(Node):
    def __init__(self):
        Node.__init__(self)
        self.button_label = "Button"

        self.xPos = NodeInput("x position")
        self.yPos = NodeInput("y position")
        self.visible = NodeInput("visible")
        self.width = 100
        self.height = 50
        self.inputs = [self.xPos, self.yPos, self.visible]

        self.out = NodeOutput("on/off")
        self.outputs = [self.out]

        self.hover = False
        self.isPressed = False

    def setup(self):
        # determine the width of the button based on the label length
        self.width = max(self.str_width(self.button_label) + 20, 80)

    def str_width(self, string):
        total = 0
        for c in string:
            total += glutBitmapWidth(GLUT_BITMAP_8_BY_13, ord(c))
        return total

    def mouseMoved(self, x, y):
        if self.xPos.value < x < self.xPos.value + self.width and self.yPos.value < y < self.yPos.value + self.height and self.visible.value == 1:
            self.hover = True
            return 1
        self.isPressed = False
        self.hover = False
        return 0

    def mousePressed(self, x, y):
        if self.xPos.value < x < self.xPos.value + self.width and self.yPos.value < y < self.yPos.value + self.height and self.visible.value == 1:
            self.isPressed = True
            return 1
        return 0

    def mouseDragged(self, x, y):
        if self.xPos.value < x < self.xPos.value + self.width and self.yPos.value < y < self.yPos.value + self.height and self.visible.value == 1:
            self.isPressed = True
            return 1
        self.isPressed = False
        self.hover = False
        return 0


    def mouseReleased(self, x, y):
        if self.xPos.value < x < self.xPos.value + self.width and self.yPos.value < y < self.yPos.value + self.height and self.visible.value == 1:
            self.isPressed = False
            return 1
        return 0

    def compute(self):
        if self.visible.value == None:
            self.visible.value = 1

        if self.isPressed:
            self.out.value = 1
        else:
            self.out.value = 0

    def draw(self):
        if self.visible.value == None or self.visible.value == 1:
            if self.isPressed:
                glColor3f(0.4, 0.4, 0.4)
            elif self.hover:
                glColor3f(0.8, 0.8, 0.8)
            else:
                glColor3f(0.7, 0.7, 0.7)

            if self.xPos.value and self.yPos.value:
                glRectf(self.xPos.value, self.yPos.value, self.xPos.value + self.width, self.yPos.value + self.height)
                ofSetColor(0, 0, 0)
                ofDrawBitmapString(self.button_label, self.xPos.value + 10, self.yPos.value + self.height/2 + 3)


class NumberEvent(Node):
    def __init__(self):
        Node.__init__(self)
        self.number_input = 0

        self.input = NodeInput("event or number")
        self.inputs = [self.input]

        self.output = NodeOutput("number")
        self.outputs = [self.output]

    def compute(self):
        if self.input.value:
            self.output.value = float(self.number_input)
        else:
            self.output.value = None


class Combiner(Node):
    def __init__(self):
        Node.__init__(self)
        self.current = 0

        self.inA = NodeInput("a")
        self.inB = NodeInput("b")
        self.inC = NodeInput("c")
        self.inD = NodeInput("d")
        self.inputs = [self.inA, self.inB, self.inC, self.inD]

        self.out = NodeOutput("output")
        self.outputs = [self.out]

    def compute(self):
        for i in self.inputs:
            if i.value or i.value == 0:
                self.current = i.value
                return
        self.out.value = self.current


class MonoSelector(Node):
    def __init__(self):
        Node.__init__(self)

        self.control = NodeInput("control")
        self.inputs = [self.control]

        self.out1 = NodeOutput("0")
        self.out2 = NodeOutput("1")
        self.out3 = NodeOutput("2")
        self.out4 = NodeOutput("3")
        self.outputs = [self.out1, self.out2, self.out3, self.out4]

    def compute(self):
        for o in self.outputs:
            o.value = 0
        if self.control.value != None:
            try:
                self.outputs[int(self.control.value)].value = 1
            except IndexError:
                pass


class PlaySound(Node):
    def __init__(self):
        Node.__init__(self)
        self.filename = ""

        self.playControl = NodeInput("play sound")
        self.volume = NodeInput("volume (0-1)")
        self.donePlaying = NodeOutput("done playing")
        self.inputs = [self.playControl, self.volume]
        self.outputs = [self.donePlaying]

        self.sound = ofSoundPlayer()
        self.sound.setMultiPlay(True)
        self.playing = False

    def setup(self):
        newPathList = self.filename.split("/")
        # print "newPath list:",newPathList
        newPath = ""
        soundFile = newPathList[-1]
        for i in newPathList[:-1]:
            newPath += i + "/"
        ofSetDataPathRoot(newPath)
        # print "SOUND FILE:",soundFile
        try:
            self.sound.loadSound(soundFile)
        except:
            print "sound could not be loaded"

    def compute(self):
        if self.volume.value != None:
            vol = ofClamp(self.volume.value, 0, 1)
            self.sound.setVolume(vol)
        if self.playControl.value == 1:
            self.sound.play()
            self.playing = True
        if self.playing:
            if self.sound.getIsPlaying() == False:
                self.playing = False
                self.donePlaying.value = 1
        else:
            self.donePlaying.value = 0



# THESE are here so that the node.py-to-player.py translation doesn't throw an error.
class Container(Node):
    def __init__(self):
        Node.__init__(self)

class ContainerInlet(Node):
    def __init__(self):
        Node.__init__(self)
        self.outputs = [NodeOutput("number in")]

class ContainerOutlet(Node):
    def __init__(self):
        Node.__init__(self)
        self.inputs = [NodeInput("number out")]

class ContainerTitle(Node):
    def __init__(self):
        Node.__init__(self)
#------------------------------------------------------------------------------------


class Counter(Node):
    def __init__(self):
        Node.__init__(self)

        self.plusEvent = NodeInput("plus event")
        self.minusEvent = NodeInput("minus event")
        self.increment = NodeInput("increment")
        self.inputs = [self.plusEvent, self.minusEvent, self.increment]

        self.output = NodeOutput("output")
        self.outputs = [self.output]

        self.init_val = 0
        self.value = 0

    def setup(self):
        self.value = self.init_val

    def compute(self):
        if self.plusEvent.value:
            if self.increment.value:
                self.value += self.increment.value
            else:
                self.value += 1
        elif self.minusEvent.value:
            if self.increment.value:
                self.value -= self.increment.value
            else:
                self.value -= 1
        self.output.value = self.value


class TimeGraph(Node):
    def __init__(self):
        Node.__init__(self)

        self.x_in = NodeInput("x")
        self.y_in = NodeInput("y")
        self.x_move = NodeInput("x increment")
        self.y_move = NodeInput("y increment")
        self.inputs = [self.x_in, self.y_in, self.x_move, self.y_move]

        # these values will be populated from the node's textfields
        self.x_pos, self.y_pos, self.graph_width, self.graph_height = 0,0,0,0
        self.hex_color = "FFFFFF"

        self.vectors = []

    def compute(self):
        x_plus, y_plus = 0, 0
        # are we moving in the X this frame?
        if self.x_move.value:
            x_plus = self.x_move.value
        # how about in the Y?
        if self.y_move.value:
            y_plus = self.y_move.value
        # change all points based on the move values
        for v in self.vectors:
            v.x1 += x_plus
            v.y1 += y_plus
        # find points outside of the bondaries and remove them
        points_to_remove_x, points_to_remove_y = [], []
        if x_plus != 0:
            points_to_remove_x = [v for v in self.vectors if v.x1 > self.x_pos + self.graph_width or v.x1 < self.x_pos]
        if y_plus != 0:
            points_to_remove_y = [v for v in self.vectors if v.y1 > self.y_pos + self.graph_width or v.y1 < self.y_pos]
        for p in points_to_remove_x:
            self.vectors.remove(p)
        for p in points_to_remove_y:
            self.vectors.remove(p)
        # print "gonna remove these:",points_to_remove
        if self.x_in.value != None and self.y_in.value != None:
            v = Vector()
            v.x1 = self.x_in.value
            v.x1 = ofClamp(v.x1, self.x_pos, self.x_pos + self.graph_width)
            v.y1 = self.y_in.value
            v.y1 = ofClamp(v.y1, self.y_pos, self.y_pos + self.graph_height)
            self.vectors.append(v)
        # if self.x_in.value != None:
        #     x_plus = self.x_in.value
        # if self.y_in.value != None:
        #     y_plus = self.y_in.value
        # for v in self.vectors:
        #     v.x1 += x_plus
        #     v.y1 += y_plus

    def draw(self):
        if self.vectors:
            #ofSetColor(146, 197, 217)
            if self.hex_color:
                try:
                    ofSetHexColor(int(self.hex_color, 16))
                except:
                    ofSetColor(255, 255, 255)
            else:
                ofSetColor(255, 255, 255)
            ofSetLineWidth(2)
            ofNoFill()
            ofBeginShape()
            for v in self.vectors:
                ofVertex(v.x1, v.y1)
            ofEndShape(False)
            ofFill()


class Vector2D(Node):
    def __init__(self):
        Node.__init__(self)

        self.x = NodeInput("x")
        self.y = NodeInput("y")
        self.x_vel = NodeInput("x velocity")
        self.y_vel = NodeInput("y velocity")
        self.multiplier = NodeInput("multiplier")
        self.inputs = [self.x, self.y, self.x_vel, self.y_vel, self.multiplier]

        self.angle = NodeOutput("angle")
        self.mag = NodeOutput("magnitude")
        self.outputs = [self.angle, self.mag]

        self.px, self.py = 0, 0

    def compute(self):
        if self.multiplier.value == None:
            self.multiplier.value = 1
        if self.x_vel.value != None and self.y_vel.value != None:
            a = math.atan2(self.y_vel.value, self.x_vel.value)
            self.angle.value = math.degrees(a) + 180
            self.mag.value = ((self.x_vel.value - self.px)**2 + (self.y_vel.value - self.py)**2)**0.5
            self.px, self.py = self.x_vel.value, self.y_vel.value

    def draw(self):
        if self.x.value != None and self.y.value != None and self.x_vel.value != None and self.y_vel.value != None:
            glColor3f(1, 1, 0)
            glLineWidth(3)
            glBegin(GL_LINES)
            glVertex3f(self.x.value, self.y.value, 0)
            glVertex3f(self.x.value + self.x_vel.value, self.y.value + self.y_vel.value, 0)
            glEnd()
            glLineWidth(1)

            glColor3f(0, 0.5, 1)

            length = math.hypot(self.x_vel.value, self.y_vel.value) * self.multiplier.value

            glPushMatrix()
            glTranslatef(self.x.value, self.y.value, 0)
            if self.angle.value != 0 and self.angle.value != None:  
                glRotatef(math.degrees(self.angle.value), 0, 0, 1)
            glRectf(0, -3, length, 3)

            glBegin(GL_POLYGON)
            glVertex3f(length, -8, 0)
            glVertex3f(length, 8, 0)
            glVertex3f(length + 12, 0, 0)
            glEnd()

            glPopMatrix()

activeNodes = []


import arielplugin

arielplugin.Node = Node

#print "prepping for plugins..."

import node

for obj in dir(node):
    c = getattr(node, obj)
    try:
        if issubclass(c,node.NodeInput):
            exec "arielplugin."+c.__name__+ " = NodeInput"
            #print "added",c.__name__
        if issubclass(c,node.NodeOutput):
            exec "arielplugin."+c.__name__+ " = NodeOutput"
            #print "added",c.__name__            
    except:
        pass

#print "loading plugins..."

for f in os.listdir("User Nodes"):
    if f[-3:] != ".py":
        continue
    sys.path.append("User Nodes")
    module = f[:-3]
    #print "importing",module
    exec "import "+module
    exec "mod = "+module
    if not eval("hasattr("+module+", 'arielplugin')"):
        #print "module",module,"is missing required arielplugin attribute"
        continue
    for o in dir(mod):
        #print "looking for classes"
        c = getattr(mod,o)
        if hasattr(c,"ARIELCLASS"):
            #print o,"is an ariel class"
            exec o+" = c"
        else:
            #print o,"is not an ariel class"
            pass

#print "plugin load complete"

#print Multiplier

for n in nodes:
    #print n
    classname = string.splitfields(string.split(n[0])[1],".")[1]
    #print classname
    newNode = eval(classname + "()")
    inputs = n[1]
    outputs = n[2]
    params = n[3]

    #print classname,inputs,outputs,params
    
    for i in inputs:
        label, number = i
        c = newNode.getInput(label)
        #if not c:
            #print "no connection found for label",label
        c.id = number
    for o in outputs:
        label, number = o
        
        c = newNode.getOutput(label)
        #if not c:
            #print "no connection found for label",label
        c.id = number
    for key in params.keys():
        cmd = "newNode."+key+ " = " + `params[key]`
        #print cmd
        exec(cmd)
    
    #print classname, newNode
    activeNodes.append(newNode)

#print "active",activeNodes

for c in connections:
    f = None
    t = None
    for a in activeNodes:
        f = a.getOutputByID(c[0])
        if f:
            #print "found f",f
            break
    for a in activeNodes:
        t = a.getInputByID(c[1])
        if t:
            #print "found t",t
            break
    f.connection = t
    #print "connection set:",f,t


from psl import *

import fonts
import time

import os

def ofSetupScreen():
    w = ofGetWidth()
    h = ofGetHeight()
    screenFov = 2.0
    eyeX = w / 2.0
    eyeY = h / 2.0
    halfFov = math.pi * screenFov / 360.0
    theTan = math.tan(halfFov)
    dist = eyeY / theTan
    nearDist = dist / 10.0	# near / far clip plane
    farDist = dist * 10.0
    aspect = w / float(h)
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(screenFov, aspect, nearDist, farDist)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(eyeX, eyeY, dist, eyeX, eyeY, 0.0, 0.0, 1.0, 0.0)
    
    glScalef(1, -1, 1)           # invert Y axis so increasing Y goes down.
    glTranslatef(0, -h, 0)       # shift origin up to upper-left corner.
    


class ArielApp(ofBaseApp):
    def setup(self):
        global activeNodes
        self.nodes = activeNodes
        self.count = 0
        self.mouseEvent = self.noMouseInput
        self.keyEvent = self.noKeyEvent
        self.kinectInstance = None
        self.guiButtons = []
        for n in self.nodes:
            n.setup()
        for n in self.nodes:
            if isinstance(n, MouseInput):
                self.mouseEvent = n.mouseEvent
            elif isinstance(n, KeyboardInput):
                self.keyEvent = n.keyEvent
            elif isinstance(n, Kinect) or isinstance(n, SimpleKinect):
                self.kinectInstance = n
            elif isinstance(n, GUIButton):
                self.guiButtons.append(n)
        self.routeSettersToGetters()
        ofDisableDataPath()
        ofDisableSetupScreen()
        ofSetFrameRate(60)
        # ofSetVerticalSync(True)
        ofEnableSmoothing()

    def routeSettersToGetters(self):
        setters = []
        getters = []
        for n in self.nodes:
            if isinstance(n, VariableSetter):
                setters.append(n)
            elif isinstance(n, VariableGetter):
                getters.append(n)
        if setters and getters:
            for s in setters:
                for g in getters:
                    if s.name == g.name:
                        g.setGetterCallback(s.setterFunction)

    def update(self):
        for n in self.nodes:
            n.compute()
            n.update()
        # for n in self.nodes:
        #     n.update()
        
        
        self.count += 1
        self.count %= 100
        # if not (self.count):
        #     self.nodes.sort()
    
    def draw(self):
        # ofSetupScreenPerspective(0, 0, OF_ORIENTATION_UNKNOWN, 1, 60, 0, 0)
        ofSetupScreenPerspective(ofGetWidth(), ofGetHeight(), OF_ORIENTATION_UNKNOWN, 1, 60, 0, 0)
        ofBackground(0,0,0)
        for n in self.nodes:
            n.draw()
    
    def mouseMoved(self, x, y):
        self.mouseEvent(x, y)
        # if there are gui buttons, loop through them
        for b in self.guiButtons:
            if b.mouseMoved(x, y):
                return

    def mousePressed(self, x, y, b):
        self.mouseEvent(x, y, b)
        # if there are gui buttons, loop through them
        for b in self.guiButtons:
            if b.mousePressed(x,y):
                return

    def mouseDragged(self, x, y, b):
        self.mouseEvent(x, y, b)
        # if there are gui buttons, loop through them
        for b in self.guiButtons:
            if b.mouseDragged(x,y):
                return
	
    def mouseReleased(self, *args):
        if len(args) > 0:
            self.mouseEvent(args[0], args[1])
            # if there are gui buttons, loop through them
            for b in self.guiButtons:
                if b.mouseReleased(args[0],args[1]):
                    return

    def keyPressed(self, key):
        self.keyEvent(key)

    def noMouseInput(self, *args):
        pass

    def noKeyEvent(self, *args):
        pass
    

#util.smoothAndLovely()
if runfullscreen:
#    print "before run",ofGetScreenWidth(),float(ofGetScreenHeight())
#    util.setupWindow(1000,1400, OF_WINDOW)
    import commands
    ans = commands.getoutput("""osascript -e 'tell application \"Finder\" to get bounds of window of desktop' """)
    fields = string.splitfields(ans,",")
    # print "ANS",ans,string.atoi(fields[-2]),string.atoi(fields[-1])
    print "---- Fullscreen mode:", str(fields[-2]) + " x" + str(fields[-1])
    util.setupWindow(string.atoi(fields[-2]),string.atoi(fields[-1]), OF_FULLSCREEN)
#    ofSetupOpenGL(2560,1600, OF_FULLSCREEN)
else:
    util.setupWindow(1024,768, OF_WINDOW)
#    util.setupWindow(1600, 1200, OF_WINDOW)    

ofRunApp(ArielApp())
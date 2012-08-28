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

import string
import time
import random
import math

from psl import *
from psl import util
from psl import gui
from psl import fontmanager
from psl import drawutils
from psl.mathtools import lerper
import color_pallet
import node_descriptions
import cPickle

class Node(gui.Button):
    
    def __init__(self):
        gui.Button.__init__(self)

        # -- a note about self.draggable:
        # ---- this is a quicker, global way to check if an object is an
        # ---- instance of Node. it can be used instead of isinstance(object, node.Node)
        self.draggable = True

        self.label = "to be named"
        self.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        self.inputs = []
        self.outputs = []

        self.color = color_pallet.node_box_bg
        
        self.w = 43
        self.h = 43
        
        self.lastMouseUpTimestamp = 0
        self.doubleClickDelayThreshold = 0.4

        self.tooltip = node_descriptions.get(self.label)
        
        # self.notes = gui.LargeTextField(self)
        # self.notes.setBorder(gui.LargeTextField.BORDER_ACTIVE_ONLY)
        # self.notes.w = 20
        # self.notes.h = 20
        
        self.propertyWindow = gui.Window()
        
        # self.propertyOkay = gui.Button(self.propertyWindow)
        # self.propertyOkay.setLabel("okay")
        # self.propertyOkay.callback = self.propertyWindow.hide
        # self.propertyOkay.showLabel = 1
        # self.propertyOkay.setColor((0.5,0.5,0.5))
        # self.propertyOkay.w = 50
        # self.propertyOkay.h = 25
        # self.placePropertyOkay()
        
        self.wasMovedOnThisClick = 0
        
        self.selector = gui.manager.getSelectionManager()
        
        class xButton(gui.Button):
            
            def draw(self):
                glPushMatrix()
                glTranslatef(self.x+5, self.y+5, 0)
                glColor3f(1,0,0)
                glRotatef(45,0,0,1)
                glRectf(-1,-4,1,4)
                glRectf(-4,-1,4,1)
                glPopMatrix()
        
        self.deleteButton = xButton(self)
        self.deleteButton.callback = self.handleDeleteRequest
        self.deleteButton.w = 10
        self.deleteButton.h = 10
        
#        self.hoverCallback = self.deleteButton.show
#        self.endHoverCallback = self.deleteButton.hide
        
        
        self.doubleClickCallback = self.showPropertyWindow
        self.downCallback = self.singleClickCallback
        self.icon = ofImage()
        self.icon.loadImage("icons/user.png")
        
        self.deleteButton.callback = self.handleDeleteRequest
        self.placeDeleteButton()
        
        #self.callback = self.activateNotes
        self.callback = None
    
    def activateNotes(self):
        self.notes.askForFocus()
    
    def initializeConnections(self):
        print "initialize connections"
        for c in self.connections:
            print "conn",c
            variableName, connType, label = c
            variableName = "self."+variableName
            conn = connType(self, label)
            exec variableName+" = conn"
            print "try",connType
            if issubclass(connType, NodeInput):
                print "add input",label
                self.addInput(conn)
            if issubclass(connType, NodeOutput):
                print "add input",label                
                self.addOutput(conn)
        self.label = self.__class__.ARIELCLASS
    
    def doSimplePropertyWindow(self,desc=""):
        title = gui.Label(self.propertyWindow)
        title.setMessage(self.label)
        title.setPosition(10, 0)
        title._setW(280)
        title.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        self.helpLabel = gui.Label(self.propertyWindow)
        self.propertyWindow.w = 300
        self.propertyWindow.h = 150
        # self.placePropertyOkay()
        # self.helpLabel.setMessage(desc)
        self.helpLabel.setMessage("This node has no properties.")
        self.helpLabel.setPosition(10,30)
        self.helpLabel._setW(260)
    
    def placePropertyOkay(self):
        pass
    
    def getInputByName(self, n):
        for i in self.inputs:
            if i.label == n:
                return i
    
    def getOutputByName(self, n):
        for i in self.outputs:
            if i.label == n:
                return i
    
    def placeDeleteButton(self):
        self.deleteButton.setPosition(self.w - self.deleteButton.w,  0)
    
    def handleDeleteRequest(self):
        if self.mouseState == gui.MouseState.MOUSE_HOVER:
            self.delete()
    
    def delete(self):
        gui.manager.propertyDrawer.release(self)
        for i in self.inputs + self.outputs:
            i.disconnect()
        try:
            gui.manager.objects.remove(self)
        except:
            pass
    
    def setParameterDict(self, d):
        pass
    
    def getParameterDict(self):
        p = {}
        return p

    def copyAttributes(self, old_node):
        self.setParameterDict( old_node.getParameterDict() )
    
    def getExportData(self):
        inputs = map(lambda o: (o.label,id(o)), self.inputs)
        outputs = map(lambda o: (o.label,id(o)), self.outputs)
        prams = self.getParameterDict()
        layout = (self.x, self.y, self.w, self.h)
        return `self.__class__`,inputs, outputs, prams, layout
    
    def showPropertyWindow(self):
        # the reversal here is so that drop-down menus overlap each other correctly.
        # all other GUI elements are unaffected by the ordering.
        reversedList = self.propertyWindow.children[::-1]
        gui.manager.propertyDrawer.populate(self, reversedList)
    
    def maybeCallDoubleClickCallback(self):
        #print "DOUBLE CLICK!"
        if self.doubleClickCallback:
            self.doubleClickCallback()

    def singleClickCallback(self):
        if self.selector.isSelected(self):
            pass
        else:
            self.selector.deselectAll()
            self.selector.select(self)
    
    def addInput(self, i):
        self.inputs.append(i)
        self.doConnectionLayout()
    
    def addOutput(self, o):
        self.outputs.append(o)
        self.doConnectionLayout()
    
    def doConnectionLayout(self):

        self.w = max(43, max(len(self.outputs),len(self.inputs))*25)
        
        start = 10
        end = self.w - 10
        outSpacing = float(end - start)/max(1,len(self.outputs)-1)
        outStartX = 10 + outSpacing
        
        if len(self.outputs):
            self.outputs[0].setPosition(10,self.h+7)
        for o in self.outputs[1:]:
            o.setPosition(outStartX,self.h+7)
            outStartX += outSpacing
        
        end -= 6
        inSpacing = float(end - start)/max(1,len(self.inputs)-1)
        inStartX = 10 + inSpacing
        
        if len(self.inputs):
            self.inputs[0].setPosition(10, -6)
        for i in self.inputs[1:]:
            i.setPosition(inStartX, -6)
            inStartX += inSpacing
        
        # self.w = max(43, max(len(self.outputs),len(self.inputs))*25)
        # self.w = 20 + max(len(self.outputs)*outSpacing, len(self.inputs)*inSpacing)
        # self.w = max(43, max(len(self.outputs),len(self.inputs))*min(inSpacing, outSpacing))
        self.placeDeleteButton()
    
    def handleMouse(self, *args):
        
        if len(self.children):
            childArgs = []
            if len(args) == 3:
                cx1 = args[0] - self.x
                cy1 = args[1] - self.y
                childArgs = [cx1, cy1, args[2]]
            if len(args) == 2:
                cx1 = args[0] - self.x
                cy1 = args[1] - self.y
                childArgs = [cx1, cy1]
            for c in self.children:
                if isinstance(c, NodeInput) or isinstance(c, NodeOutput):
                    # print "skip"
                    continue
                # print "sending mouse check to child of node",c,self
                if apply(c.handleMouse, childArgs):
                    #print "node child consumed"
                    return 1
                    
        for c in self.inputs + self.outputs:
            apply(c.handleMouse, args)
        
        # MOUSE RELEASED
        if len(args) == 0:
            retval = 0
            if self.mouseState == gui.MouseTweaker.MOUSE_DRAGGING_US:
                 if self.lastMouseX > self.x and self.lastMouseX < self.x + self.w and self.lastMouseY > self.y and self.lastMouseY < self.y + self.h:
                     self.maybeCallCallback()
                     if not self.wasMovedOnThisClick:
                         if gui.ctrlIsPressed():
                             self.selector.toggleSelection(self)
                         else:
                             self.selector.deselectAll()
                             self.selector.toggleSelection(self)

                     if time.time() - self.lastMouseUpTimestamp < self.doubleClickDelayThreshold:
                         self.maybeCallDoubleClickCallback()
                     else:
                         self.lastMouseUpTimestamp = time.time()
                     retval = 1
            # grab global mouse x&y, use that to find out whether we are hovering or not
            x,y = gui.manager.ruler.x, gui.manager.ruler.y
            if self.x < x < self.x + self.w and self.y < y < self.y + self.h:
                self.mouseState = gui.MouseState.MOUSE_HOVER
            else:
                self.mouseState = gui.MouseTweaker.MOUSE_UP
            #print "node return",retval
            return retval
        
        # MOUSE MOVED
        if len(args) == 2:
            if self.mouseState == gui.MouseTweaker.MOUSE_UP:
                if args[0] > self.x and args[0] < self.x + self.w and args[1] > self.y and args[1] < self.y + self.h:
#                    print "hover begin",self
                    self.mouseState = gui.MouseState.MOUSE_HOVER
                    self.maybeCallHoverCallback()
                    # gui.manager.setHoverNode(self)
#                    print self,"mouse",self.mouseState
                    return 1
                    
            if self.mouseState == gui.MouseState.MOUSE_HOVER:
                gui.manager.setHoverNode(self)
                if not (args[0] > self.x and args[0] < self.x + self.w and args[1] > self.y and args[1] < self.y + self.h):
#                    print "hover end"
                    self.mouseState = gui.MouseTweaker.MOUSE_UP
                    self.maybeCallEndHoverCallback()
                    return 1

        # MOUSE PRESSED, DRAGGED, OR RELEASED
        if len(args) == 3:
            if self.mouseState == gui.MouseTweaker.MOUSE_DRAGGING_US:
                if self.lastMouseX or self.lastMouseY:
                    self.x += args[0] - self.lastMouseX
                    self.y += args[1] - self.lastMouseY
                    if (args[0] - self.lastMouseX) != 0 and (args[1] - self.lastMouseY) != 0:
                        self.wasMovedOnThisClick = 1
                    self.selector.notifyMove(self, args[0] - self.lastMouseX, args[1] - self.lastMouseY)
                
                self.lastMouseX = args[0]
                self.lastMouseY = args[1]
                return 1
                
            if self.mouseState in (gui.MouseTweaker.MOUSE_UP, gui.MouseState.MOUSE_HOVER):
#                print "check mouse",
                if args[0] > self.x and args[0] < self.x + self.w and args[1] > self.y and args[1] < self.y + self.h:
#                    print "engaged"
                    self.wasMovedOnThisClick = 0
                    self.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_US
                    gui.manager.setMouseOnNode(self)
                    self.lastMouseX = args[0]
                    self.lastMouseY = args[1]
                    self.maybeCallDownCallback()
#                    print "HANDLED"
                    return 1
                else:
                    self.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_ELSEWHERE
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        for i in self.inputs:
            i.draw()
        for o in self.outputs:
            o.draw()
        #self.notes.draw()
        glPopMatrix()

        if self.selector.isSelected(self):
            gui.Button.drawHighlight(self)
            gui.Button.draw(self)
        else:
            gui.Button.draw(self)
            gui.Button.drawOutline(self, color_pallet.node_box_outline)
        
        if self.icon:
            ofEnableAlphaBlending()
            glColor3f(1, 1, 1)
            self.icon.draw(self.x+ self.w/2 - 12,self.y + 8)

        if gui.manager.showNames or self.mouseState == gui.MouseState.MOUSE_HOVER or self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            if self.selector.isSelected(self):
                apply(glColor3f, color_pallet.node_box_outline_highlight_top)
            else:
                apply(glColor3f, color_pallet.node_box_text)
            self.font.drawString(self.label,self.x + self.w + 7, self.y + self.h - 34)

        if self.mouseState == gui.MouseState.MOUSE_HOVER:
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            self.deleteButton.draw()
            glPopMatrix()

        if gui.manager.alignTool and self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            apply(ofSetColor, color_pallet.align_tool)
            ofLine(0, self.y, ofGetWidth(), self.y)
            ofLine(self.x, 0, self.x, ofGetHeight())

    def drawOrderNumber(self, n):
        glColor3f(1.0, 0.38, 0.22)
        ofCircle(self.x, self.y + self.h/2, 12)
        glColor3f(1, 1, 1)
        self.font.drawString(str(n), self.x - self.font.stringWidth(str(n))/2.0 - 1, self.y + self.h/2 + 6)
    

class NodeInput(gui.PSGObject):
    
    def __init__(self, parent, label="unnamed input"):
        gui.PSGObject.__init__(self, parent)
        self.label = label
        self.w = 10
        self.h = 6
        self.labelOpacityLerper = lerper.Lerper(1,0,2)
        self.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        self.labelXoffset = self.font.stringWidth(self.label)
        self.accepts = []
        self.connectCallback = None
        #self.inputColor = (0.3, 0.3, 0.3)
        self.inputColor = color_pallet.default_input
    
    def onConnect(self, f):
        if self.connectCallback:
            self.connectCallback(f)
    
    def disconnect(self):
        global connector
        connector.remove(self)

    def getParent(self):
        global connector
        return connector.getParent(self)
    
    def setLabel(self, l):
        self.label = l
        self.labelXoffset = self.font.stringWidth(self.label)
    
    def handleMouse(self, *args):
#        print "INPUT HANDLE MOUSE",args
        distThresholdSq  = 150.0
        if len(args) >= 2:
            x,y = self.getAbsolutePosition()
#            print "x,y",args[0],args[1], x, y
            if ofDistSquared(args[0],args[1], x, y) < distThresholdSq:
                if self.labelOpacityLerper.getGoal() != 1:
                    self.labelOpacityLerper = lerper.Lerper(self.labelOpacityLerper.compute(), 1, 0.25)
            else:
                self.labelOpacityLerper = lerper.Lerper(self.labelOpacityLerper.compute(), 0, 0.25)
    
    def canConnect(self, output):
        global connector
        if connector.isConnected(self):
            return 0
        if not len(self.accepts):
            return 1
        for i in self.accepts:
            if isinstance(output, i):
                return 1
        return 0
    
    def draw(self):
        apply(glColor3f, self.inputColor)
        glBegin(GL_TRIANGLE_FAN)
        # middle point
        glVertex3f(self.x + self.w/2 - 2, self.y + self.h/2,self.z)
        # ?
        glVertex3f(self.x + self.w/2 - self.h/2 - 2, self.y - 1, self.z)
        # top left?
        glVertex3f(self.x - 2, self.y - 1,self.z)
        glVertex3f(self.x - 2, self.y + self.h,self.z)
        glVertex3f(self.x + self.w - 2, self.y + self.h,self.z)
        glVertex3f(self.x + self.w - 2, self.y - 1,self.z)
        glVertex3f(self.x + self.w/2 + self.h/2 - 2, self.y - 1,self.z)
        glEnd()

        # o = 2

        # glBegin(GL_POLYGON)
        # # top left
        # glVertex3f(self.x - o, self.y - o, 0)
        # # middle
        # glVertex3f(self.x - 3 + self.w/2, self.y + 2, 0)
        # glVertex3f(self.x - o + self.w, self.y - o, 0)
        # # bottom
        # glVertex3f(self.x - o + self.w, self.y - o + self.h + 2, 0)
        # glVertex3f(self.x - o, self.y - o + self.h + 2, 0)
        # glEnd()

        if self.labelOpacityLerper.compute() > 0.01:
            c = (color_pallet.node_box_text[0], color_pallet.node_box_text[1], color_pallet.node_box_text[2], self.labelOpacityLerper.compute())
            # glColor4f(color_pallet.node_box_text, self.labelOpacityLerper.compute())
            apply(glColor4f, c)
            self.font.drawString(self.label, self.x - 10 - self.labelXoffset, self.y - 5)
    
    
class ConnectionManager:
    
    def __init__(self):
        self.connections = set()
        self.isLoadingFromFile = 0
    
    def clearAll(self):
        self.connections = set()
    
    def getExportData(self):
        return map(lambda c: (id(c[0]),id(c[1])), self.connections)
    
    def add(self, f, t):
        self.connections.add((f,t))
        if not self.isLoadingFromFile:
            t.onConnect(f)
    
    def remove(self, f):
#        print "remove",f,"from",self.connections
        deleted = 1
        while deleted == 1:
            deleted = 0
            for c in self.connections:
                if c[0] == f:
                    self.connections.remove(c)
                    deleted = 1
                    break
                if c[1] == f:
                    self.connections.remove(c)
                    c[0].disconnect()
                    deleted = 1
                    break
    
    def isConnected(self, t):
        for c in self.connections:
            if c[1] == t:
                return True
        return False

    def getParent(self, t):
        for c in self.connections:
            if c[1] == t:
                return c[0]
        return None
    

connector = ConnectionManager()

class NodeOutput(gui.PSGObject):
    
    def __init__(self, parent, label="unnamed output"):
        gui.PSGObject.__init__(self, parent)
        self.label = label
        self.w = 6
        self.h = 6
        self.target = (-50+random.random()*100,80 + 40 * random.random())
        self.arrow = Arrow()
        self.arrow.setStart(0,0)
        self.updateArrowTarget()
        self.mouseState = 0
        self.connection = None
        self.labelOpacityLerper = lerper.Lerper(1,0,2)
        self.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        #self.arrowColor = (1.0, 0.38, 0.22)
        self.arrowColor = color_pallet.default_output
    
    def setLabel(self, l):
        self.label = l
    
    def connect(self, input):
        global connector
        connector.add(self, input)
        self.connection = input
        self.arrow.dontShrink()
    
    def disconnect(self):
        global connector
        connector.remove(self)
        self.connection = None
        self.arrow.shrinkArrow()
    
    def handleMouseRelease(self):
#        print "TARGET",self.target
        x2,y2 = self.getAbsolutePosition()
        check = self.target[0] + x2, self.target[1] + y2
#        print "check",check
        
        for o in gui.manager.objects:
#            print "check",o
            if isinstance(o, Node):
#                print "is a node"
                for i in o.inputs:
#                    print "I>>>",i
                    if i.canConnect(self):
#                        print "can connect"
                        x,y = i.getAbsolutePosition()
#                        print "TRY",x, y, check[0], check[1],ofDistSquared(x, y, check[0], check[1])
                        if ofDistSquared(x, y, check[0], check[1]) < 150:
                            self.connect(i)
                            return 1
        if not self.connection:
            self.arrow.shrinkArrow()
                        
    
    def handleMouse(self, *args):
#        print "OUTPUT HANDLE MOUSE",args
        distThresholdSq  = 80.0
        if len(args) == 2:
            x, y = self.target
            x2,y2 = self.getAbsolutePosition()
            x += x2
            y += y2
#            print "x,y",args[0],args[1], x, y
            if ofDistSquared(args[0],args[1], x, y) < distThresholdSq:
                if self.labelOpacityLerper.getGoal() != 1:
                    self.labelOpacityLerper = lerper.Lerper(self.labelOpacityLerper.compute(), 1, 0.5)
            else:
                self.labelOpacityLerper = lerper.Lerper(self.labelOpacityLerper.compute(), 0, 0.25)
        if len(args) == 0:
            if self.mouseState == gui.MouseTweaker.MOUSE_DRAGGING_US:
                gui.manager.arrowDrag = False
                self.handleMouseRelease()
                self.labelOpacityLerper = lerper.Lerper(self.labelOpacityLerper.compute(), 0, 0.25)
            self.mouseState = gui.MouseTweaker.MOUSE_UP
        if len(args) == 3:
            if self.mouseState == gui.MouseTweaker.MOUSE_DRAGGING_US:
                if self.lastMouseX or self.lastMouseY:
                    x, y = self.target
                    x += args[0] - self.lastMouseX
                    y += args[1] - self.lastMouseY
                    self.target = (x,y)
                    self.updateArrowTarget()
                    self.arrow.dontShrink()
                    gui.manager.arrowDrag = True
                self.lastMouseX = args[0]
                self.lastMouseY = args[1]
                return 1
            if self.mouseState == gui.MouseTweaker.MOUSE_UP:
#                print "check mouse"
                if self.arrow.endPoint:
                    x,y = self.arrow.endPoint
                    x2,y2 = self.getAbsolutePosition()
                    x += x2
                    y += y2
                else:
                   # print "NO END POINT"
                    self.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_ELSEWHERE
                    return
#                print "X,Y,mouse,dist",args[0],args[1], x, y, ofDistSquared(args[0],args[1], x, y)
                if ofDistSquared(args[0],args[1], x, y) < distThresholdSq:
#                    print "OUTPUT engaged"
                    self.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_US
                    self.lastMouseX = args[0]
                    self.lastMouseY = args[1]
                    self.disconnect()
                    self.labelOpacityLerper = lerper.Lerper(self.labelOpacityLerper.compute(), 1, 0.5)
                    return 1
                else:
                    self.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_ELSEWHERE
    
    def updateArrowTarget(self):
        self.arrow.setEnd(self.target[0], self.target[1])
    
    def draw(self):
        #This should be moved to an update callback
        if self.arrow.lerper.compute() < 0.01 and self.arrow.lerper.isDone():
            self.target = (0,0)
            self.updateArrowTarget()
        if self.connection:
            # grab the absolute positions of the current output and the input it is connected to
            x1,y1 = self.getAbsolutePosition()
            x2,y2 = self.connection.getAbsolutePosition()
            self.target = (x2-x1+3,y2-y1+3)
#            print "target is",self.target
            self.updateArrowTarget()
        
        glColor3f(1,1,1)
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(self.arrowColor[0], self.arrowColor[1], self.arrowColor[2])
        self.arrow.draw()
        if self.labelOpacityLerper.compute() > 0.01:
            alpha = self.labelOpacityLerper.compute()
            # ofSetColor(255, 255, 255, int(alpha * 63))
            # ofNoFill()
            # glColor4f(1, 1, 1, alpha * 0.25)
            glColor4f(color_pallet.node_output_highlight[0], color_pallet.node_output_highlight[1], color_pallet.node_output_highlight[2], alpha * 0.33)
            # apply(glColor4f, color_pallet.node_box_outline_highlight_bottom)
            ofCircle(self.arrow.endPoint[0], self.arrow.endPoint[1], 7)
            # ofNoStroke()
            ofFill()
            glColor4f(self.arrowColor[0], self.arrowColor[1], self.arrowColor[2],alpha)
            #Clean up where label is drawn
            self.font.drawString(self.label, self.arrow.endPoint[0] + 15, max(20, self.arrow.endPoint[1] - 6))
        
        glPopMatrix()


# -----------------------------------------------------------------------------------------
# INPUT AND OUTPUT TYPES.
# these are the various types of data ins and outs. They all extend either
# NodeOutput or NodeInput. if you want a datatype to have a specific color,
# add it to color_pallet.py and reference it using:
# self.arrow = color_pallet.whatever (outputs)
# or self.inputColor = color_pallet.whatever (inputs)
# -----------------------------------------------------------------------------------------

class EventOutput(NodeOutput):
    
    def __init__(self, parent, label="event output"):
        NodeOutput.__init__(self, parent, label)

class MatrixOutput(NodeOutput):
    
    def __init__(self, parent, label="matrix output"):
        NodeOutput.__init__(self, parent, label)  

class GlyphOutput(NodeOutput):
    
    def __init__(self, parent, label="glyphs"):
        NodeOutput.__init__(self, parent, label)

class ImageOutput(NodeOutput):
    
    def __init__(self, parent, label="image"):
        NodeOutput.__init__(self, parent, label)
        self.arrowColor = color_pallet.image_output
        
class BlobOutput(NodeOutput):
    
    def __init__(self, parent, label="blobs"):
        NodeOutput.__init__(self, parent, label)
        
class PolygonOutput(NodeOutput):
    
    def __init__(self, parent, label="blob geometry"):
        NodeOutput.__init__(self, parent, label)
        
class ButtonOutput(EventOutput):
    
    def __init__(self, parent, label="button event"):
        EventOutput.__init__(self, parent, label)
        
class SwitchOutput(EventOutput):
    
    def __init__(self, parent, label="switch event"):
        EventOutput.__init__(self, parent, label)
        
class RangeOutput(EventOutput):
    
    def __init__(self, parent, label="range event"):
        EventOutput.__init__(self, parent, label)
        
class NumberOutput(NodeOutput):
    
    def __init__(self, parent, label="number"):
        NodeOutput.__init__(self, parent, label)
        self.arrowColor = color_pallet.number_output

class VectorListOutput(NodeOutput):
    
    def __init__(self, parent, label="vector list"):
        NodeOutput.__init__(self, parent, label)
        
class Scalar2DOutput(NodeOutput):
    
    def __init__(self, parent, label="scalar 2D array"):
        NodeOutput.__init__(self, parent, label)
        
class VelocityOutput(NodeOutput):
    
    def __init__(self, parent, label="velocity"):
        NodeOutput.__init__(self, parent, label)

# INPUTS ---------------------------------------------------------

class NumberInput(NodeInput):
     def __init__(self, parent, label="number"):
        NodeInput.__init__(self, parent, label)
        self.accepts = [NumberOutput, EventOutput]
        self.inputColor = color_pallet.number_input

class MatrixInput(NodeInput):
     def __init__(self, parent, label="matrix"):
        NodeInput.__init__(self, parent, label)
        self.accepts = [MatrixOutput]        

class ImageInput(NodeInput):
     def __init__(self, parent, label="image"):
        NodeInput.__init__(self, parent, label)
        self.accepts = [ImageOutput]
        self.inputColor = color_pallet.image_input

class PolygonInput(NodeInput):
    def __init__(self, parent, label = "polygons"):
        NodeInput.__init__(self, parent, label)
        self.accepts = [PolygonOutput]
        
class GlyphDataInput(NodeInput):
    def __init__(self, parent, label = "glyphs"):
        NodeInput.__init__(self, parent, label)
        self.accepts = [GlyphOutput]
        
class Scalar2DInput(NodeInput):
    def __init__(self, parent, label="data"):
        NodeInput.__init__(self, parent, label)
        self.accepts = [Scalar2DOutput]
        
class VectorListInput(NodeInput):
    def __init__(self, parent, label="vectors"):
        NodeInput.__init__(self, parent,label)
        self.accepts = [VectorListOutput]
        
class PositionInput(NodeInput):
    def __init__(self, parent,label="positions"):
        NodeInput.__init__(self, parent, label)
        self.accepts = [GlyphOutput, BlobOutput]

class BlobInput(NodeInput):
    def __init__(self, parent, label="blobs"):
        NodeInput.__init__(self, parent, label)
        self.accepts = [BlobOutput]

class EventInput(NodeInput):
    def __init__(self, parent,label="events"):
        NodeInput.__init__(self, parent, label)
        self.accepts = [NumberOutput, EventOutput]  


class Arrow:
    
    def __init__(self):
        self.curves = []
        self.start = (0,0)
        self.end = (0,0)
        self.lerper = lerper.Lerper(100,100,0)
        self.shrinkArrow()
        self.endPoint = None
    
    def shrinkArrow(self):
        self.lerper = lerper.Lerper(self.lerper.compute(),0,1)
    
    def dontShrink(self):
        self.lerper = lerper.Lerper(100,100,0)
    
    def setStart(self, x, y):
        self.start = x,y
    
    def setEnd(self, x, y):
        self.end = x,y
        self.compute()
    
    def compute(self):
        self.curves = []
        self.curves.append((self.start[0], self.start[1], self.start[0], self.start[1]+50, self.end[0], self.end[1]-50,self.end[0], self.end[1]))
    
    def computeOLD(self):
        self.curves = []
        midpoint = (self.start[0] + self.end[0]) / 2, (self.start[1] + self.end[1]) / 2
        dist = geom.getDistance(self.start, self.end) 
        shift = 0#dist / 10 * random.random()
        ang = geom.getAngle(self.start, self.end)
        vertex = geom.getPoint(midpoint, ang + math.pi/2, shift)

        ang1 = geom.getAngle(self.start,vertex)
        ang1 += (random.random() - 0.5) * math.pi / 4
        p1 = geom.getPoint(self.start, ang1, dist/2)

        ang2 = geom.getAngle(self.end, self.start)
        ang2 += (random.random() - 0.5) * math.pi / 4
        p2 = geom.getPoint(vertex, ang2, dist/4)
        p3 = geom.getPoint(vertex, ang2+math.pi, dist/4)

        ang3 = geom.getAngle(self.end, vertex)
        ang3 += (random.random() - 0.5) * math.pi / 4
        p4 = geom.getPoint(self.end, ang3, dist/2)
        self.curves.append((self.start[0], self.start[1], p1[0], p1[1], p4[0], p4[1], self.end[0], self.end[1]))
    
    def draw(self):
        glEnable(GL_LINE_SMOOTH)
        ofEnableSmoothing()
        glLineWidth(2)
        glBegin(GL_LINE_STRIP)
        arrowheadLoc = None
        # self.endPoint = self.end
        glVertex3f(0,-6,0)
        offset = 0

        # if self.end != (0, 0):
        #     glVertex3f(0, 5, 0)
        #     glVertex3f(self.end[0], self.end[1] - 10, 0)
        #     glVertex3f(self.end[0], self.end[1], 0)

        for c in self.curves:
            arrowheadLoc = drawutils.slowBezier(c[0],c[1],c[2],c[3],c[4],c[5],c[6],c[7],80,min(100,self.lerper.compute() - offset))
            offset += 100
        glEnd()
        glLineWidth(1)
        if arrowheadLoc:
            self.endPoint = arrowheadLoc[0]
            glPushMatrix()
            glTranslatef(arrowheadLoc[1][0],arrowheadLoc[1][1],0)
            glRotatef(-1*geom.getGLDegreesFromRadians(geom.getAngle(arrowheadLoc[0],arrowheadLoc[1])),0,0,1)
            glBegin(GL_POLYGON)
            glVertex3f(-5,-5,0)
            glVertex3f(0,0,0)
            glVertex3f(5,-5,0)
            glEnd()
            glPopMatrix()


# -----------------------------------------------------------------------------------------
# NODE CLASSES.
# these all extend the Node class. You can expose Node functions for various reasons;
# i.e. to draw differently, set parameters (setParameterDict and getParameterDict), etc.
# -----------------------------------------------------------------------------------------
    

class Camera(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "camera"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/camera.png")
        
        i = Camera.SubtractBackground(self)
        self.addInput(i)
        
        i = NumberInput(self, "threshold")
        self.addInput(i)
        
        i = NumberInput(self, "min blob size")
        self.addInput(i)
        
        i = NumberInput(self, "max blob size")
        self.addInput(i)
        
        self.addOutput(GlyphOutput(self))
        self.addOutput(BlobOutput(self))
        self.addOutput(PolygonOutput(self))
        self.addOutput(ImageOutput(self))
        
        l = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 264-53-50
        
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("camera - properties")
        l.setPosition(10,-4)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("camera number")
        l.setPosition(10,24)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("camera number - indicates which camera to use")
        l.setPosition(10,95)
        l._setW(357)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("mirror image")
        l.w = 200
        l.setPosition(10,73)        
        
        self.mirrorImage = gui.ComboBox(self.propertyWindow)
        self.mirrorImage.setChoices(("no","yes"))
        self.mirrorImage.currentChoice = 0
        self.mirrorImage.setPosition(264-117, 80) 
        
        self.valueWidget = gui.TextEntry(self.propertyWindow)
        self.valueWidget.validateAsNumber()
        self.valueWidget.w = 75+167-200
        self.valueWidget.currentText = "0"
        self.valueWidget.setPosition(264-167+10, 32)
        
        self.placePropertyOkay()
    
    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.valueWidget.currentText = `d["indexvalue"]`
            self.mirrorImage.currentChoice = d["mirrorImage"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["indexvalue"] = string.atof(self.valueWidget.currentText)
        d["mirrorImage"] = self.mirrorImage.currentChoice
        return d
    
    class SubtractBackground(NodeInput):
        
        def __init__(self, parent):
            NodeInput.__init__(self, parent)
            self.setLabel("trigger: subtract background")
        
        def canConnect(self, output):
            global connector
            if connector.isConnected(self):
                return 0
            if isinstance(output, EventOutput):
                return 1
        
    

class SimpleCamera(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "camera"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/camera.png")
        self.addOutput(ImageOutput(self))
        #
        l = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 161
        
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("camera")
        l.setPosition(10,0)
        
        l = gui.Label(self.propertyWindow)
        l.w = 200
        l.setMessage("camera number")
        l.setPosition(10,34)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("mirror image")
        l.w = 200
        l.setPosition(10,73)
        
        self.mirrorImage = gui.ComboBox(self.propertyWindow)
        self.mirrorImage.setChoices(("no","yes"))
        self.mirrorImage.currentChoice = 0
        self.mirrorImage.setPosition(140, 80) 
        
        self.valueWidget = gui.TextEntry(self.propertyWindow)
        self.valueWidget.validateAsNumber()
        self.valueWidget.w = 75+167-200
        self.valueWidget.currentText = "0"
        self.valueWidget.setPosition(140, 42)
        
        self.placePropertyOkay()
    
    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.valueWidget.currentText = `d["indexvalue"]`
            self.mirrorImage.currentChoice = d["mirrorImage"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["indexvalue"] = string.atof(self.valueWidget.currentText)
        d["mirrorImage"] = self.mirrorImage.currentChoice
        return d


class SimpleKinect(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "kinect"
        self.icon.loadImage("icons/kinect.png")
        self.tooltip = node_descriptions.get(self.label)
        self.addOutput(ImageOutput(self))
        #
        l = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 264-53-50
        
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("kinect")
        l.setPosition(10,0)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("camera number")
        l.setPosition(10,34)
        l._setW(357)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("mirror image")
        l.w = 200
        l.setPosition(10,73)
        
        self.mirrorImage = gui.ComboBox(self.propertyWindow)
        self.mirrorImage.setChoices(("no","yes"))
        self.mirrorImage.currentChoice = 0
        self.mirrorImage.setPosition(140, 80)

        self.valueWidget = gui.TextEntry(self.propertyWindow)
        self.valueWidget.validateAsNumber()
        self.valueWidget.w = 75+167-200
        self.valueWidget.currentText = "0"
        self.valueWidget.setPosition(140, 42)

        self.mode = gui.ComboBox(self.propertyWindow)
        self.mode.setChoices(("RGB", "IR", "Depth"))
        self.mode.currentChoice = 2
        self.mode.setPosition(140, 120)

        l = gui.Label(self.propertyWindow)
        l.setMessage("mode")
        l.w = 100
        l.setPosition(10,113)

        # self.exp = gui.NewComboBox(self.propertyWindow)
        # self.exp.setChoices(("one", "two", "thr33"))
        # self.exp.currentChoice = 1
        # self.exp.setPosition(140, 200)
    
    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.valueWidget.currentText = `d["indexvalue"]`
            self.mirrorImage.currentChoice = d["mirrorImage"]
            self.mode.currentChoice = d["mode"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["indexvalue"] = string.atof(self.valueWidget.currentText)
        d["mirrorImage"] = self.mirrorImage.currentChoice
        d["mode"] = self.mode.currentChoice
        return d


class BlobTracking(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "blob tracking"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/blob.png")
        
        self.addInput(ImageInput(self, "image data"))
        self.addInput(NumberInput(self, "min blob size"))
        self.addInput(NumberInput(self, "max blob size"))
        self.addInput(NumberInput(self, "threshold"))
        
        self.addOutput(BlobOutput(self))
        self.addOutput(PolygonOutput(self))
        self.addOutput(ImageOutput(self))
        self.addOutput(NumberOutput(self, "video sync"))
        
        self.doSimplePropertyWindow("Blob tracking. Video sync should only be used with Data Collector.")
        self.propertyWindow.h = 150
        self.placePropertyOkay()


class BlobFilter(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "blob filter"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/filter.png")

        self.addInput(BlobInput(self, "blobs"))
        self.addInput(NumberInput(self, "id"))

        self.addOutput(NumberOutput(self, "x"))
        self.addOutput(NumberOutput(self, "y"))
        self.addOutput(NumberOutput(self, "width"))
        self.addOutput(NumberOutput(self, "height"))

        self.doSimplePropertyWindow("Filter for a list of blobs. 0 (default) will always grab the largest blob.")
        self.propertyWindow.h = 150
        self.placePropertyOkay()
    

class GlyphTracking(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "glyph tracking"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/glyph.png")
        
        self.addInput(ImageInput(self, "image data"))
        self.addOutput(GlyphOutput(self))
        
        self.doSimplePropertyWindow("Glyph tracking.")
        self.propertyWindow.h = 150
        self.placePropertyOkay()

class BackgroundDifferencing(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "bg differencing"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/bgdif.png")

        self.addInput(ImageInput(self, "image data"))
        self.addInput(EventInput(self, "trigger"))

        self.addOutput(ImageOutput(self))

        self.doSimplePropertyWindow("Bg Differencing.")
        self.propertyWindow.h = 150
        self.placePropertyOkay()

class Parameter(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.icon.loadImage("icons/parameter.png")
        self.label = "parameter"
        self.tooltip = node_descriptions.get(self.label)
        self.addInput(NumberInput(self, "value"))
        self.addOutput(NumberOutput(self, "value"))
        
        l = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 264-53-50
        
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("parameter")
        l.setPosition(10,0)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("initial value")
        l.setPosition(10,26)
        
        self.valueWidget = gui.TextEntry(self.propertyWindow)
        self.valueWidget.validateAsNumber()
        self.valueWidget.w = 70
        self.valueWidget.currentText = "0"
        self.valueWidget.setPosition(110, 32)
        
        self.placePropertyOkay()
    
    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.valueWidget.currentText = `d["value"]`
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["value"] = string.atof(self.valueWidget.currentText)
        return d
    

class Conditional(Node):
    
    def __init__(self):
        Node.__init__(self)
        
        self.symbols = {}
        self.symbols["greater than"] = ">"
        self.symbols["less than"] = "<"
        self.symbols["equal to"] = "=="
        self.symbols["not equal to"] = "!="
        self.symbols["greater or equal to"] = ">="
        self.symbols["less or equal to"] = "<="    
        
        self.icon.loadImage("icons/conditional.png")                
        self.label = "conditional"
        self.tooltip = node_descriptions.get(self.label)
        self.addInput(NumberInput(self, "value1"))
        self.addInput(NumberInput(self, "value2"))
        self.addOutput(NumberOutput(self, "value"))

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("conditional")
        l.setPosition(10,0)

        l = gui.Label(self.propertyWindow)
        l.setMessage("value 1")
        l.setPosition(10,24)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("value 2")
        l.setPosition(240,24)   
        
        w = gui.ComboBox(self.propertyWindow)
        w.setChoices(("greater than","less than","equal to","not equal to","greater or equal to","less or equal to"))
        w.setPosition(68,31)
        w.w = 164
        self.relation = w

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        for i in self.inputs:
            i.draw()
        for o in self.outputs:
            o.draw()
        glPopMatrix()

        if self.selector.isSelected(self):
            gui.Button.drawHighlight(self)
            gui.Button.draw(self)
        else:
            gui.Button.draw(self)
            gui.Button.drawOutline(self, color_pallet.node_box_outline)
        
        glColor3f(1, 1, 1)
        width = self.font.stringWidth(self.symbols[self.relation.choices[self.relation.currentChoice]])
        self.font.drawString(self.symbols[self.relation.choices[self.relation.currentChoice]], self.x + self.w/2 - width/2, self.y + self.h/2 + 4)
        if gui.manager.showNames or self.mouseState == gui.MouseState.MOUSE_HOVER or self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            if self.selector.isSelected(self):
                apply(glColor3f, color_pallet.node_box_outline_highlight_top)
            else:
                apply(glColor3f, color_pallet.node_box_text)
            self.font.drawString(self.label,self.x + self.w + 7, self.y + self.h - 34)
        if self.mouseState == gui.MouseState.MOUSE_HOVER:
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            self.deleteButton.draw()
            glPopMatrix()
        if gui.manager.alignTool and self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            apply(ofSetColor, color_pallet.align_tool)
            ofLine(0, self.y, ofGetWidth(), self.y)
            ofLine(self.x, 0, self.x, ofGetHeight())
    
    def getParameterDict(self):
        try:
            d = {}
            d = Node.getParameterDict(self)
            d["relation"] = self.symbols[self.relation.choices[self.relation.currentChoice]]
            return d
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def setParameterDict(self, d):
        Node.setParameterDict(self, d)        
        k = d["relation"]
        for key in self.symbols.keys():
            if self.symbols[key] == k:
                self.relation.currentChoice = self.relation.choices.index(key)
                return
    

class Mathematics(Node):
	
    def __init__(self):
        Node.__init__(self)
        
        self.symbols = {}
        self.symbols["+"] = "+"
        self.symbols["-"] = "-"
        self.symbols["*"] = "*"
        self.symbols["/"] = "/"
        self.symbols["%"] = "%"
        
        self.mathLabel = ["a+b","a-b","a*b","a/b","a%b"]
        self.mathIcons = []
        for i in range(5):
            self.mathIcons.append(ofImage())

        l = gui.Label(self.propertyWindow)
        l.w = 200
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("math")
        l.setPosition(10, 0)

        l = gui.Label(self.propertyWindow)
        l.w = 200
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        l.setMessage("operation to perform")
        l.setPosition(10, 32)
        
        self.icon.loadImage("icons/math.png")
        self.label = "math"
        self.tooltip = node_descriptions.get(self.label)
        self.addInput(NumberInput(self, "a"))
        self.addInput(NumberInput(self, "b"))
        self.addOutput(NumberOutput(self, "value"))
        
        w = gui.ComboBox(self.propertyWindow)
        w.setChoices(("+","-","*","/","%"))
        w.setPosition(10, 63)
        w.w = 80
        self.relation = w
        
        # self.fonttwo = fontmanager.manager.getFont("Frutiger-Roman.ttf", 16)
    
    def getParameterDict(self):
        try:
            d = {}
            d = Node.getParameterDict(self)
            d["relation"] = self.symbols[self.relation.choices[self.relation.currentChoice]]
            return d
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def setParameterDict(self, d):
        Node.setParameterDict(self, d)
        k = d["relation"]
        for key in self.symbols.keys():
            if self.symbols[key] == k:
                self.relation.currentChoice = self.relation.choices.index(key)
                return

    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        for i in self.inputs:
            i.draw()
        for o in self.outputs:
            o.draw()
        glPopMatrix()

        if self.selector.isSelected(self):
            gui.Button.drawHighlight(self)
            gui.Button.draw(self)
        else:
            gui.Button.draw(self)
            gui.Button.drawOutline(self, color_pallet.node_box_outline)
        
        glColor3f(1, 1, 1)
        width = self.font.stringWidth(self.mathLabel[self.relation.currentChoice])
        self.font.drawString(self.mathLabel[self.relation.currentChoice], self.x + self.w/2 - width/2, self.y + self.h/2 + 4)
        if gui.manager.showNames or self.mouseState == gui.MouseState.MOUSE_HOVER or self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            if self.selector.isSelected(self):
                apply(glColor3f, color_pallet.node_box_outline_highlight_top)
            else:
                apply(glColor3f, color_pallet.node_box_text)
            self.font.drawString(self.label,self.x + self.w + 7, self.y + self.h - 34)
        if self.mouseState == gui.MouseState.MOUSE_HOVER:
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            self.deleteButton.draw()
            glPopMatrix()
        if gui.manager.alignTool and self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            apply(ofSetColor, color_pallet.align_tool)
            ofLine(0, self.y, ofGetWidth(), self.y)
            ofLine(self.x, 0, self.x, ofGetHeight())
	

class Image(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "image"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/image.png")                        
        self.addInput(NumberInput(self, "index"))
        self.addInput(NumberInput(self, "x position"))
        self.addInput(NumberInput(self, "y position"))
        self.addInput(NumberInput(self, "z position"))
        self.addInput(MatrixInput(self, "matrix"))
        # self.addInput(NumberInput(self, "drawing order"))
        self.addInput(NumberInput(self, "rotation"))
        self.addInput(NumberInput(self, "scale"))
        self.addInput(NumberInput(self, "transparency"))
        self.addInput(EventInput(self, "to draw or not to draw"))
        
        self.addInput(PolygonInput(self, "mask"))
        self.addInput(ImageInput(self, "image data"))
        
        self.addOutput(NumberOutput(self, "image width"))
        self.addOutput(NumberOutput(self, "image height"))
        
        self.propertyLabel = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 264
        
        self.propertyLabel.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        self.propertyLabel.w = 350
        self.propertyLabel.setMessage("image")
        self.propertyLabel.setPosition(10,0)
        
        # l = gui.Label(self.propertyWindow)
        # l.setMessage("filename")
        # l.setPosition(10,34)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("full size")
        l.w = 200
        l.setPosition(190 - l.font.stringWidth(l.message),95)

        l = gui.Label(self.propertyWindow)
        l.setMessage("align")
        l.w = 200
        l.setPosition(190 - l.font.stringWidth(l.message), 140)    
        
        self.filename = gui.TextEntry(self.propertyWindow)
        self.filename.w = 180
        self.filename.currentText = "filename"
        self.filename.setPosition(10, 60)
        
        self.coverWindow = gui.ComboBox(self.propertyWindow)
        self.coverWindow.setChoices(("no","yes"))
        self.coverWindow.currentChoice = 0
        self.coverWindow.setPosition(210, 102)
        self.coverWindow.w = 71

        self.alignFromCenter = gui.ComboBox(self.propertyWindow)
        self.alignFromCenter.setChoices(("top-left", "center"))
        self.alignFromCenter.currentChoice = 0
        self.alignFromCenter.setPosition(210, 147)
        self.alignFromCenter.w = 71
        
        self.browse = gui.Button(self.propertyWindow)
        self.browse.setLabel("browse...")
        self.browse.callback = self.askForImageFilename
        self.browse.showLabel = 1
        self.browse.autoSize()
        self.browse.setPosition(210, 60)
        self.browse.setColor((0.5,0.5,0.5))
        self.placePropertyOkay()
    
    def askForImageFilename(self):
        f = gui.getFilenameToOpen()
        self.filename.setText(f)
    
    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.filename.currentText = d["filename"]
            self.coverWindow.currentChoice = d["autoAlign"]
            self.alignFromCenter.currentChoice = d["anchor"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = {}
        d = Node.getParameterDict(self)
        d["filename"] = self.filename.currentText
        d["autoAlign"] = self.coverWindow.currentChoice
        d["anchor"] = self.alignFromCenter.currentChoice
        return d
        
    

class Video(Image):
    
    def __init__(self):
        Image.__init__(self)
        self.label = "video"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/video.png")                        
        self.propertyLabel.setMessage("video")
        # self.helpLabel.setMessage("filename - specifies the video file to be displayed")
#        del(self.inputs[-1])
        self.addInput(NumberInput(self, "playback rate"))
    

class DataDisplay(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "simulator data"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/simulator.png")
        self.addInput(VectorListInput(self, "vector data"))
        self.addInput(Scalar2DInput(self, "scalar data"))
        self.addInput(NumberInput(self, "x position"))
        self.addInput(NumberInput(self, "y position"))
        self.addInput(NumberInput(self, "z position"))
        # self.addInput(NumberInput(self, "drawing order"))
        self.addInput(NumberInput(self, "rotation"))
        self.addInput(NumberInput(self, "scale"))
        self.addInput(EventInput(self, "to draw or not to draw"))

        l = gui.Label(self.propertyWindow)
        l.w = 250
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("simulator data")
        l.setPosition(10, 0)

        self.mapLabel = gui.Label(self.propertyWindow)
        self.mapLabel.setMessage("scalar data color map")
        self.mapLabel.setPosition(10,36)
        self.mapLabel._setW(250)

        self.colorMap = gui.ComboBox(self.propertyWindow)
        self.colorMap.setChoices(("rainbow","red-blue","gray-blue"))
        self.colorMap.currentChoice = 0
        self.colorMap.setPosition(180, 40)
    
    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)        
            self.colorMap.currentChoice = d["colorMapIndex"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = {}
        d = Node.getParameterDict(self)        
        d["colorMapIndex"] = self.colorMap.currentChoice
        return d
    

class DataCollector(Node):
    def __init__(self):
        Node.__init__(self)
        self.label = "data collector"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/datacollector.png")
        self.addInput(NumberInput(self, "x"))
        self.addInput(NumberInput(self, "y"))
        self.addInput(EventInput(self, "trigger"))
        self.addInput(NumberInput(self, "erase all"))
        self.addInput(NumberInput(self, "video sync"))

        self.addOutput(VectorListOutput(self))
        self.doSimplePropertyWindow("Stores x,y,z coordinates as a vector list while \
            trigger input is non-zero. Use with Curve Display. Video Sync is used with \
            Blob Tracking to prevent duplicate points.")
        self.placePropertyOkay()


class CurveDisplay(Node):
    def __init__(self):
        Node.__init__(self)
        self.label = "curve display"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/curve.png")
        self.addInput(VectorListInput(self, "vector list"))

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 300
        l.setMessage("curve display")
        l.setPosition(10,0)

        self.color = gui.TextEntry(self.propertyWindow)
        self.color.w = 100
        self.color.currentText = "FFFFFF"
        self.color.setPosition(130, 32)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.w = 200
        l.setMessage("color (hex value)")
        l.setPosition(10, 26)

    def getParameterDict(self):
        try:
            d = {}
            d = Node.getParameterDict(self)
            d["color"] = self.color.currentText
            return d
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def setParameterDict(self, d):
        Node.setParameterDict(self, d)
        self.color.currentText = d["color"]


class Velocity(Node):
    def __init__(self):
        Node.__init__(self)
        self.label = "velocity measurer"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/velocity.png")                        
        self.addInput(NumberInput(self, "x position"))
        self.addInput(NumberInput(self, "y position"))
        self.addOutput(NumberOutput(self, "x velocity"))
        self.addOutput(NumberOutput(self, "y velocity"))
        self.doSimplePropertyWindow("velocity - this node computes x and y velocity from x and y position.")
    

class GlyphFilter(Node):
    def __init__(self):
        Node.__init__(self)
        self.label = "glyph filter"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/filter.png")                                
        self.addInput(GlyphDataInput(self, "glyphs"))
        self.addInput(NumberInput(self, "id"))
        # self.addOutput(GlyphOutput(self, "filtered glyphs"))
        self.addOutput(NumberOutput(self, "x"))
        self.addOutput(NumberOutput(self, "y"))
        self.addOutput(NumberOutput(self, "z"))
        self.addOutput(NumberOutput(self, "angle"))
        self.addOutput(EventOutput(self, "present"))
        self.addOutput(MatrixOutput(self, "matrix"))
        
        # self.helpLabel = gui.Label(self.propertyWindow)
        # self.propertyWindow.w = 300
        # self.propertyWindow.h = 150
        # self.placePropertyOkay()
        # self.helpLabel.setMessage("glyph filter - this node looks for a specific glyph \
        #     from the camera and outputs its x, y, and rotation values.")
        # self.helpLabel.setPosition(10,10)
        # self.helpLabel._setW(280)

        self.doSimplePropertyWindow()
    

class Startup(Node):
    def __init__(self):
        Node.__init__(self)
        self.label = "startup node"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/power.png")                                
        self.addOutput(EventOutput(self, "startup event"))
        
        self.doSimplePropertyWindow("startup node - this node generates an event when the player starts.")
    

class Splitter(Node):
    def __init__(self):
        Node.__init__(self)
        self.label = "splitter"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/splitter.png")
        d = NodeInput(self, "data")
        d.connectCallback = self.handleConnect
        self.addInput(d)
        self.addOutput(NodeOutput(self, "data1"))
        self.addOutput(NodeOutput(self, "data2"))
        self.addOutput(NodeOutput(self, "data3"))
        self.addOutput(NodeOutput(self, "data4"))
        
        self.propertyWindow.w = 377
        l = gui.Label(self.propertyWindow)
        l.setMessage("The splitter node sends the same input data to multiple outputs.")
        l.setPosition(10,10)
        l._setW(357)
        self.placePropertyOkay()
        
    
    # def handleConnect(self, f):
    #     if self.outputs[0].__class__ != f.__class__:
    #         self.outputs[0].disconnect()
    #         self.outputs[1].disconnect()
    #         self.outputs[2].disconnect()
    #         self.outputs[3].disconnect()
    #         self.outputs = []
            
    #         newOutput = f.__class__(self, "data1")
    #         self.addOutput(newOutput)
    #         newOutput = f.__class__(self, "data2")
    #         self.addOutput(newOutput)
    #         newOutput = f.__class__(self, "data3")
    #         self.addOutput(newOutput)
    #         newOutput = f.__class__(self, "data4")
    #         self.addOutput(newOutput)

    def handleConnect(self, f):
        if f.__class__ != self.outputs[0].__class__:
            for o in self.outputs:
                o.disconnect()
        self.switchOutputClass(f)

    def switchOutputClass(self, f):
        for o in self.outputs:
            o.__class__ = f.__class__
            o.arrowColor = f.arrowColor

class Delay(Node):
    def __init__(self):
        Node.__init__(self)
        self.label = "delay node"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/delay.png")
        d = NodeInput(self, "data")
        d.connectCallback = self.handleConnect
        self.addInput(d)
        self.addInput(NumberInput(self, "delay"))
        self.addOutput(NodeOutput(self, "data"))
        
        self.doSimplePropertyWindow()
    
    def handleConnect(self, f):
        if f.__class__ != self.outputs[0].__class__:
            self.outputs[0].disconnect()
            self.outputs = []
            newOutput = f.__class__(self, "data")
            self.addOutput(newOutput)
    

class Collision(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "collision"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/collision.png")
        self.addInput(PolygonInput(self,"polygons"))
        self.addOutput(EventOutput(self,"collision events"))
        self.doSimplePropertyWindow("Collision - This node fires an event whenever a \
            blob enters an area you define. That area can be defined as a rectangle by \
            specifying the X and Y values above. Alternatively a polygon can be loaded from a file.")
        
        self.helpLabel.y+=200 - 65
        self.propertyWindow.h = 300
        self.propertyWindow.w += 60
        self.placePropertyOkay()
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("x minimum")
        l.setPosition(10,24)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("x maximum")
        l.setPosition(183,24)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("y minimum")
        l.setPosition(10,54)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("y maximum")
        l.setPosition(183, 54)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("polygon data file")
        l.setPosition(10,84)        
        
        w = gui.TextEntry(self.propertyWindow)
        w.validateAsNumber()
        w.w = 45
        w.currentText = "100"
        w.setPosition(100, 34)
        self.minx = w
        
        w = gui.TextEntry(self.propertyWindow)
        w.validateAsNumber()        
        w.w = 45
        w.currentText = "200"
        w.setPosition(275, 34)
        self.maxx = w        
        
        w = gui.TextEntry(self.propertyWindow)
        w.validateAsNumber()        
        w.w = 45
        w.currentText = "300"
        w.setPosition(100, 64)
        self.miny = w        
        
        w = gui.TextEntry(self.propertyWindow)
        w.validateAsNumber()        
        w.w = 45
        w.currentText = "400"
        w.setPosition(275, 64)
        self.maxy = w
        
        self.filename = gui.TextEntry(self.propertyWindow)
        self.filename.w = 167
        self.filename.currentText = "C:\\"
        self.filename.setPosition(264-167-6, 32+70)
        
        self.browse = gui.Button(self.propertyWindow)
        self.browse.setLabel("browse...")
        self.browse.callback = self.askForPolyFilename
        self.browse.showLabel = 1
        self.browse.autoSize()
        self.browse.setPosition(274-6, 32+70)
        self.browse.setColor((0.5,0.5,0.5))
    
    def askForPolyFilename(self):
        f = gui.getFilenameToOpen()
        self.filename.setText(f)
    
    def getParameterDict(self):
        try:
            d = {}
            d = Node.getParameterDict(self)        
            d["filename"] = self.filename.currentText
            d["minx"] = string.atof(self.minx.currentText)
            d["miny"] = string.atof(self.miny.currentText)
            d["maxx"] = string.atof(self.maxx.currentText)
            d["maxy"] = string.atof(self.maxy.currentText)
            return d
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def setParameterDict(self, d):
        Node.setParameterDict(self, d)        
        self.filename.currentText = d["filename"]
        self.minx.currentText = `d["minx"]`
        self.miny.currentText = `d["miny"]` 
        self.maxx.currentText = `d["maxx"]` 
        self.maxy.currentText = `d["maxy"]` 
    

class Kinect(Camera):
    
    def __init__(self):
        Camera.__init__(self)
        self.label = "kinect"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/kinect.png")
#        self.addOutput(GlyphOutput(self))
#        self.addOutput(BlobOutput(self))
#        self.addOutput(PolygonOutput(self))
    

class ColladaAnimation(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "collada animation"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/collada.png")
        self.addInput(NumberInput(self, "x position"))
        self.addInput(NumberInput(self, "y position"))
        self.addInput(NumberInput(self, "z position"))
        # self.addInput(NumberInput(self, "drawing order"))
        self.addInput(NumberInput(self, "rotation"))
        self.addInput(NumberInput(self, "scale"))
        self.addInput(MatrixInput(self, "matrix"))       
        self.addInput(EventInput(self, "to draw or not to draw"))
        self.addInput(EventInput(self, "start animation"))
        
        self.propertyLabel = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 264
        
        self.propertyLabel.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        self.propertyLabel.w = 300
        self.propertyLabel.setMessage("collada animation")
        self.propertyLabel.setPosition(10,0)

        self.filename = gui.TextEntry(self.propertyWindow)
        self.filename.w = 180
        self.filename.currentText = "filename"
        self.filename.setPosition(10, 32)
        
        self.browse = gui.Button(self.propertyWindow)
        self.browse.setLabel("browse...")
        self.browse.callback = self.askForImageFilename
        self.browse.showLabel = 1
        self.browse.autoSize()
        self.browse.setPosition(210, 32)
        self.browse.setColor((0.5,0.5,0.5))
        self.placePropertyOkay()
    
    def askForImageFilename(self):
        f = gui.getFilenameToOpen()
        self.filename.setText(f)
    
    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)        
            self.filename.currentText = d["filename"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = {}
        d = Node.getParameterDict(self)        
        d["filename"] = self.filename.currentText
        return d
    

class Firmata(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "firmata"
        self.tooltip = node_descriptions.get(self.label)
        #self.addOutput(ButtonOutput(self))
        #self.addOutput(SwitchOutput(self))
        #self.addOutput(RangeOutput(self))        
        self.icon.loadImage("icons/serial.png")                                        
        
        self.propertyWindow.w = 377
        
        
        self.addOutput(NumberOutput(self, "dial pin one"))
        self.addOutput(NumberOutput(self, "dial pin two"))
        self.addOutput(NumberOutput(self, "dial pin three"))
        self.addOutput(NumberOutput(self, "switch pin"))
        self.addOutput(NumberOutput(self, "button pin one"))
        self.addOutput(NumberOutput(self, "button pin two"))
        
        self.doSimplePropertyWindow("Firmata - This node lets you connect hardware inputs to your system. \
            You can connect a switch between ground and digital pin 2. Buttons can be connected between ground \
            and digital pins 3 and 4. Potentiometers can be used as voltage dividers on analog pins 1, 2 and 3. \
            See the documentation for more details.")
        
        self.propertyWindow.h = 250
        self.placePropertyOkay()


class OSCReceive(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "OSC receive"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/oscr.png")
        self.addOutput(NumberOutput(self, "OSC receive"))

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("OSC receive")
        l.setPosition(10,0)
        l._setW(300)

        # port

        self.port = gui.TextEntry(self.propertyWindow)
        self.port.validateAsNumber()
        self.port.w = 120
        self.port.currentText = "6000"
        self.port.setPosition(10, 50)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("listening to port:")
        l.setPosition(10,24)
        l._setW(300)

        # tag

        self.tag = gui.TextEntry(self.propertyWindow)
        self.tag.w = 120
        self.tag.currentText = "/ariel"
        self.tag.setPosition(10, 90)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("listening for tag:")
        l.setPosition(10,64)
        l._setW(300)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.port.currentText = `d["port"]`
            self.tag.currentText = d["tag"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = {}
        d = Node.getParameterDict(self)        
        d["port"] = self.port.currentText
        d["tag"] = self.tag.currentText
        return d
    

class OSCSend(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "OSC send"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/oscs.png")
        self.addInput(NumberInput(self, "OSC send"))
        
        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("OSC send")
        l.setPosition(10,0)
        l._setW(300)

        # server
        
        self.server = gui.TextEntry(self.propertyWindow)
        self.server.w = 100
        self.server.currentText = "127.0.0.1"
        self.server.setPosition(10, 50)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("server")
        l.setPosition(10,24)
        l._setW(300)

        # port

        self.port = gui.TextEntry(self.propertyWindow)
        self.port.validateAsNumber()
        self.port.w = 80
        self.port.currentText = "6000"
        self.port.setPosition(120, 50)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("port")
        l.setPosition(120,24)
        l._setW(300)

        # tag

        self.tag = gui.TextEntry(self.propertyWindow)
        self.tag.w = 190
        self.tag.currentText = "/ariel"
        self.tag.setPosition(10, 90)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("tag")
        l.setPosition(10,64)
        l._setW(300)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.server.currentText = d["server"]
            self.port.currentText = `d["port"]`
            self.tag.currentText = d["tag"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = {}
        d = Node.getParameterDict(self)
        d["server"] = self.server.currentText
        d["port"] = int(self.port.currentText)
        d["tag"] = self.tag.currentText
        return d
    

class OSCFilter(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "OSC filter"
        self.tooltip = node_descriptions.get(self.label)
        self.addInput(NumberInput(self, "OSC message"))
        self.addInput(NumberInput(self, "message number"))
        self.addOutput(NumberOutput(self, "item output"))
        
        self.doSimplePropertyWindow("Grabs a specific item from an OSC message. Also works with regular lists.")
        self.propertyWindow.h = 200
        self.placePropertyOkay()
    

class RotaryEncoders(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "rotary encoders"
        self.tooltip = node_descriptions.get(self.label)
        self.addOutput(NumberOutput(self, "rotary 1"))
        self.addOutput(NumberOutput(self, "rotary 2"))
        
        self.doSimplePropertyWindow("Reads two rotary encoders as degrees.")
        self.propertyWindow.h = 150
        self.placePropertyOkay()
    

class Arduino(Node):
    
    def __init__(self):
        Node.__init__(self)
        self.label = "Arduino"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/arduino.png")
        for i in range(2, 14):
            self.addInput(NumberInput(self, "pin" + str(i)))
            self.addOutput(NumberOutput(self, "pin" + str(i)))
        for i in range(0, 6):
            self.addOutput(NumberOutput(self, "a" + str(i)))
        # self.addOutput(NumberOutput(self, "pinread"))
        self.doSimplePropertyWindow("Arduino, via Firmata. You can only write at this point in time (reading pins has not been implemented yet).")
        self.propertyWindow.h = 150
        self.placePropertyOkay()
        
        self.ins = []
        self.outs = []
    
    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.ins = `d["ins"]` # array of inputs that are used
            self.outs = `d["outs"]` # array of outputs that are used
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."

    def getParameterDict(self):
        d = Node.getParameterDict(self)
        self.outs = []
        self.ins = []
        for i in range(len(self.outputs)):
            if isinstance(self.outputs[i], NodeOutput) and self.outputs[i].connection != None:
                self.outs.append(i)
        for i in range(len(self.inputs)):
            global connector
            if isinstance(self.inputs[i], NodeInput):
                if connector.isConnected(self.inputs[i]):
                    self.ins.append(i)
                    # print "appended",self.inputs[i].label,"as",i
            
            #elif isinstance(self.children[i], NodeInput):
                #global connector
                #if connector.isConnected(self.children[i]):
                    #self.ins.append(i)
        d["ins"] = self.ins
        d["outs"] = self.outs
        return d

    #------------------------------- these functions are exposed to change the node's appearance

    def doConnectionLayout(self):
        
        start = 10
        end = self.w - 10
        outSpacing = float(end - start)/max(1,len(self.outputs)-1)
        outStartX = 10 + outSpacing
        
        if len(self.outputs):
            self.outputs[0].setPosition(10,self.h+7)
        for o in self.outputs[1:]:
            o.setPosition(outStartX,self.h+7)
            outStartX += outSpacing
        
        inSpacing = outSpacing
        inStartX = 5 + inSpacing
        
        if len(self.inputs):
            self.inputs[0].setPosition(5, -6)
        for i in self.inputs[1:]:   
            i.setPosition(inStartX, -6)
            inStartX += inSpacing
        
        self.w = max(43, max(len(self.outputs),len(self.inputs))*25)
        self.placeDeleteButton()

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        # if not o.connection, draw
        global connector
        for i in range(len(self.inputs)):
            if not connector.isConnected(self.inputs[i]):
                self.outputs[i].draw()
            if not self.outputs[i].connection:
                self.inputs[i].draw()
        for o in self.outputs[len(self.outputs)-6:]:
            o.draw()
        # for i in self.inputs:
        #     i.draw()
        # for o in self.outputs:
        #     o.draw()
        #x x x ------ self.notes.draw() ------ x x x
        glPopMatrix()

        if self.selector.isSelected(self):
            gui.Button.drawHighlight(self)
            gui.Button.draw(self)
        else:
            gui.Button.draw(self)
            gui.Button.drawOutline(self, color_pallet.node_box_outline)

        # if self.icon:
        #     ofEnableAlphaBlending()
        #     self.icon.draw(self.x+ self.w/2 - 12,self.y + 8)
        if gui.manager.showNames or self.mouseState == gui.MouseState.MOUSE_HOVER or self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            if self.selector.isSelected(self):
                apply(glColor3f, color_pallet.node_box_outline_highlight_top)
            else:
                apply(glColor3f, color_pallet.node_box_text)
            self.font.drawString(self.label,self.x + self.w + 7, self.y + self.h - 34)
        boxWidth = 273
        glColor3f(0.9, 0.9, 0.9)
        glRectf(self.x + 5, self.y + 5, self.x + boxWidth + 5, self.y + self.h - 5)
        glRectf(self.x + boxWidth + 17, self.y + 5, self.x + boxWidth + 147, self.y + self.h - 5)
        # ofSetColor(100, 100, 100)
        glColor3f(0.4, 0.4, 0.4)
        self.font.drawString("digital", self.x + boxWidth/2 - 20, self.y + self.h/2 + 5)
        self.font.drawString("analog", self.x + boxWidth + 55, self.y + self.h/2 + 5)
        if self.mouseState == gui.MouseState.MOUSE_HOVER:
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            self.deleteButton.draw()
            glPopMatrix()
        if gui.manager.alignTool and self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            apply(ofSetColor, color_pallet.align_tool)
            ofLine(0, self.y, ofGetWidth(), self.y)
            ofLine(self.x, 0, self.x, ofGetHeight())


class ExpressionBuilder(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "expression builder"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/expr.png")
        self.addInput(NumberInput(self, "a"))
        self.addInput(NumberInput(self, "b"))
        self.addInput(NumberInput(self, "c"))
        self.addInput(NumberInput(self, "d"))
        self.addOutput(NumberOutput(self, "result"))

        l = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 150
        
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("expression builder")
        l.setPosition(10,-4)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("expression using a,b,c, or d as values. e.g. a+b-c*d or a*(b+4)-c")
        l.setPosition(10,62)
        l._setW(357)
        
        self.valueWidget = gui.TextEntry(self.propertyWindow)
        self.valueWidget.w = 250
        self.valueWidget.currentText = "a+b"
        self.valueWidget.setPosition(10, 32)
        self.placePropertyOkay()

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.valueWidget.currentText = d["expression"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["expression"] = self.valueWidget.currentText
        return d


class MouseInput(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "mouse input"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/mouse.png")

        self.addOutput(NumberOutput(self, "Mouse X"))
        self.addOutput(NumberOutput(self, "Mouse Y"))
        self.addOutput(NumberOutput(self, "Left Click"))
        self.addOutput(NumberOutput(self, "Right Click"))

        self.doSimplePropertyWindow("Outputs mouse data.")
        self.placePropertyOkay()


class VariableGetter(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "get var"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/parameter.png")
        self.addOutput(NumberOutput(self, "out"))

        l = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 150
        
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("var get")
        l.setPosition(10,0)

        self.valueWidget = gui.TextEntry(self.propertyWindow)
        self.valueWidget.w = 250
        self.valueWidget.currentText = "myVariable"
        self.valueWidget.setPosition(10, 32)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("specify the name of your variable")
        l.setPosition(10,46)
        l._setW(300)

        self.varFont = fontmanager.manager.getFont("Frutiger-Roman.ttf",9)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.valueWidget.currentText = d["name"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["name"] = self.valueWidget.currentText
        return d

    def draw(self):
        if self.selector.isSelected(self):
            gui.Button.drawHighlight(self)
            gui.Button.draw(self)
        else:
            gui.Button.draw(self)
            gui.Button.drawOutline(self, color_pallet.node_box_outline)

        self.deleteButton.setPosition(self.w - self.deleteButton.w,  0)
        textwidth = self.varFont.stringWidth(self.valueWidget.currentText)
        if textwidth > 23:
            self.w = textwidth + 20
        else:
            self.w = 43
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        for i in self.inputs:
            i.draw()
        for o in self.outputs:
            o.draw()            
        #self.notes.draw()
        glPopMatrix()

        # if self.icon:
        #     ofEnableAlphaBlending()
        #     self.icon.draw(self.x+ self.w/2 - 12,self.y + 8)
        if gui.manager.showNames or self.mouseState == gui.MouseState.MOUSE_HOVER or self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            if self.selector.isSelected(self):
                apply(glColor3f, color_pallet.node_box_outline_highlight_top)
            else:
                apply(glColor3f, color_pallet.node_box_text)
            self.font.drawString(self.label,self.x + self.w + 7, self.y + self.h - 34)
        glColor3f(0.9, 0.9, 0.9)
        self.varFont.drawString(self.valueWidget.currentText, self.x + 10, self.y + self.h/2 + 4)
        if self.mouseState == gui.MouseState.MOUSE_HOVER:
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            self.deleteButton.draw()
            glPopMatrix()
        if gui.manager.alignTool and self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            apply(ofSetColor, color_pallet.align_tool)
            ofLine(0, self.y, ofGetWidth(), self.y)
            ofLine(self.x, 0, self.x, ofGetHeight())


class VariableSetter(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "set var"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/parameter.png")
        self.addInput(NumberInput(self, "in"))

        l = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 150
        
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("var set")
        l.setPosition(10,0)

        self.valueWidget = gui.TextEntry(self.propertyWindow)
        self.valueWidget.w = 250
        self.valueWidget.currentText = "myVariable"
        self.valueWidget.setPosition(10, 32)
        
        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("specify the name of your variable")
        l.setPosition(10,46)
        l._setW(300)

        self.varFont = fontmanager.manager.getFont("Frutiger-Roman.ttf",9)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.valueWidget.currentText = d["name"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["name"] = self.valueWidget.currentText
        return d

    def draw(self):
        if self.selector.isSelected(self):
            gui.Button.drawHighlight(self)
            gui.Button.draw(self)
        else:
            gui.Button.draw(self)
            gui.Button.drawOutline(self, color_pallet.node_box_outline)

        self.deleteButton.setPosition(self.w - self.deleteButton.w,  0)
        textwidth = self.varFont.stringWidth(self.valueWidget.currentText)
        if textwidth > 23:
            self.w = textwidth + 20
        else:
            self.w = 43
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        for i in self.inputs:
            i.draw()
        for o in self.outputs:
            o.draw()            
        #self.notes.draw()
        glPopMatrix()

        # if self.icon:
        #     ofEnableAlphaBlending()
        #     self.icon.draw(self.x+ self.w/2 - 12,self.y + 8)
        if gui.manager.showNames or self.mouseState == gui.MouseState.MOUSE_HOVER or self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            if self.selector.isSelected(self):
                apply(glColor3f, color_pallet.node_box_outline_highlight_top)
            else:
                apply(glColor3f, color_pallet.node_box_text)
            self.font.drawString(self.label,self.x + self.w + 7, self.y + self.h - 34)
        glColor3f(0.9, 0.9, 0.9)
        self.varFont.drawString(self.valueWidget.currentText, self.x + 10, self.y + self.h/2 + 4)
        if self.mouseState == gui.MouseState.MOUSE_HOVER:
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            self.deleteButton.draw()
            glPopMatrix()
        if gui.manager.alignTool and self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            apply(ofSetColor, color_pallet.align_tool)
            ofLine(0, self.y, ofGetWidth(), self.y)
            ofLine(self.x, 0, self.x, ofGetHeight())

class LogicButton(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "button"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/button.png")

        self.addInput(NumberInput(self, "in"))
        self.addOutput(NumberOutput(self, "out"))

        self.doSimplePropertyWindow("Sends only one event for every stream of 1s it receives.")
        self.placePropertyOkay()

class LogicToggle(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "toggle"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/toggle.png")

        self.addInput(NumberInput(self, "in"))
        self.addOutput(NumberOutput(self, "out"))

        self.doSimplePropertyWindow("Flips between 1 and 0 every time it receives a 1. Use with button.")
        self.placePropertyOkay()

class PrintInput(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "print"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/print.png")

        self.addInput(NumberInput(self, "in"))
        self.addOutput(NumberOutput(self, "out (optional)"))

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("print")
        l.setPosition(10,0)

        self.valueWidget = gui.TextEntry(self.propertyWindow)
        self.valueWidget.w = 250
        self.valueWidget.currentText = "print"
        self.valueWidget.setPosition(10, 32)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("specify a unique name if you are using multiple print nodes.")
        l.setPosition(10,52)
        l._setW(220)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.valueWidget.currentText = d["name"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["name"] = self.valueWidget.currentText
        return d

class ImageMask(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "image mask"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/imagemask.png")

        self.addInput(ImageInput(self))
        self.addOutput(ImageOutput(self))

        self.propertyLabel = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 377
        self.propertyWindow.h = 120
        
        self.propertyLabel.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        self.propertyLabel.w = 350
        self.propertyLabel.setMessage("image mask")
        self.propertyLabel.setPosition(10,0)
        
        # l = gui.Label(self.propertyWindow)
        # l.setMessage("filename")
        # l.setPosition(10,24)

        self.filename = gui.TextEntry(self.propertyWindow)
        self.filename.w = 180
        self.filename.currentText = "filename"
        self.filename.setPosition(10, 32)
        
        self.browse = gui.Button(self.propertyWindow)
        self.browse.setLabel("browse...")
        self.browse.callback = self.askForImageFilename
        self.browse.showLabel = 1
        self.browse.autoSize()
        self.browse.setPosition(210, 32)
        self.browse.setColor((0.5,0.5,0.5))
        self.placePropertyOkay()
    
    def askForImageFilename(self):
        f = gui.getFilenameToOpen()
        self.filename.setText(f)
    
    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)        
            self.filename.currentText = d["filename"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = {}
        d = Node.getParameterDict(self)        
        d["filename"] = self.filename.currentText
        return d

class LogicGate(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "gate"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/gate.png")

        self.addInput(NumberInput(self, "control"))
        self.addInput(NumberInput(self, "input 1"))
        self.addInput(NumberInput(self, "input 2"))
        self.addOutput(NumberOutput(self, "output"))

        self.doSimplePropertyWindow("When control = 0, output = input 1. When control = 1, output = input 2. Useful with toggle.")
        self.placePropertyOkay()

class ButtonDelay(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "button delay"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/delay.png")

        self.addInput(NumberInput(self, "input"))
        self.addInput(NumberInput(self, "delay (seconds)"))
        self.addOutput(NumberOutput(self, "output"))

        self.doSimplePropertyWindow("Delays button signals by the delay amount.")
        self.placePropertyOkay()

class DrawCode(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "draw code"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/drawcode.png")

        self.addInput(NumberInput(self, "in1"))
        self.addInput(NumberInput(self, "in2"))

        l = gui.Label(self.propertyWindow)
        
        self.propertyWindow.w = 500
        self.propertyWindow.h = 150
        
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("draw code")
        l.setPosition(10,0)
        
        l = gui.Label(self.propertyWindow)
        l.setMessage("Use in1 and in2 as variables.")
        l.setPosition(10,52)
        l._setW(250)
        
        self.valueWidget = gui.TextEntry(self.propertyWindow)
        self.valueWidget.w = 280
        self.valueWidget.currentText = "glRectf(in1, in2, 100, 100)"
        self.valueWidget.setPosition(10, 32)
        self.placePropertyOkay()

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.valueWidget.currentText = d["expression"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["expression"] = self.valueWidget.currentText
        return d

class KeyboardInput(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "key input"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/keyinput.png")
        self.addOutput(NumberOutput(self, "key"))

        self.doSimplePropertyWindow("Outputs a key's ASCII code once per key event.")
        self.placePropertyOkay()

class GUIButton(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "gui button"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/button.png")

        self.addInput(NumberInput(self, "x position"))
        self.addInput(NumberInput(self, "y position"))
        self.addInput(NumberInput(self, "visible"))
        self.addOutput(NumberOutput(self, "on/off"))

        # property window
        self.propertyWindow.w = 400
        self.propertyWindow.h = 150

        l = gui.Label(self.propertyWindow)
        l.w = 200
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("GUI button")
        l.setPosition(10, 0)

        l = gui.Label(self.propertyWindow)
        l.w = 150
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        l.setMessage("Button Name")
        l.setPosition(10, 26)

        self.labelTextfield = gui.TextEntry(self.propertyWindow)
        self.labelTextfield.w = 170
        self.labelTextfield.currentText = "Button"
        self.labelTextfield.setPosition(120, 32)

        self.placePropertyOkay()

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.labelTextfield.currentText = d["button_label"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."

    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["button_label"] = self.labelTextfield.currentText
        return d

class NumberEvent(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "number event"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/numberevent.png")

        self.addInput(NumberInput(self, "event or number"))
        self.addOutput(NumberOutput(self, "number"))

        self.propertyWindow.w = 400
        self.propertyWindow.h = 150

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("number event")
        l.setPosition(10,0)

        l = gui.Label(self.propertyWindow)
        l.w = 200
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("Send this number every time the input is non-zero.")
        l.setPosition(10, 52)

        self.numberTextfield = gui.TextEntry(self.propertyWindow)
        self.numberTextfield.validateAsNumber()
        self.numberTextfield.w = 100
        self.numberTextfield.currentText = "0"
        self.numberTextfield.setPosition(10, 32)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.numberTextfield.currentText = `d["number_input"]`
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."

    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["number_input"] = float(self.numberTextfield.currentText)
        return d

class Combiner(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "combiner"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/combiner.png")

        self.addInput(NumberInput(self, "a"))
        self.addInput(NumberInput(self, "b"))
        self.addInput(NumberInput(self, "c"))
        self.addInput(NumberInput(self, "d"))

        self.addOutput(NumberOutput(self, "output"))

        self.doSimplePropertyWindow("Continuously sends the last non-zero number it receives.")
        self.placePropertyOkay()

class MonoSelector(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "mono selector"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/monoselector.png")

        self.addInput(NumberInput(self, "control"))

        self.addOutput(NumberOutput(self, "0"))
        self.addOutput(NumberOutput(self, "1"))
        self.addOutput(NumberOutput(self, "2"))
        self.addOutput(NumberOutput(self, "3"))

        self.doSimplePropertyWindow("Continuously send 1 to the output specified by control.")
        self.placePropertyOkay()

# ---------------------------------------------------------------------
# CONTAINER NODE
# ---------------------------------------------------------------------

class Container(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "container"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/container.png")
        self.title = "empty container"

        self.nodeData, self.connectorData = None, None

        self.propertyWindow.w = 377
        self.propertyWindow.h = 150

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("container")
        l.setPosition(10,0)
        l._setW(300)

        self.filename = gui.TextEntry(self.propertyWindow)
        self.filename.w = 200
        self.filename.currentText = "filename"
        self.filename.setPosition(10, 32)

        self.browse = gui.Button(self.propertyWindow)
        self.browse.setLabel("browse...")
        self.browse.callback = self.getAndParseFile
        self.browse.showLabel = 1
        self.browse.autoSize()
        self.browse.setPosition(220, 32)
        self.browse.setColor((0.5,0.5,0.5))
    
    def getAndParseFile(self):
        f = gui.getFilenameToOpen()
        try:
            self.filename.setText(f)
            # open the file and get the stuff out of it
            fm = open(f)
            data = cPickle.load(fm)
            fm.close()
            # further separation of data...
            nodeData, connectorData = data
            self.nodeData = nodeData
            self.connectorData = connectorData

            self.parseExistingData()

            print "success"
        except:
            "Container had a problem opening the requested .ariel file."

    def parseFile(self):
        try:
            fm = open(self.filename.currentText)
            data = cPickle.load(fm)
            fm.close()
            # further separation of data...
            nodeData, connectorData = data
            self.nodeData = nodeData
            self.connectorData = connectorData

            self.parseExistingData()
        except:
            print "Container failed to load a file."

    def parseExistingData(self):
        self.inputs = []
        for o in self.outputs:
            o.disconnect()
        self.outputs = []

        for n in self.nodeData:
            name, inputs, outputs, params, layout = n
            basename = string.splitfields(string.split(name)[1],".")[1]
            classname = "node."+basename

            # is the class an inlet or an outlet?
            if classname == "node.ContainerInlet":
                self.addInput(NumberInput(self, params['inlet_label']))
            elif classname == "node.ContainerOutlet":
                self.addOutput(NumberOutput(self, params['outlet_label']))
            elif classname == "node.ContainerTitle":
                print "found a title node"
                self.title = params['title']

        print "container title is now:",self.title

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.filename.currentText = d["filename"]
            self.nodeData = d["nodeData"]
            self.connectorData = d["connectorData"]
            self.parseExistingData()
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."
    
    def getParameterDict(self):
        d = {}
        d = Node.getParameterDict(self)
        d["filename"] = self.filename.currentText
        d["nodeData"] = self.nodeData
        d["connectorData"] = self.connectorData
        return d

    def draw(self):


        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        for i in self.inputs:
            i.draw()
        for o in self.outputs:
            o.draw()
        #self.notes.draw()
        glPopMatrix()

        if self.selector.isSelected(self):
            gui.Button.drawHighlight(self)
            gui.Button.draw(self)
        else:
            gui.Button.draw(self)
            gui.Button.drawOutline(self, color_pallet.node_box_outline)

        # gui.Button.draw(self)

        if self.icon:
            ofEnableAlphaBlending()
            glColor3f(1, 1, 1)
            self.icon.draw(self.x+ self.w/2 - 12,self.y + 8)
        if gui.manager.showNames or self.mouseState == gui.MouseState.MOUSE_HOVER or self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            if self.title:
                if self.selector.isSelected(self):
                    apply(glColor3f, color_pallet.node_box_outline_highlight_top)
                else:
                    apply(glColor3f, color_pallet.node_box_text)
                self.font.drawString(self.title,self.x + self.w + 7, self.y + self.h - 34)
                glColor3f(0.6,0.6,0.6)
                self.font.drawString("container", self.x + self.w + 7, self.y + self.h - 18)
            # else:
            #     self.font.drawString(self.label,self.x + self.w + 7, self.y + self.h - 34)
        if self.mouseState == gui.MouseState.MOUSE_HOVER:
            glPushMatrix()
            glTranslatef(self.x, self.y, self.z)
            self.deleteButton.draw()
            glPopMatrix()
        if gui.manager.alignTool and self.mouseState == gui.MouseState.MOUSE_DRAGGING_US:
            apply(ofSetColor, color_pallet.align_tool)
            ofLine(0, self.y, ofGetWidth(), self.y)
            ofLine(self.x, 0, self.x, ofGetHeight())

# ---------------------------------------------------------------------
# ^^ END OF CONTAINER NODE ^^
# ---------------------------------------------------------------------

class ContainerInlet(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "container inlet"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/inlet.png")
        self.addOutput(NumberOutput(self, "number in"))

        self.propertyWindow.w = 400
        self.propertyWindow.h = 150

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("container inlet")
        l.setPosition(10,0)
        l._setW(300)

        self.labelTextfield = gui.TextEntry(self.propertyWindow)
        self.labelTextfield.w = 250
        self.labelTextfield.currentText = "Inlet"
        self.labelTextfield.setPosition(10, 32)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("give your input a unique name")
        l.setPosition(10,46)
        l._setW(300)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.labelTextfield.currentText = d["inlet_label"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."

    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["inlet_label"] = self.labelTextfield.currentText
        return d

    def saySomething(self):
        print "butts"

class ContainerOutlet(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "container outlet"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/outlet.png")
        self.addInput(NumberInput(self, "number out"))

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("container outlet")
        l.setPosition(10,0)
        l._setW(300)

        self.labelTextfield = gui.TextEntry(self.propertyWindow)
        self.labelTextfield.w = 250
        self.labelTextfield.currentText = "Outlet"
        self.labelTextfield.setPosition(10, 32)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("give your output a unique name")
        l.setPosition(10,46)
        l._setW(300)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.labelTextfield.currentText = d["outlet_label"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."

    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["outlet_label"] = self.labelTextfield.currentText
        return d

class ContainerTitle(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "container title"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/container.png")

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("container title")
        l.setPosition(10,0)
        l._setW(300)

        self.labelTextfield = gui.TextEntry(self.propertyWindow)
        self.labelTextfield.w = 250
        self.labelTextfield.currentText = "New Container"
        self.labelTextfield.setPosition(10, 32)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        l.setMessage("give your container a unique name")
        l.setPosition(10,46)
        l._setW(300)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.labelTextfield.currentText = d["title"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."

    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["title"] = self.labelTextfield.currentText
        return d


class PlaySound(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "play sound"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/playsound.png")

        self.addInput(NumberInput(self, "play sound"))
        self.addInput(NumberInput(self, "volume (0-1)"))
        self.addOutput(NumberOutput(self, "done playing"))

        self.propertyWindow.w = 400
        self.propertyWindow.h = 150

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.w = 350
        l.setMessage("play sound")
        l.setPosition(10,0)

        # l = gui.Label(self.propertyWindow)
        # l.w = 400
        # l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)
        # l.setMessage("Select a sound file.")
        # l.setPosition(10, -5)

        self.filename = gui.TextEntry(self.propertyWindow)
        self.filename.w = 180
        self.filename.currentText = "C://"
        self.filename.setPosition(10, 32)

        self.browse = gui.Button(self.propertyWindow)
        self.browse.setLabel("browse...")
        self.browse.callback = self.getFile
        self.browse.showLabel = 1
        self.browse.autoSize()
        self.browse.setPosition(210, 32)
        self.browse.setColor((0.5,0.5,0.5))

    def getFile(self):
        f = gui.getFilenameToOpen()
        self.filename.setText(f)

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.filename.currentText = d["filename"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."

    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["filename"] = self.filename.currentText
        return d


class Counter(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "counter"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/counter.png")

        
        self.addInput(NumberInput(self, "plus event"))
        self.addInput(NumberInput(self, "minus event"))
        self.addInput(NumberInput(self, "increment"))

        self.addOutput(NumberOutput(self, "output"))

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("Counter")
        l.setPosition(10,0)

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        l.setMessage("initial value")
        l.setPosition(10,34)

        self.initial_value = gui.TextEntry(self.propertyWindow)
        self.initial_value.setPosition(105, 40)
        self.initial_value.w = 100
        self.initial_value.currentText = "0"
        self.initial_value.validateAsNumber()

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.initial_value.currentText = `d["init_val"]`
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."

    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["init_val"] = float(self.initial_value.currentText)
        return d

class TimeGraph(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "time graph"
        self.tooltip = node_descriptions.get(self.label)
        self.icon.loadImage("icons/timegraph.png")

        self.addInput(NumberInput(self, "x"))
        self.addInput(NumberInput(self, "y"))
        self.addInput(NumberInput(self, "x increment"))
        self.addInput(NumberInput(self, "y increment"))

        self.propertyWindow.w = 250
        self.propertyWindow.h = 180

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Bold.ttf",14)
        l.setMessage("time graph")
        l.setPosition(10, 0)
        l._setW(300)

        v = 30

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        l.setMessage("x position")
        l.setPosition(10,0 + v)

        # coordinates
        self.x_pos = gui.TextEntry(self.propertyWindow)
        self.x_pos.setPosition(10, 30 + v)
        self.x_pos.w = 100
        self.x_pos.currentText = "0"
        self.x_pos.validateAsNumber()

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        l.setMessage("y position")
        l.setPosition(140,0 + v)

        self.y_pos = gui.TextEntry(self.propertyWindow)
        self.y_pos.setPosition(140, 30 + v)
        self.y_pos.w = 100
        self.y_pos.currentText = "0"
        self.y_pos.validateAsNumber()

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        l.setMessage("width")
        l.setPosition(10,50 + v)

        # width and height
        self.graph_width = gui.TextEntry(self.propertyWindow)
        self.graph_width.setPosition(10, 80 + v)
        self.graph_width.w = 100
        self.graph_width.currentText = "1024"
        self.graph_width.validateAsNumber()

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        l.setMessage("height")
        l.setPosition(140,50 + v)

        self.graph_height = gui.TextEntry(self.propertyWindow)
        self.graph_height.setPosition(140, 80 + v)
        self.graph_height.w = 100
        self.graph_height.currentText = "768"
        self.graph_height.validateAsNumber()

        l = gui.Label(self.propertyWindow)
        l.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        l.setMessage("color (hex)")
        l.setPosition(10,100 + v)

        # color as hex value
        self.hex_color = gui.TextEntry(self.propertyWindow)
        self.hex_color.setPosition(10, 130 + v)
        self.hex_color.w = 100
        self.hex_color.currentText = "FFFFFF"

        self.placePropertyOkay()

    def setParameterDict(self, d):
        try:
            Node.setParameterDict(self, d)
            self.x_pos.currentText = `d["x_pos"]`
            self.y_pos.currentText = `d["y_pos"]`
            self.graph_width.currentText = `d["graph_width"]`
            self.graph_height.currentText = `d["graph_height"]`
            self.hex_color.currentText = d["hex_color"]
        except KeyError:
            print self.label,"had a backwards compatibility issue. Check to make sure all the parameters are correct."

    def getParameterDict(self):
        d = Node.getParameterDict(self)
        d["x_pos"] = float(self.x_pos.currentText)
        d["y_pos"] = float(self.y_pos.currentText)
        d["graph_width"] = float(self.graph_width.currentText)
        d["graph_height"] = float(self.graph_height.currentText)
        d["hex_color"] = self.hex_color.currentText
        return d

class Vector2D(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "vector 2d"
        self.tooltip = node_descriptions.get(self.label)
        # self.icon.loadImage("icons/vec2d.png")

        self.addInput(NumberInput(self, "x"))
        self.addInput(NumberInput(self, "y"))
        self.addInput(NumberInput(self, "x velocity"))
        self.addInput(NumberInput(self, "y velocity"))
        self.addInput(NumberInput(self, "multiplier"))
        self.addOutput(NumberOutput(self, "angle"))
        self.addOutput(NumberOutput(self, "magnitude"))

        self.doSimplePropertyWindow("Outputs the angle and magnitude of a given 2d velocity.")
        self.placePropertyOkay()

class FindColor(Node):

    def __init__(self):
        Node.__init__(self)
        self.label = "find color"
        self.tooltip = node_descriptions.get(self.label)

        self.addInput(ImageInput(self, "image"))
        self.addOutput(ImageOutput(self, "modified image"))

        self.doSimplePropertyWindow("")
        
        
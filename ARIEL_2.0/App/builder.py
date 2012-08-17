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

from OpenGL.GLUT import *

from openframeworks import *

from psl import *
from psl import util
from psl import gui
from psl import fontmanager

# import fonts
import time
import cPickle
import os
import sys

import nodepallet
import node
import color_pallet
import node_descriptions

import random

print "### Running ARIEL Builder v2 ####"

class NodePallet(gui.PSGObject):

    def __init__(self):
        gui.PSGObject.__init__(self)
        self.categories = []
        self.x, self.y = 10, 59
        self.w = 150
        self.ARIEL_label = ofImage()
        self.ARIEL_label.loadImage("icons/ARIEL_label.jpg")
    
    def addCategory(self, c):
        self.categories.append(c)
        self.updateCategoryPositions()
    
    def updateCategoryPositions(self):
        if gui.manager.palletScrollBar.scrollBox.active and self.getTotalHeight() > ofGetHeight() - 103:
            ypos = -gui.manager.palletScrollBar.scrollBox.scroll * (self.getTotalHeight() - (ofGetHeight() - 103))
        elif gui.manager.palletScrollBar.scrollBox.active == False:
            ypos = 0
        else:
            ypos = 0
        for s in self.categories:
            x,y = s.getPosition()
            y = ypos
            s.setPosition(x,y)
            ypos += s.getHeight()

        gui.manager.palletSizeUpdate(self.getTotalHeight())
    
    def handleMouse(self, *args):
        if len(args) == 0 or ((self.x < args[0] < self.x + self.w) and (self.y < args[1] < ofGetHeight() - 44)):
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
                    if apply(c.handleMouse, childArgs):
                        return 1
#        for c in self.categories:
#            c.handleMouse(args)
    
    def draw(self):
        # background of pallet
        apply(glColor3f, color_pallet.tool_pallet_bg)
        glRectf(self.x, self.y, self.x + self.w, ofGetHeight() - 44)

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        for s in self.categories:
            s.draw()
        glPopMatrix()
        #
        glColor3f(0.8,0.8,0.8)
        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex3f(160, 59, 0)
        glVertex3f(160, ofGetHeight() - 44, 0)
        glVertex3f(160, ofGetHeight() - 44, 0)
        glVertex3f(10, ofGetHeight() - 44, 0)
        glEnd()
        #
        apply(glColor3f, color_pallet.background)
        glRectf(0, ofGetHeight() - 44, 160, ofGetHeight())
        glRectf(0, 20, 160, 58)
        #
        glColor3f(1, 1, 1)
        self.ARIEL_label.draw(8, 20)

    def getTotalHeight(self):
        h = 0
        for s in self.categories:
            h += s.getHeight()
        return h

    def resetScroll(self):
        pass
    

class NodeCategory(gui.Button):
        
    def __init__(self,name, parent=None):
        gui.Button.__init__(self, parent)
        self.x = 0
        self.y = 0

        self.w = 110
        self.h = 30

        self.nodes = []
        self.isCollapsed = 1
        self.label = gui.Label(self)
        self.label.setMessage(name)
        self.label.setColor((0.2, 0.2, 0.2))
        self.label.setPosition(14,-17)
        self.name = name
        self.callback = self.toggleCollapsed
        self.space = 28
    
    def collapse(self):
        self.isCollapsed = 1
        self.parent.updateCategoryPositions()
    
    def expand(self):
        self.isCollapsed = 0
        self.parent.updateCategoryPositions()        
    
    def toggleCollapsed(self):
        if self.isCollapsed:
            self.expand()
        else:
            self.collapse()
    
    def addNode(self, n):
        n = NodePalletIcon(n[0], n[1], parent=self)
        self.nodes.append(n)
        apply(n.setPosition,self.getSlot(len(self.nodes)))
 # size of rounded rect behind node image!
        n.w = 24
        n.h = 24
    
    def getSlot(self, n):
        x = (18, 80)
        space = 28
        n-=1
        return (x[n%1],36+space*(n/1))
    
    def getHeight(self):
        if self.isCollapsed:
            return 30
        else:
            return 40 + self.space * len(self.nodes)
    
    def handleMouse(self, *args):
#        print "HM",args,self.x, self.y, self.w, self.h
        c = [self]
        c.extend(args)
#        print c
        if apply(gui.Button.handleMouse, c):
            return 1

        if self.isCollapsed:
            return 0

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
                if apply(c.handleMouse, childArgs):
                    return 1
    

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x+10, self.y+10, self.z)
        # glColor3f(1,1,1)
        apply(glColor3f, color_pallet.tool_pallet_shapes)
        glPushMatrix()
        glRotatef(-90*(self.isCollapsed),0,0,1)
        glBegin(GL_POLYGON)
        glVertex3f(-7, -5, 0)
        glVertex3f(7, -5, 0)
        glVertex3f(0, 7, 0)
        glEnd()
        glPopMatrix()
        glBegin(GL_LINES)
        glVertex3f(-10,-10,0)
        glVertex3f(140,-10,0)
        glEnd()
        self.label.draw()

        if not self.isCollapsed:
            for n in self.nodes:
                n.draw()

        
        glPopMatrix()
    

class NodePalletIcon(gui.Button):

    def __init__(self, label, icon, parent=None):
        gui.Button.__init__(self, parent)
        ofDisableDataPath()
        self.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",9)
#        print "loaded",self.font
        self.label = label
        self.tooltip = node_descriptions.get(self.label)
        self.icon = ofImage()
        if not self.icon.loadImage(icon):
            print "Failed to load",icon
        
        self.nodeToCreate = nodepallet.getNodeFromLabel(label)
        self.downCallback = self.handlePress
    
    def handlePress(self):
        self.createNode()
        gui.manager.selectionManager.deselectAll()
        self.releaseMouse()
    
    def releaseMouse(self):
        self.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_ELSEWHERE
    
    def createNode(self):
        newNode = self.nodeToCreate()
        x,y = gui.manager.getMouseLocation()
        newNode.x = x - newNode.w / 2
        newNode.y = y - newNode.h / 2
        newNode.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_US
        newNode.draggable = True
    
    def draw(self):
        glPushMatrix()
        glTranslatef(-14,-14,0)
        if self.mouseState == gui.MouseState.MOUSE_HOVER:
            gui.Button.drawHighlight(self)
            gui.manager.setHoverNode(self)
        gui.Button.draw(self)
        gui.Button.drawOutline(self, (0, 0, 0))
        glColor3f(1, 1, 1)
        ofEnableAlphaBlending()
        self.icon.draw(self.x,self.y)
        apply(glColor3f, color_pallet.node_box_text)
        self.font.drawString(self.label,self.x + self.w + 5, self.y + self.h/2 + 3)
        glPopMatrix()
        


class PalletScrollBar(gui.Button):
    def __init__(self, pallet):
        gui.Button.__init__(self)
        self.pallet = pallet
        gui.manager.setPalletScrollBar(self)

        self.x = 160
        self.y = 59
        self.w = 10
        self.h = ofGetHeight() - 103

        self.scrollBox = self.Box(self, self.x, self.y, self.w, self.h)

        self.mx, self.my, self.pmx, self.pmy = 0, 0, 0, 0

        self.hovering, self.dragging = False, False

    def draw(self):
        apply(glColor3f, color_pallet.scrollbar_bg)
        glRectf(self.x, self.y, self.x + self.w, self.y + self.h)
        self.scrollBox.draw(self.hovering)

    # ----

    def mouseMoved(self, *args):
        if self.scrollBox.isMouseOver(args[0], args[1]):
            self.hovering = True
        else:
            self.hovering = False

    def mousePressed(self, *args):
        self.pmx, self.pmy = args[0], args[1]
        # perhaps here you could state that if we aren't hovering but we tap
        # the bar, it will increment down a bit (or something)

    def mouseDragged(self, *args):
        if self.hovering:
            self.dragging = True
            self.scrollBox.drag(args[1], self.pmy)
        self.pmx, self.pmy = args[0], args[1]

    def mouseReleased(self, *args):
        self.dragging = False

    def handleMouse(self, *args):
        pass

    # ----

    def resize(self, h):
        self.h = h - 103
        self.scrollBox.resizeBox(self.pallet.getTotalHeight())

    def sizeUpdate(self, h):
        self.scrollBox.resizeBox(h)

    class Box:
        def __init__(self, parent, x, y, w, h):
            self.x, self.y, self.w, self.h = x, y, w, h
            self.parent = parent
            self.active = False
            self.scroll = 0

        def resizeBox(self, totalheight):
            if totalheight > self.parent.h:
                ratio = self.parent.h / float(totalheight)
                self.h = self.parent.h * ratio
                self.active = True
                self.y = self.parent.y + (self.scroll * (self.parent.h - self.h))
            else:
                self.active = False
                self.y = self.parent.y
                self.scroll = 0
                #self.parent.pallet.resetScroll

        def drag(self, y, py):
            self.y += y - py
            self.y = ofClamp(self.y, self.parent.y, self.parent.y + self.parent.h - self.h)
            self.scroll = (self.y - self.parent.y) / (self.parent.h - self.h)
            self.parent.pallet.updateCategoryPositions()

        def draw(self, hover):
            if self.active:
                #print "should be drawing scrollbar"
                if hover:
                    apply(glColor3f, color_pallet.scrollbar_box_hover)
                else:
                    apply(glColor3f, color_pallet.scrollbar_box)
                glRectf(self.x, self.y, self.x + self.w, self.y + self.h)
            else:
                pass

        def isMouseOver(self, mx, my):
            if self.x < mx < self.x + self.w and self.y < my < self.y + self.h:
                return True
            return False

class SaveBanner(gui.PSGObject):
    def __init__(self):
        gui.PSGObject.__init__(self)
        self.img = ofImage()
        self.img.loadImage("icons/saved.png")
        self.alpha = 0
        self.initialTime = time.time()
        self.x, self.y = ofGetWidth()/2 - self.img.getWidth()/2, ofGetHeight()/2 - self.img.getHeight()/2
        self.w = self.img.getWidth()
        self.h = self.img.getHeight()

    def draw(self):
        elapsedTime = time.time() - self.initialTime
        if elapsedTime < 1:
            glColor4f(0.5, 0.5, 0.5, elapsedTime)
            self.img.draw(self.x, self.y)
        elif 1 <= elapsedTime < 2:
            glColor4f(0.5, 0.5, 0.5, 1)
            self.img.draw(self.x, self.y)
        elif 2 <= elapsedTime < 3:
            glColor4f(0.5, 0.5, 0.5, 1 - (elapsedTime - 2))
            self.img.draw(self.x, self.y)
        else:
            gui.manager.objects.remove(self)

class AboutWindow(gui.Button):
    def __init__(self, close_callback):
        gui.Button.__init__(self)
        self.img = ofImage()
        self.img.loadImage("icons/ARIEL_about.png")
        self.x, self.y = ofGetWidth()/2 - self.img.getWidth()/2, ofGetHeight()/2 - self.img.getHeight()/2
        self.w = self.img.getWidth()
        self.h = self.img.getHeight()
        self.downCallback = self.goAway
        self.closeCallback = close_callback

    def draw(self):
        glColor3f(1, 1, 1)
        self.img.draw(self.x, self.y)

    def goAway(self):
        self.closeCallback()
        gui.manager.objects.remove(self)


#------------------------------------------------------------
#------------------------------------------------------------       TAG CONTROLLER
#------------------------------------------------------------


class TagController:
    def __init__(self, parent):
        self.parent = parent
        self.font = fontmanager.manager.getFont("Frutiger-Roman.ttf",11)
        self.offset = 0
        for i in range(len(gui.manager.objects)):
            if isinstance(gui.manager.objects[i], node.Node):
                self.offset = i
                break
        print self.offset
        self.nodes = filter(lambda o: isinstance(o,node.Node),gui.manager.objects)
        self.selected = None
        self.tags = []
        for i, n in enumerate(self.nodes):
            self.tags.append(Tag(self, n, i))

    def requestSwap(self, old_pos, new_pos):
        if new_pos >= len(self.nodes):
            return
        self.selected = None

        node_to_move = gui.manager.objects.pop(old_pos + self.offset)
        gui.manager.objects.insert(new_pos + self.offset, node_to_move)

        self.nodes, self.tags = [], []
        self.nodes = filter(lambda o: isinstance(o,node.Node),gui.manager.objects)
        for i, n in enumerate(self.nodes):
            self.tags.append(Tag(self, n, i))

    def draw(self):
        glColor4f(0, 0, 0, 0.2)
        glRectf(0, 0, ofGetWidth(), ofGetHeight())
        glColor3f(0.6, 0.6, 0.6)
        glRectf(0, 0, ofGetWidth(), 20)
        glColor3f(0, 0, 0)
        self.font.drawString("You are currently in Order Edit Mode. Press Escape to exit.", 10, 15)
        for t in self.tags:
            t.draw()

    def setSelected(self, t):
        if self.selected:
            self.selected.deselect()
        self.selected = t

    def deselect(self):
        if self.selected:
            self.selected.deselect()
            self.selected = None

    def mouseMoved(self, *args):
        x, y = args[0], args[1]

    def mousePressed(self, *args):
        x, y = args[0], args[1]
        for t in self.tags:
            if t.mousePressed(x, y):
                return

    def keyPressed(self, key):
        if key == 27:
            self.parent.showOrdering()
        elif self.selected:
            self.selected.keyPressed(key)

class Tag:
    def __init__(self, parent, node, pos):
        self.parent = parent
        self.font = parent.font
        self.node = node
        self.x, self.y = node.x, node.y + node.h/2
        self.pos = pos
        self.selected = False
        self.numberBuffer = ""

    def draw(self):
        if self.selected:
            glColor3f(1, 1, 1)
            ofCircle(self.x, self.y, 15)
        glColor3f(1.0, 0.38, 0.22)
        ofCircle(self.x, self.y, 12)

        if self.selected:
            glColor4f(1, 1, 1, 0.3)
            self.font.drawString(str(self.pos), self.x - self.font.stringWidth(str(self.pos))/2.0 - 1, self.y + 6)
            glColor3f(0, 0, 0)
            self.font.drawString(str(self.numberBuffer), self.x - self.font.stringWidth(str(self.pos))/2.0 - 1, self.y + 6)
        else:
            glColor3f(1, 1, 1)
            self.font.drawString(str(self.pos), self.x - self.font.stringWidth(str(self.pos))/2.0 - 1, self.y + 6)

    def deselect(self):
        self.selected = False
        self.numberBuffer = ""

    def mousePressed(self, x, y):
        if ofDistSquared(self.x, self.y, x, y) < 144:
            self.parent.setSelected(self)
            self.selected = True
            return 1
        return 0

    def keyPressed(self, key):
        if 48 <= key <= 57: # number keys
            self.numberBuffer += chr(key)
        elif key == 127: # backspace
            self.numberBuffer = self.numberBuffer[:-1]
        elif key == 13: # return
            if self.numberBuffer == "":
                self.parent.deselect()
            else:
                self.parent.requestSwap(self.pos, int(self.numberBuffer))


#------------------------------------------------------------
#------------------------------------------------------------       TAG CONTROLLER
#------------------------------------------------------------




class ArielBuilder(ofBaseApp):

    def setup(self):
        ofDisableDataPath()
        ofSetEscapeQuitsApp(0)
        ofSetFrameRate(60)
        ofNoFill()
        ofEnableSmoothing()
        util.fixPath()

        self.nodePallet = NodePallet()
        gui.manager.setPallet(self.nodePallet)
        self.palletScrollBar = PalletScrollBar(self.nodePallet)

        # used for saving!
        self.lastFilename = ""
        ofSetWindowTitle("New File (unsaved)")

        w = gui.MenuBar()
        # --
        i = gui.MenuItem("File",None)
        w.addItem(i)
        e = gui.MenuEntry("New",self.fileNew)
        i.addItem(e)
        e = gui.MenuEntry("Open...",self.loadGraph)
        i.addItem(e)
        e = gui.MenuEntry("Save (opt+s)",self.saveOver)
        i.addItem(e)
        e = gui.MenuEntry("Save as...",self.exportGraph)
        i.addItem(e)
        # e = gui.MenuEntry("Close",self.close)
        # i.addItem(e)
        # e = gui.MenuEntry("Export...",self.exportGraph)
        # i.addItem(e)
        e = gui.MenuEntry("Quit",self.close)
        i.addItem(e)
        # --
        i = gui.MenuItem("Edit")
        w.addItem(i)

        e = gui.MenuEntry("Undo (opt+z)",self.doUndo)
        i.addItem(e)
        e = gui.MenuEntry("Redo (opt+y)",self.doRedo)
        i.addItem(e)

        e = gui.MenuEntry("Copy (opt+c)", self.copySelectedNodes)
        i.addItem(e)
        e = gui.MenuEntry("Paste (opt+v)", self.pasteSelectedNodes)
        i.addItem(e)

        # align tool for nice blue lines
        e = gui.MenuEntry("Align On/Off", self.alignOnOff)
        i.addItem(e)

        # menu item for showing names
        e = gui.MenuEntry("Show/Hide Names", self.showNamesOnOff)
        i.addItem(e)

        e = gui.MenuEntry("Order Edit Mode", self.showOrdering)
        i.addItem(e)
        
        i = gui.MenuItem("About")
        w.addItem(i)
        e = gui.MenuEntry("About ARIEL...",self.doAbout)
        i.addItem(e)
        
        
        # w = gui.Label()
        # w.w = 160
        # w.font = fontmanager.getFont("Frutiger-Bold.ttf",16)
        # w.setMessage("ARIEL Builder")
        # w.setColor(color_pallet.node_box_text)
        # w.setPosition(10, 30)

        # self.ARIEL_label = ofImage()
        # self.ARIEL_label.loadImage("icons/ariel_labels/logo5.jpg")

        w = gui.Button()
        w.setLabel("Run")
        w.showLabel = 1
        w.h = 22
        w.setPosition(799,727)
        w.callback = self.exportAndRunGraph

        self.runButton = w

        self.fullscreen = gui.ComboBox()
        self.fullscreen.setChoices(("in window","fullscreen"))
        self.fullscreen.currentChoice = 0
        self.fullscreen.setPosition(907, 727)

        gui.undo.setStoreCallback(self.doUndoCheckpoint)

        self.nodePallet.setPosition(10, 60)
        sensors = NodeCategory("sensors", self.nodePallet)
        sensors.expand()
        for n in nodepallet.sensorNodes:
            sensors.addNode(n)
        self.nodePallet.addCategory(sensors)
        
        tracking = NodeCategory("tracking", self.nodePallet)
        for n in nodepallet.trackingNodes:
            tracking.addNode(n)
        self.nodePallet.addCategory(tracking)
        
        display = NodeCategory("display", self.nodePallet)
        for n in nodepallet.displayNodes:
            display.addNode(n)
        self.nodePallet.addCategory(display)

        mathLogic = NodeCategory("math & logic", self.nodePallet)
        for n in nodepallet.mathLogicNodes:
            mathLogic.addNode(n)
        self.nodePallet.addCategory(mathLogic)
        
        general = NodeCategory("general", self.nodePallet)
        for n in nodepallet.generalNodes:
            general.addNode(n)
        self.nodePallet.addCategory(general)

        containers = NodeCategory("containers", self.nodePallet)
        for n in nodepallet.containerNodes:
            containers.addNode(n)
        self.nodePallet.addCategory(containers)
        
        arduino = NodeCategory("arduino", self.nodePallet)
        for n in nodepallet.arduinoNodes:
            arduino.addNode(n)
        self.nodePallet.addCategory(arduino)
        
        user = NodeCategory("user nodes", self.nodePallet)
        for n in nodepallet.userNodes:
            user.addNode(n)
        self.nodePallet.addCategory(user)

        # buffer for copy+paste
        self.nodesToCopy = None

        # font for bottom left tooltips
        self.tooltipFont = fontmanager.manager.getFont("Frutiger-Roman.ttf",10)

        # some visual scrolling accompaniment
        self.scroll_pointer = ofImage()
        self.scroll_pointer.loadImage("icons/scroll_pointer.png")
        self.mX, self.mY = 0,0

        # flag for "Saved" popup image
        self.didSave = False

        # this will store an instance of the order_interface
        self.tagController = None

        gui.manager.createPropertyDrawer()

        self.aboutWindowIsShowing = False
    
    def doAbout(self):

        # propertyWindow = gui.Window()
        # helpLabel = gui.Label(propertyWindow)
        # propertyWindow.w = 300
        # propertyWindow.h = 150

        # helpLabel.setMessage("ARIEL version 1.6, May 2012")
        # helpLabel.setPosition(25,10)
        # helpLabel._setW(280)

        # propertyOkay = gui.Button(propertyWindow)
        # propertyOkay.setLabel("okay")
        # propertyOkay.callback = propertyWindow.hide
        # propertyOkay.showLabel = 1
        # propertyOkay.setColor((0.5,0.5,0.5))
        # propertyOkay.w = 50
        # propertyOkay.h = 25
        # propertyOkay.x = 239
        # propertyOkay.y = 110
        # propertyWindow.show()
        if self.aboutWindowIsShowing == False:
            AboutWindow(self.aboutWindowClose)
            self.aboutWindowIsShowing = True

    def aboutWindowClose(self):
        self.aboutWindowIsShowing = False

    
    def doUndo(self):
        try:
            del(gui.undo.undoState[-1])
        except:
            pass
        state = gui.undo.undo()
        if not state:
            gui.doPopupMessage("There is no further undo information.")
            return
        self.loadGraph(state)
    

    def doRedo(self):
        try:
            del(gui.undo.undoState[-1])
        except:
            pass
        state = gui.undo.redo()
        if not state:
            gui.doPopupMessage("There is no further redo information.")
            return
        print "redo state",state
        self.loadGraph(state)
    
    def fileNew(self):
        self.lastFilename = ""
        ofSetWindowTitle("New File (unsaved)")
        #print "lastFilename got erased"
        node.connector.clearAll()
        gui.manager.objects = filter(lambda f: not isinstance(f, node.Node),  gui.manager.objects)
    
    def close(self):
        ofQuit()
        # sys.exit()

    #--------------------------------------------------------------------------------------
    # SKETCH LOADING
    #--------------------------------------------------------------------------------------
    
    def loadGraph(self, state=None):

      node.connector.isLoadingFromFile = 1
        
      try:
        if not state:
          fname = gui.getFilenameToOpen()
          self.lastFilename = fname
          if fname == "":
            return
          fm = open(fname)
          data = cPickle.load(fm)
          fm.close()
          
        else:
          data = cPickle.loads(state)
#        print "loading data"
#        print data
        nodeData, connectorData = data
        index = {}

        node.connector.clearAll()
        # filter out (delete) all existing nodes
        gui.manager.objects = filter(lambda f: not isinstance(f, node.Node),  gui.manager.objects)

        for n in nodeData:
            #print n
            name, inputs, outputs, params, layout = n
            basename = string.splitfields(string.split(name)[1],".")[1]
            classname = "node."+basename
            try:
                newNode = eval(classname + "()")
            except:
                #print "failed to load class",classname
                classname = basename
                #print "trying user scripts"
                for c in nodepallet.labelsToNodes.values():
                    # print "checking",c.__name__
                    if c.__name__ == classname:
                        #print "we have a match!"
                        newNode = c()
                        #print "class loaded"
            newNode.x, newNode.y, newNode.w, newNode.h = layout
            #print newNode
            newNode.setParameterDict(params)

            # if isinstance(newNode, node.Container):
            #     newNode.parseFile()

            #print inputs,outputs
            for i in inputs+outputs:
                index[i[1]] = (newNode,i[0])
        for conn in connectorData:
            f,t = conn
            fromNode, fromConn = index[f]
            toNode, toConn = index[t]
            fromConn = fromNode.getOutputByName(fromConn)
            #print "looking for",toConn,"in",toNode
            toConn = toNode.getInputByName(toConn)
            #print "connections",fromConn,toConn
            fromConn.connect(toConn)

        # is there a better spot for this?
        # change splitter's output type to match the current input type (if there is one)
        for n in gui.manager.objects:
            if isinstance(n, node.Splitter):
                if n.inputs[0]:
                    n.switchOutputClass(n.inputs[0].getParent())

      except:
        print "load failed."
        import traceback
        traceback.print_exc()
        gui.doPopupMessage("Load failed.","Please make sure you are trying to load a valid ARIEL scene.")

      node.connector.isLoadingFromFile = 0
      ofSetWindowTitle(self.lastFilename)
    
    def exportAndRunGraph(self):
        print "Running Sketch:", time.ctime()

        tempName = self.lastFilename
        # if there is a container present, we need to create a buffer file so that the container node
        # can get expanded without completely ruining the current sketch.
        if self.hasContainers():
            tempFile = self.exportGraph(asString=1)
            self.stitchContainers()
            self.exportGraph("scene_with_container.ariel")
            self.runGraph("scene_with_container.ariel")
            self.loadGraph(tempFile)
        # otherwise, run things as normal.
        else:
            self.exportGraph("scene.ariel")
            self.runGraph("scene.ariel")
        self.lastFilename = tempName
        if tempName == "":
            ofSetWindowTitle("New File (unsaved)")
        else:
            ofSetWindowTitle(self.lastFilename)

    def hasContainers(self):
        for o in gui.manager.objects:
            if isinstance(o, node.Container):
                return True
        return False

    # def stitchContainers(self):
    #     for i, o in enumerate(gui.manager.objects):
    #         if isinstance(o, node.Container):
    #             self.nodesFromContainer(o, i)

    def stitchContainers(self):
        for o in gui.manager.objects:
            if isinstance(o, node.Container):
                self.nodesFromContainer(o)
                o.delete()

    def nodesFromContainer(self, o):
        nodeData, connectorData = o.nodeData, o.connectorData
        index = {}
        inlets = []
        outlets = []
        # listOfActualNodes = []
        for n in nodeData:
            #print n
            name, inputs, outputs, params, layout = n
            basename = string.splitfields(string.split(name)[1],".")[1]
            classname = "node."+basename
            try:
                newNode = eval(classname + "()")
            except:
                #print "failed to load class",classname
                classname = basename
                #print "trying user scripts"
                for c in nodepallet.labelsToNodes.values():
                    print "checking",c.__name__
                    if c.__name__ == classname:
                        #print "we have a match!"
                        newNode = c()
                        #print "class loaded"
            if isinstance(newNode, node.ContainerInlet):
                inlets.append(newNode)
            elif isinstance(newNode, node.ContainerOutlet):
                outlets.append(newNode)
            
            newNode.x, newNode.y, newNode.w, newNode.h = layout
            #print newNode
            newNode.setParameterDict(params)
            #print inputs,outputs
            for i in inputs+outputs:
                index[i[1]] = (newNode,i[0])

            # if not isinstance(newNode, node.ContainerTitle) and not isinstance(newNode, node.ContainerInlet) and not isinstance(newNode, node.ContainerOutlet):
            #     listOfActualNodes.append(newNode)

        outlet_parents = []
        for conn in connectorData:
            f,t = conn
            fromNode, fromConn = index[f]
            toNode, toConn = index[t]
            fromConn = fromNode.getOutputByName(fromConn)
            toConn = toNode.getInputByName(toConn)
            # save the outputs that are connecting to the ContainerOutlets for later
            for out in outlets:
                if out.inputs[0] == toConn:
                    outlet_parents.append(fromConn)
            fromConn.connect(toConn)

        # now we have to switch the container's existing connections to the
        # nodes that will be replacing it.
        
        for i, inputObject in enumerate(o.inputs):
            # parentOutput is the output currently connected to the container's input (inputObject)
            parentOutput = inputObject.getParent()
            # disconnect the output so we can put it somewhere else
            if parentOutput != None:
                parentOutput.disconnect()
            # get the new input that the parentOutput will be connecting to
            newInputToConnectTo = inlets[i].outputs[0].connection
            # connect them.
            if newInputToConnectTo != None and parentOutput != None:
                parentOutput.connect(newInputToConnectTo)

        outlet_parents.reverse()
        for i, outputObject in enumerate(o.outputs):
            # destination is the input that we'll be patching into
            destination = outputObject.connection
            # print "destination = outputObject.connection; type =", outputObject.connection
            # parentOutput = outlets[i].inputs[0].getParent()
            parentOutput = outlet_parents[i]
            # print "outlets[i].inputs[0].getParent() =", parentOutput
            if parentOutput != None and destination != None:
                parentOutput.disconnect()
                parentOutput.connect(destination)

        # delete the inlet and outlet nodes that we no longer need
        for i in inlets:
            i.delete()
        for out in outlets:
            out.delete()
        # delete the container node
        # o.delete()
        # print "list of nodes:", listOfActualNodes
        # here we insert the list of all the newly created nodes at container_index,
        # keeping them synced with the Order Edit Mode settings
        # for l in listOfActualNodes:
        #     gui.manager.objects.remove(l)

        # gui.manager.objects.insert(container_index, listOfActualNodes)

    
    def runGraph(self,fname):
        args = ""
        if self.fullscreen.currentChoice == 1:
            args += " fullscreen"
        if os.system(sys.executable+" player.py "+fname+args):
            gui.doPopupMessage("Scene exited abnormally.","Check the Terminal window for additional error information.")
    
    def doUndoCheckpoint(self):
        str = self.exportGraph(asString=1)
        if str:
            gui.undo.store(str)
    
#--------------------------------------------------------------------------------------
# SKETCH SAVING
#--------------------------------------------------------------------------------------

    def exportGraph(self,fname=None,asString=0):
      try:
        if not asString:
          if not fname:
            fname = gui.getFilenameToSave()
            if fname == "":
                self.didSave = False
                return
        nodes = filter(lambda o: isinstance(o,node.Node),gui.manager.objects)
        nodes = map(lambda o: o.getExportData(), nodes)
        data = (nodes, node.connector.getExportData())
        data = cPickle.dumps(data)
        if asString:
            return data
        f = open(fname,"w")
        f.write(data)
        f.close()
        if fname != "scene.ariel":
            print "sketch saved to", fname
        # save filename for later, update title of window to reflect last saved name
        self.lastFilename = fname
        ofSetWindowTitle(self.lastFilename)
        self.didSave = True
      except:
        print "export failed."
        import traceback
        traceback.print_exc()
        gui.doPopupMessage("Export failed.")

    def saveOver(self,fname=None,asString=0):
      #print "saveover:", self.lastFilename
      fname = self.lastFilename
      try:
        if not asString:
          if not fname:
            fname = gui.getFilenameToSave()
            if fname == "":
                return
        nodes = filter(lambda o: isinstance(o,node.Node),gui.manager.objects)
        nodes = map(lambda o: o.getExportData(), nodes)
        data = (nodes, node.connector.getExportData())
        data = cPickle.dumps(data)
        if asString:
            return data
        f = open(fname,"w")
        f.write(data)
        f.close()
        print "sketch saved to", fname
        self.lastFilename = fname
        ofSetWindowTitle(self.lastFilename)
        self.didSave = True
      except:
        print "export failed."
        import traceback
        traceback.print_exc()
        gui.doPopupMessage("Export failed.")


    def alignOnOff(self):
        gui.manager.alignTool = not gui.manager.alignTool

    def showNamesOnOff(self):
        gui.manager.showNames = not gui.manager.showNames

    def copySelectedNodes(self):
        self.nodesToCopy = []
        if gui.manager.selectionManager.selectedObjects:
            for o in gui.manager.selectionManager.selectedObjects:
                self.nodesToCopy.append(o)
            print self.nodesToCopy
        else:
            print "tried to copy but nothing was selected!"

    def alignOnOff(self):
        gui.manager.alignTool = not gui.manager.alignTool

    def showNamesOnOff(self):
        gui.manager.showNames = not gui.manager.showNames

    def copySelectedNodes(self):
        self.nodesToCopy = []
        if gui.manager.selectionManager.selectedObjects:
            for o in gui.manager.selectionManager.selectedObjects:
                self.nodesToCopy.append(o)
            print self.nodesToCopy
        else:
            print "tried to copy but nothing was selected!"

    def pasteSelectedNodes(self):
        if self.nodesToCopy:
            gui.manager.selectionManager.deselectAll()
            for o in self.nodesToCopy:
                nodeClass = nodepallet.getNodeFromLabel(o.label)
                newNode = nodeClass()
                newNode.copyAttributes(o)
                x,y = o.getPosition()
                newNode.setPosition(x + 43, y + 43)
                gui.manager.selectionManager.select(newNode)
                newNode.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_US
        else:
            print "there is nothing in the ARIEL clipboard to paste!"

    def duplicateViaOptionDrag(self):
        # copy the selection into temp list
        # deselect
        # do copy/paste routine
        copyList = []
        for o in gui.manager.selectionManager.selectedObjects:
            copyList.append(o)
            o.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_ELSEWHERE
        gui.manager.selectionManager.deselectAll()
        for o in copyList:
            nodeClass = nodepallet.getNodeFromLabel(o.label)
            newNode = nodeClass()
            newNode.copyAttributes(o)
            x,y = o.getPosition()
            newNode.setPosition(x,y)
            gui.manager.selectionManager.select(newNode)
            newNode.mouseState = gui.MouseTweaker.MOUSE_DRAGGING_US

    def checkForOptionKeyCommands(self, key):
        mod = glutGetModifiers()
        # option key
        if mod == 4:
            if key == 115:
                # s
                print "save!"
                self.saveOver()
                if self.didSave:
                    SaveBanner()
                    self.didSave = False
            elif key == 114:
                # r
                # print "running sketch!"
                self.exportAndRunGraph()
                return
            elif key == 99:
                # c
                self.copySelectedNodes()
            elif key == 118:
                # v
                self.pasteSelectedNodes()
                gui.undo.checkpoint()
            elif key == 122:
                # z
                self.doUndo()
            elif key == 97:
                # a
                gui.manager.selectAll()
            elif key == 100:
                # d
                gui.manager.selectionManager.deselectAll()
        # option and shift
        elif mod == 5:
            if key == 83:
                self.exportGraph()
                if self.didSave:
                    SaveBanner()
                    self.didSave = False
            elif key == 90:
                self.doRedo()

    def showOrdering(self):
        if self.tagController:
            self.tagController = None
        else:
            self.tagController = TagController(self)

    # ----------------------------------------------------------
    # ALL THE INPUTS
    # ----------------------------------------------------------

    def keyPressed(self, key):
        if self.tagController == None:
            self.checkForOptionKeyCommands(key)
            if key == 8:
                gui.manager.deleteAllSelected()
                gui.manager.selectionManager.deselectAll()
                gui.undo.checkpoint()
            else:
                gui.focus.keyPressed(key)
        else:
            self.tagController.keyPressed(key)
        # if key == ord('m'):
        #     for i in gui.manager.selectionManager.selectedObjects[0].inputs:
        #         print i.getParent()
        # elif key == ord('n'):
        #     for o in gui.manager.selectionManager.selectedObjects[0].outputs:
        #         print o
        # elif key == ord('b'):
        #     print gui.manager.selectionManager.selectedObjects[0]

    def mouseMoved(self, *args):
        if self.tagController == None:
            apply(gui.manager.handleMouse,args)
            apply(gui.manager.palletScrollBar.mouseMoved,args)
        else:
            apply(self.tagController.mouseMoved, args)
    
    def mouseDragged(self, *args):
        if self.tagController == None:
            if gui.manager.isRightClickScrolling == True:
                self.mX, self.mY = args[0], args[1]
                gui.manager.rightClickScroll(args[0], args[1])
            else:
                apply(gui.manager.handleMouse,args)
                apply(gui.manager.palletScrollBar.mouseDragged,args)
    
    def mousePressed(self, *args):
        if self.tagController == None:
        # if OPTION key is down:
            if glutGetModifiers() == 4:
                # if left click
                if args[2] == 0:
                    
                    apply(gui.manager.handleMouse,args)
                    if gui.manager.mouseOnNode:
                        gui.manager.selectionManager.select(gui.manager.mouseOnNode)
                        self.duplicateViaOptionDrag()
                        # gui.undo.checkpoint()
                    pass
                # if right click
                else:
                    self.mX, self.mY = args[0], args[1]
                    gui.manager.startRightClickScroll(args[0], args[1])
            # regular clicks without option key press
            else:
                gui.undo.checkpoint()
                apply(gui.manager.handleMouse,args)
                apply(gui.manager.palletScrollBar.mousePressed,args)
        else:
            apply(self.tagController.mousePressed, args)
    
    def mouseReleased(self, *args):
        if self.tagController == None:
            if gui.manager.isRightClickScrolling == True:
                gui.manager.isRightClickScrolling = False
            else:
                apply(gui.manager.handleMouse,args)
                apply(gui.manager.palletScrollBar.mouseReleased,args)

    def windowResized(self, w, h):
        self.runButton.setPosition(w-225, h - 44)
        self.fullscreen.setPosition(w-117, h - 44)
        gui.manager.windowResized(w, h)
    
    def update(self):
        pass
    
    def draw(self):
        # select + load the projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # set projection matrix to orthographic @ window width and height
        glOrtho(0, ofGetWidth(), ofGetHeight(), 0, 0, 1)
        # change the viewport to reflect window width/height
        glViewport(0, 0, ofGetWidth(), ofGetHeight())
        glDisable(GL_DEPTH_TEST)
        # select + load the model matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        # a lil pixel magic
        glTranslatef(0.2, 0.1, 0)
        # clear the background with the bg color
        glClearColor(0.9, 0.9, 0.9, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        # apply(ofBackground, color_pallet.byteColor(color_pallet.background))
        gui.manager.draw()

        glColor3f(1, 1, 1)
        # self.ARIEL_label.draw(0, 0)
        # self.ARIEL_label.draw(8, 20)

        if gui.manager.hoverNode:
            ofSetColor(50, 50, 50)
            self.tooltipFont.drawString(gui.manager.hoverNode.tooltip, 10, ofGetHeight() - 20)

        # add a lil pointer arrow under the mouse so you know when you're scrolling
        if gui.manager.isRightClickScrolling:
            self.scroll_pointer.draw(self.mX - 15, self.mY - 15)

        if self.tagController:
            self.tagController.draw()
        # if self.ordering:
        #     o_sorted = filter(lambda o: isinstance(o,node.Node),gui.manager.objects)
        #     for i in range(len(o_sorted)):
        #         o_sorted[i].drawOrderNumber(i)
    

util.smoothAndLovely()
util.setupWindow(1200,800, OF_WINDOW)
#print "A",os.getcwd()
ofRunApp(ArielBuilder())



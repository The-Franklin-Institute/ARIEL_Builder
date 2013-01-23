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

import node
import os
import sys

labelsToNodes = {}
# sensors
# labelsToNodes["camera"] = node.Camera
labelsToNodes["camera"] = node.SimpleCamera
# labelsToNodes["kinect"] = node.Kinect
labelsToNodes["kinect"] = node.SimpleKinect
# labelsToNodes["firmata"] = node.Firmata
labelsToNodes["mouse input"] = node.MouseInput
labelsToNodes["key input"] = node.KeyboardInput
labelsToNodes["gui button"] = node.GUIButton
# tracking
labelsToNodes["blob tracking"] = node.BlobTracking
labelsToNodes["blob filter"] = node.BlobFilter
labelsToNodes["glyph tracking"] = node.GlyphTracking
labelsToNodes["glyph filter"] =  node.GlyphFilter
labelsToNodes["bg differencing"] = node.BackgroundDifferencing
labelsToNodes["find color"] = node.FindColor
# display
labelsToNodes["video"] =  node.Video
labelsToNodes["simulator data"] = node.DataDisplay
labelsToNodes["curve display"] = node.CurveDisplay
labelsToNodes["data collector"] = node.DataCollector
labelsToNodes["time graph"] = node.TimeGraph
labelsToNodes["image"] =  node.Image
labelsToNodes["image mask"] = node.ImageMask
labelsToNodes["collada anim."] =  node.ColladaAnimation
labelsToNodes["draw code"] = node.DrawCode
# math + logic
labelsToNodes["parameter"] =  node.Parameter
labelsToNodes["math"] = node.Mathematics
labelsToNodes["conditional"] =  node.Conditional
labelsToNodes["expression builder"] = node.ExpressionBuilder
labelsToNodes["var set"] = node.VariableSetter
labelsToNodes["var get"] = node.VariableGetter
labelsToNodes["velocity"] =  node.Velocity
labelsToNodes["vector 2d"] = node.Vector2D
labelsToNodes["counter"] = node.Counter
labelsToNodes["number event"] = node.NumberEvent
labelsToNodes["button"] = node.LogicButton
labelsToNodes["toggle"] = node.LogicToggle
labelsToNodes["gate"] = node.LogicGate
labelsToNodes["mono selector"] = node.MonoSelector
labelsToNodes["combiner"] = node.Combiner
labelsToNodes["button delay"] = node.ButtonDelay
# generalNodes
labelsToNodes["splitter"] =  node.Splitter 
labelsToNodes["play sound"] = node.PlaySound
labelsToNodes["startup"] =  node.Startup
labelsToNodes["delay"] =  node.Delay
labelsToNodes["print"] = node.PrintInput
# labelsToNodes["collision"] =  node.Collision
labelsToNodes["OSC receive"] = node.OSCReceive
labelsToNodes["OSC send"] = node.OSCSend
# labelsToNodes["OSC filter"] = node.OSCFilter
# container nodes
labelsToNodes["container"] = node.Container
labelsToNodes["container inlet"] = node.ContainerInlet
labelsToNodes["container outlet"] = node.ContainerOutlet
labelsToNodes["container title"] = node.ContainerTitle
# arduino
labelsToNodes["Arduino"] = node.Arduino
labelsToNodes["Arduino+PWM"] = node.ArduinoPWM
# labelsToNodes["rotary encoders"] = node.RotaryEncoders


def getNodeFromLabel(l):
    if labelsToNodes.has_key(l):
        return labelsToNodes[l]
    return node.Node

def getSlot(n):
    x = (34, 117)
    space = 80
    n-=1
    return (x[n%2],92+space*(n/2))

sensorNodes = []
trackingNodes = []
displayNodes = []
mathLogicNodes = []
generalNodes = []
containerNodes = []
userNodes = []
arduinoNodes = []
#
x,y = 0,0 # the parameters below that use x and y no longer do anything.
#
sensorNodes.append(("camera", "icons/camera.png", x, y))
# sensorNodes.append(("camera", "icons/camera.png", x, y))
# sensorNodes.append(("firmata", "icons/serial.png", x, y))
sensorNodes.append(("kinect", "icons/kinect.png", x, y))
# sensorNodes.append(("kinect","icons/kinect.png", x, y))
sensorNodes.append(("mouse input", "icons/mouse.png", x, y))
sensorNodes.append(("key input", "icons/keyinput.png", x, y))
sensorNodes.append(("gui button", "icons/button.png", x, y))
#
trackingNodes.append(("blob tracking", "icons/blob.png", x, y))
trackingNodes.append(("blob filter", "icons/filter.png", x, y))
trackingNodes.append(("glyph tracking", "icons/glyph.png", x, y))
trackingNodes.append(("glyph filter","icons/filter.png", x, y))
trackingNodes.append(("bg differencing", "icons/bgdif.png", x, y))
trackingNodes.append(("find color", "icons/bgdif.png", x, y))
#
displayNodes.append(("image", "icons/image.png", x, y))
displayNodes.append(("image mask", "icons/imagemask.png", x, y))
displayNodes.append(("video", "icons/video.png", x, y))
displayNodes.append(("data collector", "icons/datacollector.png", x, y))
displayNodes.append(("time graph", "icons/timegraph.png", x, y))
displayNodes.append(("simulator data", "icons/simulator.png", x, y))
displayNodes.append(("curve display", "icons/curve.png", x, y))
displayNodes.append(("collada anim.","icons/collada.png", x, y))
displayNodes.append(("draw code","icons/drawcode.png",x,y))
#
mathLogicNodes.append(("parameter","icons/parameter.png", x, y))
mathLogicNodes.append(("math","icons/math.png", x, y))
mathLogicNodes.append(("conditional","icons/conditional.png", x, y))
mathLogicNodes.append(("expression builder", "icons/expr.png", x, y))
mathLogicNodes.append(("var set", "icons/set.png", x, y))
mathLogicNodes.append(("var get", "icons/get.png", x, y))
mathLogicNodes.append(("velocity","icons/velocity.png", x, y))
mathLogicNodes.append(("vector 2d", "icons/velocity.png", x, y))
mathLogicNodes.append(("counter", "icons/counter.png", x, y))
mathLogicNodes.append(("number event", "icons/numberevent.png", x, y))
mathLogicNodes.append(("button", "icons/button.png", x, y))
mathLogicNodes.append(("toggle", "icons/toggle.png", x, y))
mathLogicNodes.append(("gate", "icons/gate.png", x, y))
mathLogicNodes.append(("mono selector", "icons/monoselector.png", x, y))
mathLogicNodes.append(("combiner", "icons/combiner.png", x, y))
mathLogicNodes.append(("button delay", "icons/delay.png", x, y))
#
generalNodes.append(("splitter","icons/splitter.png", x, y))
generalNodes.append(("play sound", "icons/playsound.png", x, y))
generalNodes.append(("startup","icons/power.png", x, y))
generalNodes.append(("delay","icons/delay.png", x, y))
generalNodes.append(("print","icons/print.png", x, y))
# generalNodes.append(("collision", "icons/collision.png", x, y))
generalNodes.append(("OSC receive","icons/oscr.png", x, y))
generalNodes.append(("OSC send","icons/oscs.png", x, y))
# generalNodes.append(("OSC filter","icons/filter.png", x, y))
#
containerNodes.append(("container", "icons/container.png", x, y))
containerNodes.append(("container inlet", "icons/inlet.png", x ,y))
containerNodes.append(("container outlet", "icons/outlet.png", x, y))
containerNodes.append(("container title", "icons/container.png", x, y))
#
arduinoNodes.append(("Arduino","icons/arduino.png", x, y))
arduinoNodes.append(("Arduino+PWM", "icons/arduino.png", x, y))
# arduinoNodes.append(("rotary encoders","icons/user.png", x, y))

import arielplugin

arielplugin.Node = node.Node

#print "prepping for plugins..."

for obj in dir(node):
    c = getattr(node, obj)
    try:
        if issubclass(c,node.NodeInput) or issubclass(c,node.NodeOutput):
            exec "arielplugin."+c.__name__+ " = node."+c.__name__
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
        #try:
            #print dir(mod)
            #print mod.arielplugin
        #except:
            #print "print failed"
        continue
    #print "looking for classes"
    for o in dir(mod):
        c = getattr(mod,o)
        if hasattr(c,"ARIELCLASS"):
            #print o,"is an ariel class"
            labelsToNodes[c.ARIELCLASS] = c
            #x,y = getSlot(len(nodes)+1)
            userNodes.append((c.ARIELCLASS, "icons/user.png",x,y))
        else:
            #print o,"is not an ariel class"
            pass

#print "plugin load complete"
    
    

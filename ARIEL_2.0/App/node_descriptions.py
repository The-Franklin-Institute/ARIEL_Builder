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

d = {}

def get(label):
	if label in d:
		return d[label]
	else:
		return "No information to display."

d["to be named"] = "No information to display."
# sensors
d["camera"] = "Camera grabs a webcam image."
# d["simple camera"] = "Simple Camera grabs an image from a webcam."
d["kinect"] = "Kinect grabs an XBox Kinect image."
# d["simple kinect"] = "Simple Kinect, used for grabbing an image from an XBox Kinect."
# d["firmata"] = "Firmata serial connection. Use Arduino node instead!"
d["mouse input"] = "Mouse Input provides the mouse position and status of both mouse buttons."
d["key input"] = "Key Input sends the ASCII (number) value of a key when it is pressed."
d["gui button"] = "GUI Button provides an on-screen button within your ARIEL sketch."
# tracking
d["blob tracking"] = "Blob Tracking detects blobs within an image. Access the blob information using Blob Filter."
d["blob filter"] = "Blob Filter accesses blobs detected by Blob Tracking and sorts them by size (0 being the largest)."
d["glyph tracking"] = "Glyph Tracking detects glyphs within an image. Access the glyph information using Glyph Filter."
d["glyph filter"] = "Glyph Filter accesses glyphs detected by Glyph Tracking and sorts them by ID number."
d["bg differencing"] = "Background Differencing saves a frame and subtracts subsequent frames from it, detecting the differences."
# display
d["video"] = "Load a video file and play it."
d["simulator data"] = "Simulator Data displays vector lists and/or scalar data."
d["curve display"] = "Curve Display draws lines using vector lists. Use with Data Collector."
d["data collector"] = "Data Collector saves X,Y data as a list of points. It only collects data when the trigger input is set to 1."
d["image"] = "Image displays image data, either from a file or from another node."
d["image mask"] = "Image Mask is used to mask out a portion of the input image using a second image."
d["collada anim."] = "Collada Animation loads and displays a 3d file."
d["draw code"] = "Draw Code runs a piece of code within the draw loop, allowing for programmatic visuals."
# math + logic
d["parameter"] = "Parameter outputs a number."
d["math"] = "Math performs one of the following operations on two numbers: addition, subtraction, multiplication, division, or modulus."
d["conditional"] = "Conditional outputs either a 1 or a 0 based on whether or not a condition has been met among two numbers."
d["expression builder"] = "Expression Builder performs a mathematical expression using up to four inputs. It can also run one line of Python code."
d["var set"] = "Var Set creates and gives a value to a global variable."
d["var get"] = "Var Get grabs the current value of a variable."
d["counter"] = "Counter adds or subtracts by an increment (1 by default) whenever it receives an event."
d["number event"] = "Number Event sends out a specific number when it receives a 1 as an input."
d["button"] = "Button Sends a single 1 for each series of 1s it receives."
d["toggle"] = "Toggle switches its output between 1 and 0 each time it receives a 1 as an input."
d["gate"] = "Gate sends one of two inputs through its output based on the value of the control input."
d["mono selector"] = "Mono Selector sends a continuous 1 to the output specified by the control input."
d["combiner"] = "Combiner continuously sends the last value it receives."
d["button delay"] = "Button Delay pauses a signal for a specified amount of time."
# generalNodes
d["splitter"] = "Splitter duplicates its input to four different outputs."
d["play sound"] = "Play Sound loads a sound file and plays it whenever it is sent a 1. Volume is set to 1 by default."
d["startup"] = "Startup sends a single 1 when the sketch starts running."
d["delay"] = "Delay pauses a signal once for a specified amount of time when the sketch starts running."
d["print"] = "Print displays the input in the Terminal window each frame. Print nodes can be named to differentiate between several of them."
d["collision"] = "Collision looks at two sets of polygons to see if they overlap."
d["velocity"] = "Velocity calculates the velocity of x and y inputs, though these inputs do not necessarily need to be coordinates."
d["OSC receive"] = "OSC Receive listens for tagged OSC messages at the specified host and port number."
d["OSC send"] = "OSC Send transmits tagged OSC messages over a specified host and port number."
d["OSC filter"] = "OSC Filter grabs the specified index of an incoming OSC message."
# container nodes
d["container"] = "Container loads a .ariel file as a node, including inputs and outputs if they were specified."
d["container inlet"] = "Container Inlet provides an input to a sketch when it is loaded as a container."
d["container outlet"] = "Container Outlet provides an output to a sketch when it is loaded as a container."
d["container title"] = "Container Title provides a custom title to a sketch when it is loaded as a container."
# arduino
d["Arduino"] = "Arduino allows communication to and from an Arduino that has Firmata loaded on it."
d["rotary encoders"] = ""
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

# this file stores the color information. the colors are RGB floats from 0-1.

def floatColor(r, g, b, a=None):
	if a:
		return r/255.0, g/255.0, b/255.0, a/255.0
	else:
		return r/255.0, g/255.0, b/255.0

def byteColor(c):
	return int(c[0]*255), int(c[1]*255), int(c[2]*255)

# NODE INPUTS AND OUTPUTS

# dark blue
default_output = floatColor(59, 82, 97)
default_input = floatColor(12, 41, 53)

# light blue
number_output = floatColor(50, 157, 164)
number_input = floatColor(0, 88, 101)

# red
image_output = floatColor(201, 112, 94)
image_input = floatColor(177, 38, 42)

# the circle that fades in when you hover over an arrow
node_output_highlight = floatColor(98, 98, 98)


# GENERAL NODERY

# text color for most labels
node_box_text = (0.3, 0.3, 0.3)

node_box_bg = (0.6, 0.6, 0.6)
node_box_outline = (0, 0, 0)

node_box_bg_highlight = (0.6, 0.6, 0.6)

# top to bottom gradient for node highlight (currently red)
node_box_outline_highlight_top = floatColor(212, 77, 77)
node_box_outline_highlight_bottom = floatColor(212, 77, 77, 128)

# top to bottom gradient for node
node_top = (0.6, 0.6, 0.6)
node_bottom = (0.3, 0.3, 0.3)

align_tool = (50, 157, 164)


# ENVIRONMENT

background = (0.9, 0.9, 0.9)
text_highlight = (0.7, 1, 1, 0.3)

scrollbar_bg = (0.7, 0.7, 0.7)
scrollbar_box = (0.4, 0.4, 0.4)
scrollbar_box_hover = (0.5, 0.5, 0.5)

menubar_top = (0.5, 0.5, 0.5)
menubar_bottom = (0.4, 0.4, 0.4)

tool_pallet_bg = (0.8, 0.8, 0.8)
tool_pallet_shapes = (0.4, 0.4, 0.4)
tool_pallet_title = (0.2, 0.2, 0.2)

# property drawer background
property_drawer = (0.6, 0.6, 0.6)

# open/close button of property drawer
drawer_button_top = (0.6, 0.6, 0.6)
drawer_button_bottom = (0.6, 0.6, 0.6)
drawer_button_top_hover = (0.6, 0.6, 0.6)
drawer_button_bottom_hover = (0.7, 0.7, 0.7)

# highlight for drop-down menus
selection_highlight = floatColor(212, 77, 77, 200)

button_highlight = (0.7, 0.7, 0.7)
button_down = (0.4, 0.4, 0.4)
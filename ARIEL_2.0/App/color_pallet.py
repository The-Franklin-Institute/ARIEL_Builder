# this file stores the color information. the colors are RGB floats from 0-1.

def floatColor(r, g, b, a=None):
	if a:
		return r/255.0, g/255.0, b/255.0, a/255.0
	else:
		return r/255.0, g/255.0, b/255.0

def byteColor(c):
	return int(c[0]*255), int(c[1]*255), int(c[2]*255)

# NODE INPUTS AND OUTPUTS

default_output = floatColor(59, 82, 97)
default_input = floatColor(12, 41, 53)
# default_output = (1.0, 0.38, 0.22)
# default_input = (0.3, 0.3, 0.3)

number_output = floatColor(50, 157, 164)
number_input = floatColor(0, 88, 101)
# number_output = (0.0, 0.64, 0.53)
# number_input = (0.14, 0.31, 0.28)

image_output = floatColor(201, 112, 94)
image_input = floatColor(177, 38, 42)
# image_output = (0.55, 0.76, 0.48)
# image_input = (0.45, 0.66, 0.38)

# node_output_highlight = floatColor(212, 77, 77)
node_output_highlight = floatColor(98, 98, 98)


# GENERAL NODERY

node_box_text = (0.3, 0.3, 0.3)

node_box_bg = (0.6, 0.6, 0.6)
node_box_outline = (0, 0, 0)

node_box_bg_highlight = (0.6, 0.6, 0.6)

node_box_outline_highlight_top = floatColor(212, 77, 77)

node_box_outline_highlight_bottom = floatColor(212, 77, 77, 128)

node_top = (0.6, 0.6, 0.6)
node_bottom = (0.3, 0.3, 0.3)


# ENVIRONMENT
# 
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

property_drawer = (0.6, 0.6, 0.6)

drawer_button_top = (0.8, 0.8, 0.8)
drawer_button_bottom = (0.6, 0.6, 0.6)

drawer_button_top = (0.6, 0.6, 0.6)
drawer_button_bottom = (0.6, 0.6, 0.6)
drawer_button_top_hover = (0.6, 0.6, 0.6)
drawer_button_bottom_hover = (0.7, 0.7, 0.7)

selection_highlight = floatColor(212, 77, 77, 200)

button_highlight = (0.7, 0.7, 0.7)
button_down = (0.4, 0.4, 0.4)
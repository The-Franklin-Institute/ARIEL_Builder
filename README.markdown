ARIEL BUILDER v2.0
==================

ARIEL Builder is a visual programming language for prototyping augmented reality interactive software, developed as part of The Franklin Institute's ARIEL Grant.

For a pre-packaged installer file, visit http://www.fi.edu/ariel/software.php

It is licensed with a Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
It makes use of OpenFrameworks, distributed under the MIT License.

Direct questions and comments to kstetz@fi.edu; bugs should be reported as Issues on GitHub.  
https://github.com/The-Franklin-Institute/ARIEL_Builder

* * *

System Requirements
===================

This is currently Mac-Only.

* OS X 10.6 or higher
* Minimum 2Gb RAM
* Takes 300Mb hard drive space

* * *

Development
===============

This software was produced by:

The Franklin Institute  
Philadelphia, Pennsylvania, USA  
www.fi.edu/ariel  
Lead Programmer: Kyle Stetz
 
Patten Studio  
Brooklyn, New York, USA  
www.pattenstudio.com  
Lead Programmer: James Patten  

The ARIEL project received support from the National Science Foundation under Grant No. 0741659. Any opinions, findings, and conclusions or recommendations expressed in this material are those
of the author(s) and do not necessarily reflect the views of the National Science Foundation.

* * *

Technical Details
=================

ARIEL Builder is programmed completely in Python, making use of the OpenFrameworks library (which has been compiled to run from Python using SWIG). It runs within an OpenGL context; this allows access to both OpenFrameworks tools and native OpenGL functions in the same space. The context is running in C++, making it several times faster than using equivalent PyOpenGL calls.

While there is no official developer documentation yet, take a look at `builder.py` (environment), `node.py` (nodes), and `player.py` (node functions) to get started. All GUI tools are located in `ARIEL_2.0/App/python/lib/python2.6/site-packages/psl/gui.py`
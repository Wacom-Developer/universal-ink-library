# -*- coding: utf-8 -*-
"""
Ink Data
========
Contains all data structures which are relevant for representing the visual appearance:

- `Stroke`- Structure to  store the ink geometry of a stroke,
- `Brush` - Structures to store vector and raster brush configurations

In general, the WILL engine differentiates between:

- raster particle - called **Raster Ink**,
- and, vector polygon rendering - called **Vector Ink**.

The geometric primitives computed by the Ink Geometry Pipeline are
paths containing control points that are interpolated using a Catmull-Rom spline.

Vector Ink (shape-filling technique) is a solid color technique for rasterizing strokes that have variable width.
This method is more limited in terms of expressiveness, but performs better than more complex rendering techniques.
It is suitable for typical scalable vector graphics usages or handwriting applications.

Raster Ink renders strokes using overlapping particles. This technique allows you to build more expressive tools
(such as crayon, pencil, or watercolor brushes) by controlling several rendering parameters.

"""

__all__ = ['brush', 'strokes']

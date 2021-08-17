# -*- coding: utf-8 -*-
"""
   Helpers
   =======
   The  helpers are simple functions to support with:

    - Catmull-Rom splines
    - Extracting text and named entities from Ink Model
    - Iterate over the Ink Tree
"""

__all__ = ['spline', 'text_extractor', 'treeiterator', 'policy']

from uim.model.helpers import spline
from uim.model.helpers import text_extractor
from uim.model.helpers import treeiterator
from uim.model.helpers import policy

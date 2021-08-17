# -*- coding: utf-8 -*-
"""
Parser
=======
This package contains different parsers for ink formats:

- Universal Ink Model (v3.0.0 and v3.1.0)
- Wacom Ink Layer Language (WILL)

"""
__all__ = ['decoder', 'uim', 'will']

from uim.codec.parser import will
from uim.codec.parser import uim
from uim.codec.parser import decoder

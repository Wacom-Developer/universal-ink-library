# -*- coding: utf-8 -*-
"""
Decoder classes
===============
This package contains all decoders for the different versions of the Universal Ink Model:

- Version 3.0.0
- Version 3.1.0
"""
__all__ = ['base', 'decoder_3_0_0', 'decoder_3_1_0']


from uim.codec.parser.decoder import base
from uim.codec.parser.decoder import decoder_3_0_0
from uim.codec.parser.decoder import decoder_3_1_0


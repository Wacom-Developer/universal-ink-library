# -*- coding: utf-8 -*-
"""
Context
=======
This package contains structures to handle the encoding an decoding context, with information such as:

- Version of format
- Encoding scheme
- Encoding and decoding context for caching stroke information

"""
__all__ = ['decoder', 'encoder', 'scheme', 'version']

from uim.codec.context import scheme
from uim.codec.context import encoder
from uim.codec.context import version
from uim.codec.context import decoder


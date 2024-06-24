# -*- coding: utf-8 -*-
"""
Package for the UIM model.
This package contains the data model for the UIM.
"""
from uim.model.base import UUIDIdentifier
__all__ = ['helpers', 'inkdata', 'inkinput', 'semantics',  'ink', 'UUIDIdentifier']

import uim.model.helpers
import uim.model.inkdata
import uim.model.inkinput
import uim.model.semantics
import uim.model.ink

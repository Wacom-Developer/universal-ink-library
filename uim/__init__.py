# -*- coding: utf-8 -*-
"""
    Universal Ink Library
    =====================
    This Python library is designed to work with Universal Ink Models (UIM).

    The UIM defines a language-neutral and platform-neutral data model for representing and manipulating
    digital ink data captured using an electronic pen or stylus, or using touch input.

    The main aspects of the UIM are:

    - Interoperability of ink-based data models by defining a standardized interface with other systems
    - Biometric data storage mechanism
    - Spline data storage mechanism
    - Rendering configurations storage mechanism
    - Ability to compose spline/raw-input based logical trees, which are contained within the ink model
    - Portability, by enabling conversion to common industry standards
    - Extensibility, by enabling the description of ink data related semantic metadata
    - Standardized serialization mechanism

    This reference document defines a RIFF container and Protocol Buffers schema for serialization of ink models as well
    as a standard mechanism to describe relationships between different parts of the ink model, and/or between parts of
    the ink model and external entities.
"""
__author__ = "Markus Weber"
__copyright__ = "Copyright 2021 Wacom. All rights reserved."
__credits__ = ["Markus Weber"]
__license__ = "Apache 2.0 License"
__version__ = "1.0.4"
__maintainer__ = ["Markus Weber"]
__email__ = "markus.weber@wacom.com"
__status__ = "alpha"

__all__ = ['codec', 'model', 'utils', '__version__']

from uim import model
from uim import codec
from uim import utils

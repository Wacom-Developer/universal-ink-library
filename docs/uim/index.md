Module uim
==========
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

Sub-modules
-----------
* uim.codec
* uim.model
* uim.utils
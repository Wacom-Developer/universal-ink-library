# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: will-message-format.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='will-message-format.proto',
  package='WacomInkFormat',
  syntax='proto2',
  serialized_options=b'H\003',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x19will-message-format.proto\x12\x0eWacomInkFormat\"\xef\x02\n\x0eParticlesPaint\x12\r\n\x05shape\x18\x01 \x03(\x0c\x12\x12\n\x07spacing\x18\x02 \x01(\x02:\x01\x32\x12\x15\n\nscattering\x18\x03 \x01(\x02:\x01\x30\x12?\n\x08rotation\x18\x04 \x01(\x0e\x32\'.WacomInkFormat.ParticlesPaint.Rotation:\x04NONE\x12\x0c\n\x04\x66ill\x18\x05 \x03(\x0c\x12\x14\n\tfillWidth\x18\x06 \x01(\x02:\x01\x34\x12\x15\n\nfillHeight\x18\x07 \x01(\x02:\x01\x34\x12\x1c\n\rrandomizeFill\x18\x08 \x01(\x08:\x05\x66\x61lse\x12K\n\x12\x63ompositeOperation\x18\t \x01(\x0e\x32\".WacomInkFormat.CompositeOperation:\x0bSOURCE_OVER\x12\n\n\x02id\x18\x64 \x01(\r\"0\n\x08Rotation\x12\x08\n\x04NONE\x10\x00\x12\n\n\x06RANDOM\x10\x01\x12\x0e\n\nTRAJECTORY\x10\x02\"\xac\x02\n\x04Path\x12\x19\n\x0estartParameter\x18\x01 \x01(\x02:\x01\x30\x12\x17\n\x0c\x65ndParameter\x18\x02 \x01(\x02:\x01\x31\x12\x1b\n\x10\x64\x65\x63imalPrecision\x18\x03 \x01(\r:\x01\x32\x12\x10\n\x04\x64\x61ta\x18\x04 \x03(\x11\x42\x02\x10\x01\x12\x17\n\x0bstrokeWidth\x18\x05 \x03(\x11\x42\x02\x10\x01\x12\x17\n\x0bstrokeColor\x18\x06 \x03(\x11\x42\x02\x10\x01\x12\x13\n\x0bstrokePaint\x18\x07 \x01(\r\x12!\n\x19strokeParticlesRandomSeed\x18\x08 \x01(\r\x12K\n\x12\x63ompositeOperation\x18\t \x01(\x0e\x32\".WacomInkFormat.CompositeOperation:\x0bSOURCE_OVER\x12\n\n\x02id\x18\x64 \x01(\r*\xfa\x01\n\x12\x43ompositeOperation\x12\x08\n\x04\x43OPY\x10\x01\x12\x0f\n\x0bSOURCE_OVER\x10\x02\x12\x14\n\x10\x44\x45STINATION_OVER\x10\x03\x12\x13\n\x0f\x44\x45STINATION_OUT\x10\x07\x12\x0b\n\x07LIGHTER\x10\x0b\x12\x13\n\x0f\x44IRECT_MULTIPLY\x10\x0c\x12!\n\x1d\x44IRECT_INVERT_SOURCE_MULTIPLY\x10\r\x12\x11\n\rDIRECT_DARKEN\x10\x0e\x12\x12\n\x0e\x44IRECT_LIGHTEN\x10\x0f\x12\x14\n\x10\x44IRECT_SUBSTRACT\x10\x10\x12\x1c\n\x18\x44IRECT_REVERSE_SUBSTRACT\x10\x11\x42\x02H\x03'
)

_COMPOSITEOPERATION = _descriptor.EnumDescriptor(
  name='CompositeOperation',
  full_name='WacomInkFormat.CompositeOperation',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='COPY', index=0, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SOURCE_OVER', index=1, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DESTINATION_OVER', index=2, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DESTINATION_OUT', index=3, number=7,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='LIGHTER', index=4, number=11,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DIRECT_MULTIPLY', index=5, number=12,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DIRECT_INVERT_SOURCE_MULTIPLY', index=6, number=13,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DIRECT_DARKEN', index=7, number=14,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DIRECT_LIGHTEN', index=8, number=15,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DIRECT_SUBSTRACT', index=9, number=16,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='DIRECT_REVERSE_SUBSTRACT', index=10, number=17,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=719,
  serialized_end=969,
)
_sym_db.RegisterEnumDescriptor(_COMPOSITEOPERATION)

CompositeOperation = enum_type_wrapper.EnumTypeWrapper(_COMPOSITEOPERATION)
COPY = 1
SOURCE_OVER = 2
DESTINATION_OVER = 3
DESTINATION_OUT = 7
LIGHTER = 11
DIRECT_MULTIPLY = 12
DIRECT_INVERT_SOURCE_MULTIPLY = 13
DIRECT_DARKEN = 14
DIRECT_LIGHTEN = 15
DIRECT_SUBSTRACT = 16
DIRECT_REVERSE_SUBSTRACT = 17


_PARTICLESPAINT_ROTATION = _descriptor.EnumDescriptor(
  name='Rotation',
  full_name='WacomInkFormat.ParticlesPaint.Rotation',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NONE', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='RANDOM', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='TRAJECTORY', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=365,
  serialized_end=413,
)
_sym_db.RegisterEnumDescriptor(_PARTICLESPAINT_ROTATION)


_PARTICLESPAINT = _descriptor.Descriptor(
  name='ParticlesPaint',
  full_name='WacomInkFormat.ParticlesPaint',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='shape', full_name='WacomInkFormat.ParticlesPaint.shape', index=0,
      number=1, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='spacing', full_name='WacomInkFormat.ParticlesPaint.spacing', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(2),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='scattering', full_name='WacomInkFormat.ParticlesPaint.scattering', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rotation', full_name='WacomInkFormat.ParticlesPaint.rotation', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='fill', full_name='WacomInkFormat.ParticlesPaint.fill', index=4,
      number=5, type=12, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='fillWidth', full_name='WacomInkFormat.ParticlesPaint.fillWidth', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(4),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='fillHeight', full_name='WacomInkFormat.ParticlesPaint.fillHeight', index=6,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(4),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='randomizeFill', full_name='WacomInkFormat.ParticlesPaint.randomizeFill', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=True, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='compositeOperation', full_name='WacomInkFormat.ParticlesPaint.compositeOperation', index=8,
      number=9, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=2,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='id', full_name='WacomInkFormat.ParticlesPaint.id', index=9,
      number=100, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _PARTICLESPAINT_ROTATION,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=46,
  serialized_end=413,
)


_PATH = _descriptor.Descriptor(
  name='Path',
  full_name='WacomInkFormat.Path',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='startParameter', full_name='WacomInkFormat.Path.startParameter', index=0,
      number=1, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='endParameter', full_name='WacomInkFormat.Path.endParameter', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=True, default_value=float(1),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='decimalPrecision', full_name='WacomInkFormat.Path.decimalPrecision', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=2,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='WacomInkFormat.Path.data', index=3,
      number=4, type=17, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\020\001', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='strokeWidth', full_name='WacomInkFormat.Path.strokeWidth', index=4,
      number=5, type=17, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\020\001', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='strokeColor', full_name='WacomInkFormat.Path.strokeColor', index=5,
      number=6, type=17, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\020\001', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='strokePaint', full_name='WacomInkFormat.Path.strokePaint', index=6,
      number=7, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='strokeParticlesRandomSeed', full_name='WacomInkFormat.Path.strokeParticlesRandomSeed', index=7,
      number=8, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='compositeOperation', full_name='WacomInkFormat.Path.compositeOperation', index=8,
      number=9, type=14, cpp_type=8, label=1,
      has_default_value=True, default_value=2,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='id', full_name='WacomInkFormat.Path.id', index=9,
      number=100, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=416,
  serialized_end=716,
)

_PARTICLESPAINT.fields_by_name['rotation'].enum_type = _PARTICLESPAINT_ROTATION
_PARTICLESPAINT.fields_by_name['compositeOperation'].enum_type = _COMPOSITEOPERATION
_PARTICLESPAINT_ROTATION.containing_type = _PARTICLESPAINT
_PATH.fields_by_name['compositeOperation'].enum_type = _COMPOSITEOPERATION
DESCRIPTOR.message_types_by_name['ParticlesPaint'] = _PARTICLESPAINT
DESCRIPTOR.message_types_by_name['Path'] = _PATH
DESCRIPTOR.enum_types_by_name['CompositeOperation'] = _COMPOSITEOPERATION
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ParticlesPaint = _reflection.GeneratedProtocolMessageType('ParticlesPaint', (_message.Message,), {
  'DESCRIPTOR' : _PARTICLESPAINT,
  '__module__' : 'will_message_format_pb2'
  # @@protoc_insertion_point(class_scope:WacomInkFormat.ParticlesPaint)
  })
_sym_db.RegisterMessage(ParticlesPaint)

Path = _reflection.GeneratedProtocolMessageType('Path', (_message.Message,), {
  'DESCRIPTOR' : _PATH,
  '__module__' : 'will_message_format_pb2'
  # @@protoc_insertion_point(class_scope:WacomInkFormat.Path)
  })
_sym_db.RegisterMessage(Path)


DESCRIPTOR._options = None
_PATH.fields_by_name['data']._options = None
_PATH.fields_by_name['strokeWidth']._options = None
_PATH.fields_by_name['strokeColor']._options = None
# @@protoc_insertion_point(module_scope)

# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from enum import Enum

WILL_PROTOBUF_ENCODING: str = 'latin1'

# Universal Ink v3.1.0 Constants
RIFF_HEADER: bytes = b'RIFF'
"""RIFF header string"""
UIM_HEADER: bytes = b'UINK'
"""Universal Ink Model file header."""
HEAD_HEADER: bytes = b'HEAD'
"""Header string"""
DATA_HEADER: bytes = b'DATA'
"""Data header string"""
PROPERTIES_HEADER: bytes = b'PRPS'
"""Bytes header for properties chunk"""
INPUT_DATA_HEADER: bytes = b'INPT'
"""Bytes header for input data chunk"""
BRUSHES_HEADER: bytes = b'BRSH'
"""Bytes header for brushes chunk"""
INK_DATA_HEADER: bytes = b'INKD'
"""Bytes header for ink data chunk"""
KNOWLEDGE_HEADER: bytes = b'KNWG'
"""Bytes header for knowledge graph chunk"""
INK_STRUCTURE_HEADER: bytes = b'INKS'
"""Bytes header for ink structure chunk"""
# Constants
CHUNK_DESCRIPTION: int = 8
"""Size of each description chunk in UIM v3.1.0 """
CHUNK_ID_BYTES_SIZE: int = 4
"""Size of the chunk id in UIM v3.1.0 """
SIZE_BYTE_SIZE: int = 4
"""Size of the size bytes in UIM v3.1.0 """
PADDING: bytes = b'\x00'
"""Padding byte"""
RESERVED: bytes = b'\x00'
"""Reserved byte"""


class ContentType(Enum):
    """"Enum of RIFF chunk content types."""
    BINARY = b'\x00'
    """Binary encoding of content, binary/octet-stream."""
    PROTOBUF = b'\x01'
    """Protobuf encoding of content, application/protobuf."""
    JSON = b'\x02'
    """JSON encoding of content, application/json."""
    TEXT = b'\x03'
    """Text encoding of content, text/plain."""


class CompressionType(Enum):
    """Enum of RIFF chunk supported compression types."""
    NONE = b'\x00'
    """Compression not applied"""
    ZIP = b'\x01'
    """ZIP compression for particular chunk"""
    LZMA = b'\x02'
    """LZMA compression for particular chunk"""


class MimeTypes(object):
    """Mime types for ink formats."""
    UNIVERSAL_INK_MODEL: str = "application/vnd.wacom-ink.model"  # Mime type for Universal Ink Models.
    WILL3_DOCUMENT: str = "application/vnd.wacom-will3.document"  # Mime type for WILL 3 documents.
    WILL2_FILE_FORMAT: str = "application/vnd.wacom-will2.document"  # Mime type for WILL 2 documents.
    WILL2_STROKES_FORMAT: str = "application/vnd.wacom-will2.strokes"  # Mime type for WILL 2 strokes


class FileExtension(object):
    """File extension of ink content files."""
    JSON_FORMAT_EXTENSION: str = '.json'
    """JSON file encoding."""
    UIM_JSON_FORMAT_EXTENSION: str = '.uim.json'
    """UIM JSON file encoding."""
    UIM_BINARY_FORMAT_EXTENSION: str = '.uim'
    """UIM binary encoding."""
    INKML_FORMAT_EXTENSION: str = '.inkml'
    """InkML encoding."""
    WILL_FORMAT_EXTENSION: str = '.will'
    """Wacom Ink Layer Language (WILL) file encoding."""

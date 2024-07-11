# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom Authors. All Rights Reserved.
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
import ctypes
import io
import logging
import os
from chunk import Chunk
from io import BytesIO
from pathlib import Path
from typing import Tuple, Union

from uim.codec.base import RIFF_HEADER, UIM_HEADER, HEAD_HEADER
from uim.codec.parser.base import Parser, FormatException, SupportedFormats
from uim.codec.parser.decoder.decoder_3_0_0 import UIMDecoder300
from uim.codec.parser.decoder.decoder_3_1_0 import UIMDecoder310
from uim.model.ink import InkModel

# Create the Logger
logger: logging.Logger = logging.getLogger(__name__)


class UIMParser(Parser):
    """
    UIMParser
    =========

    Parser for Universal Ink Model data codec (UIM).
    The parser is able to parse UIM files in version 3.0.0 and 3.1.0.

    Examples
    --------
    >>> from uim.codec.parser.uim import UIMParser
    >>> from uim.model.ink import InkModel
    >>> parser: UIMParser = UIMParser()
    >>> ink_model: InkModel = parser.parse('../ink/uim_3.1.0/5) Cell Structure 1 (3.1 delta).uim')

    See also
    --------
    ´WILL2Parser´ - Parser for WILL files
    """

    @staticmethod
    def __parse_version__(stream: BytesIO) -> Tuple[int, SupportedFormats]:
        """
        Parses the version of the UIM file.

        Parameters
        ----------
        stream: BytesIO
            Stream of the UIM file

        Returns
        -------
        Tuple[int, SupportedFormats]
            Size of the head and the supported format

        Raises
        ------
        FormatException
            Raises if the file is not an UIM file.
        """
        head: bytes = stream.read(4)
        if head != UIM_HEADER:
            raise FormatException('Not an Universal Ink Model File.')
        if stream.read(4) != HEAD_HEADER:
            raise FormatException('Header missing.')
        size_head = ctypes.c_uint32(int.from_bytes(stream.read(4), byteorder='little')).value
        version_major = int.from_bytes(stream.read(1), byteorder='big')
        version_minor = int.from_bytes(stream.read(1), byteorder='big')
        version_patch = int.from_bytes(stream.read(1), byteorder='big')
        logger.debug(f'UIM Version: {version_major}.{version_minor}.{version_patch}')
        if version_major == 3 and version_minor == 0 and version_patch == 0:
            return size_head, SupportedFormats.UIM_VERSION_3_0_0
        if version_major == 3 and version_minor == 1 and version_patch == 0:
            return size_head, SupportedFormats.UIM_VERSION_3_1_0
        return size_head, SupportedFormats.NOT_SUPPORTED

    @classmethod
    def parse_json(cls, path: Union[str, Path]) -> InkModel:
        """
        Parse ink file from either a `Path`, `str`.

        Parameters
        ----------
        path: Union[str, Path]
            Location of the JSON file

        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream

        Raises
        ------
        ValueError
            Raises if path is not a `str` or `Path`
        FormatException
            Raises if file does not exist.
        """
        if isinstance(path, (str, Path)):
            # Check if path does exist
            if not os.path.exists(path):
                raise FormatException(f'UIM file with path: {str(path)} does not exist.')
            # Check if the file ends with JSON extension
            json_encoding: bool = str(path).lower().endswith(".json")
            # Read file
            with io.open(path, 'rb') as fp:
                if json_encoding:
                    logger.info('JSON decoder chosen.')
                    # Content parser
                    return UIMDecoder300.decode_json(fp)
        raise ValueError(f"Unsupported format. Type must be str or Path, but is {type(path)}.")

    def parse(self, path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]) -> InkModel:
        """
        Parse the Universal Ink Model codec.

        Parameters
        ----------
        path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]
            `Path` of file, path as str, stream, or byte array.

        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream

        Raises
        ------
        FormatException
            Raises if the file is not an UIM file.
        TypeError
            Raises if the type is not supported.
        """
        if isinstance(path_or_stream, (str, Path)):
            # Check if path does exist
            if not os.path.exists(path_or_stream):
                raise FormatException(f'UIM file with path: {str(path_or_stream)} does not exist.')
            # Read file
            with io.open(path_or_stream, 'rb') as fp:
                logger.info('RIFF decoder chosen.')
                riff_file: Chunk = Chunk(fp, bigendian=False)
                if riff_file.getname() != RIFF_HEADER:
                    raise FormatException('File does not start with RIFF id')
                logger.info(f'Data packet size: {riff_file.getsize()}')
                riff: BytesIO = BytesIO(riff_file.read())
                riff_size: int = riff_file.getsize()
        else:
            # Read In-Memory
            if isinstance(path_or_stream, (bytes, memoryview)):
                riff: BytesIO = BytesIO(path_or_stream)
            elif isinstance(path_or_stream, BytesIO):
                riff: BytesIO = path_or_stream
            else:
                raise TypeError('parse() accepts path (str) or stream (bytes, BytesIO)')
            # Read header
            header: bytes = riff.read(4)
            # Read the stream
            if header != RIFF_HEADER:
                raise FormatException('Stream does not start with RIFF id')
            # Read package size
            size_packet: bytes = riff.read(4)
            riff_size: int = ctypes.c_uint32(int.from_bytes(size_packet, byteorder='little')).value
        logger.info(f'Data packet size: {riff_size}')
        size_head, version = UIMParser.__parse_version__(riff)
        if version == SupportedFormats.UIM_VERSION_3_0_0:
            return UIMDecoder300.decode(riff, size_head)
        if version == SupportedFormats.UIM_VERSION_3_1_0:
            return UIMDecoder310.decode(riff, size_head)
        raise FormatException(f"Parser does not support this format. {version}")

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
import struct

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


class Chunk:
    """
    Chunk
    =====
    Copied from Chunk source code from Python as it will not be available from Python 3.13.

    A Chunk is a simple container for a chunk of data in a RIFF file.

    Parameters
    ----------
    file: file
        File object
    align: bool
        Whether to align to word (2-byte) boundaries
    bigendian: bool
        Whether the file is big endian
    inclheader: bool
        Whether the header is included in the chunk
    """
    def __init__(self, file, align=True, bigendian: bool = True, inclheader: bool = False):
        self.closed = False
        self.align = align      # whether to align to word (2-byte) boundaries
        if bigendian:
            strflag = '>'
        else:
            strflag = '<'
        self.file = file
        self.chunkname = file.read(4)
        if len(self.chunkname) < 4:
            raise EOFError
        try:
            self.chunksize = struct.unpack_from(strflag+'L', file.read(4))[0]
        except struct.error:
            raise EOFError from None
        if inclheader:
            self.chunksize = self.chunksize - 8 # subtract header
        self.size_read = 0
        try:
            self.offset = self.file.tell()
        except (AttributeError, OSError):
            self.seekable = False
        else:
            self.seekable = True

    def getname(self):
        """Return the name (ID) of the current chunk."""
        return self.chunkname

    def getsize(self):
        """Return the size of the current chunk."""
        return self.chunksize

    def close(self):
        if not self.closed:
            try:
                self.skip()
            finally:
                self.closed = True

    def seek(self, pos, whence=0):
        """Seek to specified position into the chunk.
        Default position is 0 (start of chunk).
        If the file is not seekable, this will result in an error.
        """

        if self.closed:
            raise ValueError("I/O operation on closed file")
        if not self.seekable:
            raise OSError("cannot seek")
        if whence == 1:
            pos = pos + self.size_read
        elif whence == 2:
            pos = pos + self.chunksize
        if pos < 0 or pos > self.chunksize:
            raise RuntimeError
        self.file.seek(self.offset + pos, 0)
        self.size_read = pos

    def read(self, size=-1):
        """Read at most size bytes from the chunk.
        If size is omitted or negative, read until the end
        of the chunk.
        """

        if self.closed:
            raise ValueError("I/O operation on closed file")
        if self.size_read >= self.chunksize:
            return b''
        if size < 0:
            size = self.chunksize - self.size_read
        if size > self.chunksize - self.size_read:
            size = self.chunksize - self.size_read
        data = self.file.read(size)
        self.size_read = self.size_read + len(data)
        if self.size_read == self.chunksize and \
           self.align and \
           (self.chunksize & 1):
            dummy = self.file.read(1)
            self.size_read = self.size_read + len(dummy)
        return data

    def skip(self):
        """Skip the rest of the chunk.
        If you are not interested in the contents of the chunk,
        this method should be called so that the file points to
        the start of the next chunk.
        """

        if self.closed:
            raise ValueError("I/O operation on closed file")
        if self.seekable:
            try:
                n = self.chunksize - self.size_read
                # maybe fix alignment
                if self.align and (self.chunksize & 1):
                    n = n + 1
                self.file.seek(n, 1)
                self.size_read = self.size_read + n
                return
            except OSError:
                pass
        while self.size_read < self.chunksize:
            n = min(8192, self.chunksize - self.size_read)
            dummy = self.read(n)
            if not dummy:
                raise EOFError


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
            Raises if the file is not a UIM file.
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
                    logger.debug('JSON decoder chosen.')
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
                logger.debug('RIFF decoder chosen.')
                riff_file: Chunk = Chunk(fp, bigendian=False)
                if riff_file.getname() != RIFF_HEADER:
                    raise FormatException('File does not start with RIFF id')
                logger.debug(f'Data packet size: {riff_file.getsize()}')
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
        logger.debug(f'Data packet size: {riff_size}')
        size_head, version = UIMParser.__parse_version__(riff)
        if version == SupportedFormats.UIM_VERSION_3_0_0:
            return UIMDecoder300.decode(riff, size_head)
        if version == SupportedFormats.UIM_VERSION_3_1_0:
            return UIMDecoder310.decode(riff, size_head)
        raise FormatException(f"Parser does not support this format. {version}")

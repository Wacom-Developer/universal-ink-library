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
from abc import ABC
from enum import Enum
from io import BytesIO
from pathlib import Path
from typing import Union

from uim.codec.context.version import Version

UIM: str = "Universal Ink Model (UIM)"
WILL_DATA: str = "Wacom Ink Layer Language (WILL) - Data Format"
WILL_FILE: str = "Wacom Ink Layer Language (WILL) - File Format"
INKML: str = "Ink Markup Language (InkML)"


class SupportedFormats(Enum):
    """
    SupportedFormats
    ================
    Supported formats enum.
    All formats that are currently support by the library.
    """
    # Not supported Format
    NOT_SUPPORTED: Version = Version(0, 0, 0, "Not supported")
    # Universal Ink Model - Version constants
    UIM_VERSION_3_0_0: Version = Version(3, 0, 0, UIM)
    UIM_VERSION_3_1_0: Version = Version(3, 1, 0, UIM)
    # Wacom Ink Layer Language
    WILL_DATA_VERSION_2_0_0: Version = Version(2, 0, 0, WILL_DATA)
    WILL_FILE_VERSION_2_0_0: Version = Version(2, 0, 0, WILL_FILE)
    # InkML
    INKML_VERSION: Version = Version(2011, 0, 0, INKML)


class FormatException(Exception):
    """
    FormatException
    ===============
    Exception thrown while parsing ink files.
    """


class Parser(ABC):
    """
    Parser
    ======

    Parser is responsible to parse an ink file .
    """
    def parse(self, path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]) -> 'InkModel':
        """
        Parse the content of the ink file to the Universal Ink memory model.

        Parameters
        ----------
        path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]
            `Path` of file, path as str, stream, or byte array.

        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream
        """
        raise NotImplementedError


class EndOfStream(Exception):
    """
    EndOfStream
    ===========

    Exception thrown whenever the end of the stream has been reached.
    """


class Stream:
    """
    Stream
    ======

    Stream class to read bytes from byte array.

    Parameters
    ----------
    stream: bytes
        Content byte arrays
    """
    def __init__(self, stream: bytes):
        self.__idx: int = 0
        self.__stream: bytes = stream
        self.__length: int = len(stream)

    def read(self, num: int) -> Union[bytes, int]:
        """
        Read bytes from byte array.
        Parameters
        ----------
        num: int
            Number of bytes to be read

        Returns
        -------
            value: Union[bytes, int]
        Raises
        ------
        EndOfStream
            Raised if the end of the stream has been reached
        """
        if self.__idx >= self.__length:
            raise EndOfStream()
        end = self.__idx + num
        if end > self.__length:
            end = self.__length
        value = self.__stream[self.__idx:end]
        self.__idx += num
        return value

    def __len__(self):
        return self.__length

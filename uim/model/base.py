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

import hashlib
import uuid
from abc import ABC, abstractmethod
from enum import Enum

from typing import List, Any

# Global configuration
node_registration_debug: bool = False


class InkModelException(Exception):
    pass


class IdentifiableMethod(Enum):
    """Different ID encoding methods """
    UUID = 0
    MD5 = 1


class Identifier(ABC):
    """
    Internal UIM 128bit Identifier (UimID)
    --------------------------------------
    UimID is a 128-bit number used internally by the implementations.

    It can be parsed from strings in the following formats:

    Simple Hexadecimal String Representation (S-Form)
    -------------------------------------------------
    The representation of a UimID value is the hex-decimal string representation of the 128-bit number,
    assuming that it's encoded using Big Endian byte ordering.

    For example: fa70390871c84d91b83c9b56549043ca

    Hyphenated Hexadecimal String Representation (H-Form)
    -----------------------------------------------------
    This representation of a UimID value has the following codec: <part1>-<part2>-<part3>-<part4>-<part5>

    Assuming that the UimID 128-bit value is encoded using Big Endian byte ordering, it is split into 5 groups of
    bytes and each group is formatted as hexadecimal number.

    ---------------------------------------------------------------------------
    |       |  Part 1    | Part 2 | Part 3 | Part 4 | Part 5                  |
    ---------------------------------------------------------------------------
    | Bytes | 0, 1, 2, 3 | 4, 5   | 6,7    | 8, 9   | 10, 11, 12, 13, 14, 15  |
    ---------------------------------------------------------------------------

    -----------------------------------------------------------------------------
    | S	 | 32 digits: 00000000000000000000000000000000                          |
    |    | E.g., fa70390871c84d91b83c9b56549043ca                               |
    -----------------------------------------------------------------------------
    | H	 | 32 digits separated by hyphens: 00000000-0000-0000-0000-000000000000 |
    |    | E.g.,  fa703908-71c8-4d91-b83c-9b56549043ca                          |
    -----------------------------------------------------------------------------

    The identifier's string representation varies based on the domain:
     - For MD5 hashes - "N" form
     - For Ink Model Internals (Strokes, Nodes, Group Nodes etc.) - "D" form
    """
    SEPARATOR: str = "\n"

    def __init__(self, identifier: uuid.UUID, method: IdentifiableMethod = IdentifiableMethod.MD5):
        self.__identifier: uuid.UUID = identifier
        self.__method: IdentifiableMethod = method
        if identifier is not None and type(identifier) is not uuid.UUID:
            raise TypeError('Identifier must be of type UUID. [Type: {}]'.format(type(identifier)))

    @property
    def id(self) -> uuid.UUID:
        """Identifier of object. (`UUID`, read-only)"""
        if self.__identifier is None:
            self.__identifier = self.__generate_id__()
        return self.__identifier

    @property
    def id_h_form(self) -> str:
        """
        Hyphenated Hexadecimal String Representation (H-Form) (`str`, read-only)

        Examples
        --------
        32 digits separated by hyphens: 00000000-0000-0000-0000-000000000000, e.g., fa703908-71c8-4d91-b83c-9b56549043ca
        """
        return Identifier.uimid_to_h_form(self.id)

    @property
    def id_s_form(self):
        """
        Simple Hexadecimal String Representation (S-Form). (`str`, read-only)

        Examples
        --------
         32 digits: 00000000000000000000000000000000, e.g., fa70390871c84d91b83c9b56549043ca
        """
        return Identifier.uimid_to_s_form(self.id)

    @abstractmethod
    def __generate_id__(self) -> uuid.UUID:
        pass

    @classmethod
    def str_to_uimid(cls, uuid_str: str) -> uuid.UUID:
        """
        Convert from string to UimID (UUID).

        Parameters
        ----------
        uuid_str: `str`
            UimID as s-form

        Returns
        -------
        uuid: `UUID`
            UUID from string

        Raises
        ------
        FormatException
            If UUID string is not valid.
        """
        try:
            return uuid.UUID(uuid_str)
        except ValueError as e:
            raise InkModelException(f'{uuid_str} is not a valid UUID. [Exception:= {str(e)}]')

    @classmethod
    def uimid_to_h_form(cls, uimid: uuid.UUID) -> str:
        """
        Convert Uim-ID in h-form.

        Parameters
        ----------
        uimid: `UUID`
            UUID

        Returns
        -------
        h_form: str
            h-form of UimID

        Raises
        ------
        FormatException
            If UUID string is not valid.
        """
        if uimid is None:
            return ''
        uuid_str: str = uimid.hex
        return f'{uuid_str[:4]}-{uuid_str[4:6]}-{uuid_str[6:8]}-{uuid_str[8:10]}-{uuid_str[10:]}'

    @classmethod
    def uimid_to_s_form(cls, uimid: uuid.UUID) -> str:
        """
        Convert Uim-ID in s-form.

        Parameters
        ----------
        uimid: `UUID`
            UUID

        Returns
        -------
        s_form: `str`
            s-form of UimID
        """
        return uimid.hex

    @classmethod
    def from_bytes(cls, from_bytes: bytes) -> uuid.UUID:
        """
        Convert bytes array to UUID.

        Parameters
        ----------
        from_bytes: `bytes`
            Byte array encoding the UUID

        Returns
        -------
        uuid: `UUID`
            Valid UUID

        Raises
        ------
        InkModelException
            Bytes cannot be converted to UUID
        """
        try:
            return uuid.UUID(bytes_le=from_bytes)
        except ValueError as e:
            raise InkModelException(f'Bytes: {from_bytes} cannot be converted to UUID. [Exception:= {str(e)}]')


class HashIdentifier(Identifier):
    """
    MD5-hash based Unique Identifier Generation Algorithm
    -----------------------------------------------------
    The described algorithm allows generation of unique identifiers based on a tag (encoded as string value) and
    a collection of components.

    The supported component types are:
        - Integer number
        - Floating-point number
        - String

    List of properties defined as key-value pairs; the key and value of a pair are considered to be of type string.
    The described method takes a tag value and a list of components as arguments and generates a unique MD5 hash as
    an 8-byte array.

    Parameters
    ----------
    identifier: `UUID`
        Identifier

    """

    def __init__(self, identifier: uuid.UUID = None):
        super().__init__(identifier=identifier, method=IdentifiableMethod.MD5)

    @abstractmethod
    def __tokenize__(self) -> List[Any]:
        """
        Generates a list of tokens which are identify the object. The subclass defines the order of tokens.

        Returns
        -------
        tokens: `List[Any]`
            List of tokenized items
        """
        pass

    def __generate_id__(self) -> uuid.UUID:
        token: list = self.__tokenize__()
        message: str = ''
        for t in token:
            if t is None:
                message += ''
            elif isinstance(t, float):
                message += '{:.4f}'.format(t)
            elif isinstance(t, int):
                message += str(t)
            elif isinstance(t, Enum):
                message += str(t.name)
            elif isinstance(t, uuid.UUID):
                message += Identifier.uimid_to_s_form(t)
            elif isinstance(t, list):
                for val in sorted(t, key=lambda value: value[0]):
                    message += val[0]
                    message += Identifier.SEPARATOR
                    message += val[1]
                    message += Identifier.SEPARATOR
            else:
                message += str(t)
            message += Identifier.SEPARATOR
        md5_hash: str = hashlib.md5(message.encode(encoding='UTF-8', errors='strict')).hexdigest()
        return uuid.UUID(md5_hash)

    def __invalidate__(self):
        """Invalidate the hashed id if an internal value has changed."""
        self.__id = None


class UUIDIdentifier(Identifier):
    """
    UUID Identifier.

    Parameters
    ----------
    identifier: `UUID`
        Identifier
    """

    def __init__(self, identifier: uuid.UUID):
        super().__init__(identifier=identifier, method=IdentifiableMethod.UUID)

    @staticmethod
    def id_generator() -> uuid.UUID:
        """
        UUID generator function.

        Returns
        -------
        random: UUID
            Random generated UUID
        """
        return uuid.uuid4()

    def __generate_id__(self) -> uuid.UUID:
        return UUIDIdentifier.id_generator()

    def __repr__(self):
        return f'<UUIDIdentifiable : [s-form:={self.id_s_form}, h-form:={self.id_h_form}]>'

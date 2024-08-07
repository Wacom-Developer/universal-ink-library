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
from typing import List

from uim.model.ink import InkModel


class Codec(ABC):
    """
    Codec
    =====
    Abstract codec encoder class.
    """

    def encode(self, ink_model: InkModel, *args, **kwargs) -> bytes:
        """
        Encodes Ink Model object the chosen file codec.

        Parameters
        ----------
        ink_model: `InkModel`
            Universal Ink Model (memory model)
        args: List[Any]
            Additional arguments
        kwargs: dict
            Additional parameters

        Returns
        -------
        content - bytes
            File content encode in bytes UIM v3.1.0
        """
        raise NotImplementedError


class CodecEncoder(Codec, ABC):
    """
    CodecEncoder
    ============
    Abstract content parser for the different versions of the Universal Ink Model (UIM).
    """

    @classmethod
    def __encoding__(cls, data_list: List[float], precision: int, resolution: float = 1.,
                     ignore_first: bool = False) -> List[int]:
        """
        Encode the data list.

        Parameters
        ----------
        data_list: List[float]
            List of float values
        precision: int
            Precision of the encoding
        resolution: float [optional] [default: 1.0]
            Resolution of the encoding
        ignore_first: bool [optional] [default: False]
            Ignore the first value

        Returns
        -------
        encoded - List[int]
            Encoded list of integers
        """
        # Encoding
        if len(data_list) == 0:
            return []
        factor: float = 10.0 ** precision
        # Setting the data type
        converted: List[int] = []
        last: int = round(factor * (resolution * data_list[0]))
        converted.append(last)
        # Iterate items
        for idx in range(1, len(data_list)):
            v = round(factor * (resolution * data_list[idx]))
            converted.append(v - last)
            last = v
        if ignore_first:
            converted[0] = 0
        return converted

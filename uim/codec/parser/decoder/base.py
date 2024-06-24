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
from typing import List, Tuple, Any, Union


class CodecDecoder(ABC):
    """
    CodecDecoder
    ============
    Abstract codec decoder for the different versions of the Universal Ink Model (UIM) format.
    """

    @classmethod
    def __parse_properties__(cls, properties: Any) -> List[Tuple[str, str]]:
        """
        Parse the properties of the object.

        Parameters
        ----------
        properties: Any
            Properties of the object.

        Returns
        -------
        List[Tuple[str, str]]
            List of properties.
        """
        prop: List[Tuple[str, str]] = []
        for p in properties:
            prop.append((p.name, p.value))
        return prop

    @classmethod
    def __decode__(cls, values: List[float], precision: int, resolution: float = 1., start_value: float = 0,
                   data_type=float) -> List[Union[float, int]]:
        """
        Decode the values.

        Parameters
        ----------
        values: List[float]
            List of values to decode.
        precision: int
            Precision of the values.
        resolution: float [default: 1]
            Resolution of the values.
        start_value: float [default: 0]
            Start value.
        data_type: Any [default: float]
            Data type to use. It will be float by default, but it can be changed to int.

        Returns
        -------
        List[float]
            List of decoded values.
        """
        factor: float = 10.0 ** precision
        converted: List[float] = []
        factored_resolution: float = resolution * factor
        last: float = start_value if start_value == 0. else float(start_value / (resolution * factor))
        for v in values:
            v = v / factored_resolution
            converted.append(data_type(last + v))
            last = converted[-1]
        return converted

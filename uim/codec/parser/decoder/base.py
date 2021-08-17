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
from abc import ABC
from typing import List, Tuple, Any


class CodecDecoder(ABC):
    """Abstract content parser for the different versions of the Universal Ink Model."""

    @classmethod
    def __parse_properties__(cls, properties: Any) -> List[Tuple[str, str]]:
        prop: List[Tuple[str, str]] = []
        for p in properties:
            prop.append((p.name, p.value))
        return prop

    @classmethod
    def __decode__(cls, values: List[float], precision: int, resolution: float = 1., start_value: float = 0,
                   data_type=float) -> List[float]:
        factor: float = 10.0 ** precision
        converted: List[float] = []
        factored_resolution: float = resolution * factor
        last: float = start_value if start_value == 0. else float(start_value / (resolution * factor))
        for v in values:
            v = v / factored_resolution
            converted.append(data_type(last + v))
            last = converted[-1]
        return converted

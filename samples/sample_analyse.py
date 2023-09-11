# -*- coding: utf-8 -*-
# Copyright © 2023 Wacom Authors. All Rights Reserved.
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
from typing import Dict, Any

from uim.codec.parser.uim import UIMParser
from uim.model.ink import InkModel
from uim.utils.statistics import StatisticsAnalyzer

def print_model_stats(key_str: str, value: Any, indent: str = ""):
    if isinstance(value, float):
        print(f'{indent}{key_str}: {value:.2f}')
    elif isinstance(value, int):
        print(f'{indent}{key_str}: {value:d}')
    elif isinstance(value, str):
        print(f'{indent}{key_str}: {value}')
    elif isinstance(value, Dict):
        print(f'{indent}{key_str}:')
        for key_str_2, next_value in value.items():
            print_model_stats(key_str_2, next_value, indent + " ")

if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    # Parse UIM v3.0.0
    ink_model: InkModel = parser.parse('../ink/uim_3.1.0/2) Digital Ink is processable 1 (3.1 delta).uim')

    model_analyser: StatisticsAnalyzer = StatisticsAnalyzer()
    stats: Dict[str, Any] = model_analyser.analyze(ink_model)
    for key_str, value_str in stats.items():
        print_model_stats(key_str, value_str)
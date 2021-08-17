# -*- coding: utf-8 -*-
"""
   Copyright © 2021 Wacom Authors. All Rights Reserved.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from pathlib import Path

import pytest

from uim.codec.parser.will import WILL2Parser
from uim.model.ink import InkModel

# Test data directory
test_data_dir: Path = Path(__file__).parent / '../ink/will/'


def will_files() -> list:
    return [f for f in test_data_dir.iterdir() if f.is_file() and f.name.endswith('.will')]


@pytest.mark.parametrize('path', will_files())
def test_will(path: Path):
    parser: WILL2Parser = WILL2Parser()
    ink_model: InkModel = parser.parse(path)
    assert ink_model.has_brushes()
    assert ink_model.has_ink_data()
    assert ink_model.has_input_data()
    assert ink_model.has_knowledge_graph()
    assert ink_model.has_ink_structure()
    assert len(ink_model.strokes) > 0
    assert len(ink_model.sensor_data.sensor_data) > 0
    assert len(ink_model.strokes) == len(ink_model.sensor_data.sensor_data)

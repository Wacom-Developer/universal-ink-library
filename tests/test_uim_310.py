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

from uim.codec.parser.uim import UIMParser
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.ink import InkModel

# Test data directory
test_data_dir: Path = Path(__file__).parent / '../ink/uim_3.1.0/'


def uim_files() -> list:
    return [f for f in test_data_dir.iterdir() if f.is_file() and f.name.endswith('.uim')]


@pytest.mark.parametrize('path', uim_files())
def test_uim_3_1_0(path: Path):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    assert ink_model.has_brushes()
    assert ink_model.has_ink_data()
    assert ink_model.has_ink_structure()
    assert len(ink_model.strokes) > 0
    # Validate encoding
    UIMEncoder310().encode(ink_model)


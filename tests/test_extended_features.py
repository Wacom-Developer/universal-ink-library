# -*- coding: utf-8 -*-
"""
   Copyright © 2024 Wacom Authors. All Rights Reserved.

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
from typing import Dict, Any

import pytest

from uim.codec.parser.uim import UIMParser
from uim.model.helpers.text_extractor import uim_extract_text_and_semantics_from
from uim.model.ink import InkModel
from uim.model.semantics.schema import CommonViews
from uim.utils.statistics import StatisticsAnalyzer
from uim.utils.stroke_resampling import CurvatureBasedInterpolationCalculator, SplineHandler

# Test data directory
uim300_data_dir: Path = Path(__file__).parent / '../ink/uim_3.0.0/'
uim310_data_dir: Path = Path(__file__).parent / '../ink/uim_3.1.0/'


def uim_300_files() -> list:
    return [f for f in uim300_data_dir.iterdir() if f.is_file() and f.name.endswith('.uim')]


def uim_310_files() -> list:
    return [f for f in uim310_data_dir.iterdir() if f.is_file() and f.name.endswith('.uim')]


@pytest.mark.parametrize('path', uim_310_files())
def test_uim_3_1_0_semantics(path: Path):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    if ink_model.has_knowledge_graph() and ink_model.has_tree(CommonViews.HWR_VIEW.value):
        words, entities, text = uim_extract_text_and_semantics_from(ink_model, CommonViews.HWR_VIEW.value)
        assert len(words) > 0
        assert len(entities) > 0
        assert len(text) > 0


@pytest.mark.parametrize('path', uim_300_files())
def test_uim_3_0_0_semantics(path: Path):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    if ink_model.has_knowledge_graph() and ink_model.has_tree(CommonViews.HWR_VIEW.value):
        words, entities, text = uim_extract_text_and_semantics_from(ink_model, CommonViews.LEGACY_HWR_VIEW.value)
        assert len(words) > 0
        assert len(entities) > 0
        assert len(text) > 0


@pytest.mark.parametrize('path', uim_310_files())
def test_uim_3_1_0_extended_strided_array(path: Path, point_threshold: int = 15):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    strokes_as_strided_array, strided_strokes_layout = ink_model.get_strokes_as_strided_array_extended()
    calculator: CurvatureBasedInterpolationCalculator = CurvatureBasedInterpolationCalculator()
    for si, stroke in enumerate(strokes_as_strided_array):
        resampled_stroke = SplineHandler.process(stroke, strided_strokes_layout, point_threshold, calculator)
        calculator.reset_state()
        assert len(resampled_stroke) > 0


@pytest.mark.parametrize('path', uim_310_files())
def test_uim_3_1_0_analyzer(path: Path):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    model_analyser: StatisticsAnalyzer = StatisticsAnalyzer()
    stats: Dict[str, Any] = model_analyser.analyze(ink_model)
    assert len(stats) > 0

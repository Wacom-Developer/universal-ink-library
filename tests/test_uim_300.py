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
from pathlib import Path
from typing import Dict
from uuid import UUID

import pytest

from uim.codec.parser.base import FormatException
from uim.codec.parser.uim import UIMParser
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.helpers.text_extractor import uim_extract_text_and_semantics_from
from uim.model.ink import InkModel
from uim.model.inkinput.inputdata import SensorChannel
# Test data directory
from uim.model.semantics.schema import CommonViews

test_data_dir: Path = Path(__file__).parent / '../ink'
uim_data_dir: Path = test_data_dir / 'uim_3.0.0'
uim_data_dir_json: Path = test_data_dir / 'uim_3.0.0_json'


def uim_files() -> list:
    return [f for f in uim_data_dir.iterdir() if f.is_file() and f.name.endswith('.uim')]


def uim_files_json() -> list:
    return [f for f in uim_data_dir_json.iterdir() if f.is_file() and f.name.endswith('.json')]


@pytest.mark.parametrize('path', uim_files())
def test_uim_3_0_0(path: Path):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    assert ink_model.has_brushes()
    assert ink_model.has_ink_data()
    assert ink_model.has_input_data()
    assert ink_model.has_ink_structure()
    assert len(ink_model.strokes) > 0
    assert len(ink_model.sensor_data.sensor_data) > 0
    assert len(ink_model.strokes) <= len(ink_model.sensor_data.sensor_data)
    if ink_model.has_knowledge_graph():
        if ink_model.has_tree(CommonViews.LEGACY_HWR_VIEW.value):
            uim_extract_text_and_semantics_from(ink_model, hwr_view=CommonViews.LEGACY_HWR_VIEW.value)
        if ink_model.has_tree(CommonViews.HWR_VIEW.value):
            uim_extract_text_and_semantics_from(ink_model, hwr_view=CommonViews.HWR_VIEW.value)


@pytest.mark.parametrize('path', uim_files_json())
def test_uim_3_0_0_json(path: Path):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse_json(path)
    assert ink_model.has_brushes()
    assert ink_model.has_ink_data()
    assert ink_model.has_input_data()
    assert ink_model.has_ink_structure()
    assert len(ink_model.strokes) > 0
    assert len(ink_model.sensor_data.sensor_data) > 0
    assert len(ink_model.strokes) <= len(ink_model.sensor_data.sensor_data)


def test_wrong_path():
    """
    Test parsing a wrong path with UIM parser.
    """
    parser: UIMParser = UIMParser()
    with pytest.raises(FormatException):
        parser.parse_json(test_data_dir / 'uim_3.0.0_json' / 'does_not_exists.json')


def test_wrong_file_type():
    """
    Test parsing a wrong file type with UIM parser.
    """
    parser: UIMParser = UIMParser()
    with pytest.raises(Exception):
        parser.parse_json(test_data_dir / 'will' / 'apple.will')


@pytest.mark.parametrize('path', uim_files())
def test_uim_3_1_0_conversion(path: Path):
    """
    Test UIM 3.1.0 conversion.

    Parameters
    ----------
    path: Path
        Path to the UIM file
    """
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    assert ink_model.has_brushes()
    assert ink_model.has_ink_data()
    assert ink_model.has_ink_structure()
    assert len(ink_model.strokes) > 0
    map_context: Dict[UUID, SensorChannel] = {}
    for sensor_data_context in ink_model.input_configuration.sensor_contexts:
        for context in sensor_data_context.sensor_channels_contexts:
            for channel in context.channels:
                map_context[channel.id] = channel
    # Validate encoding
    uim_310_bytes: bytes = UIMEncoder310().encode(ink_model)
    assert len(uim_310_bytes) > 0
    # Validate decoding
    ink_model_decoded: InkModel = parser.parse(uim_310_bytes)
    assert ink_model_decoded.has_brushes()
    assert ink_model_decoded.has_ink_data()
    assert ink_model_decoded.has_ink_structure()
    assert ink_model.version != ink_model_decoded.version
    assert (ink_model.transform == ink_model_decoded.transform).all()

    if ink_model.has_properties() == ink_model_decoded.has_properties():
        map_prop: dict = dict(ink_model_decoded.properties)
        for key, value in ink_model_decoded.properties:
            if key in map_prop:
                assert value != map_prop[key]
                del map_prop[key]
        assert len(map_prop) == 0

    # Check if the input data is the same
    if ink_model.has_input_data() == ink_model_decoded.has_input_data():
        if ink_model.has_input_data():
            assert ink_model.input_configuration == ink_model_decoded.input_configuration
            assert ink_model.sensor_data == ink_model_decoded.sensor_data
    # Check if the brushes are the same
    assert len(ink_model.brushes.raster_brushes) == len(ink_model_decoded.brushes.raster_brushes)
    assert len(ink_model.brushes.vector_brushes) == len(ink_model_decoded.brushes.vector_brushes)
    if ink_model.has_brushes() == ink_model_decoded.has_brushes():
        for v_brush_org, v_brush_diff in zip(ink_model.brushes.vector_brushes,
                                             ink_model_decoded.brushes.vector_brushes):
            if v_brush_org != v_brush_diff:
                return False
        for r_brush_org, r_brush_diff in zip(ink_model.brushes.raster_brushes,
                                             ink_model_decoded.brushes.raster_brushes):
            if r_brush_org != r_brush_diff:
                return False

    # Check if the strokes are the same
    assert len(ink_model.strokes) == len(ink_model_decoded.strokes)
    if ink_model.has_ink_data() == ink_model_decoded.has_ink_data():
        for str_org, str_diff in zip(ink_model.strokes,
                                     ink_model_decoded.strokes):
            if str_org != str_diff:
                return False
    assert len(ink_model_decoded.knowledge_graph.statements) == len(ink_model_decoded.knowledge_graph.statements)
    if ink_model.has_knowledge_graph() == ink_model_decoded.has_knowledge_graph():
        for t_org, t_diff in zip(ink_model.knowledge_graph.statements, ink_model_decoded.knowledge_graph.statements):
            assert t_org == t_diff

    for view_org, view_diff in zip(ink_model.views, ink_model_decoded.views):
        # There are different view names
        assert view_org != view_diff


def test_parse_wrong_file():
    """
    Test parsing a wrong file with UIM parser.
    """
    parser: UIMParser = UIMParser()
    with pytest.raises(Exception):
        parser.parse(test_data_dir / 'will' / 'apple.will')


def test_parse_inkml():
    """
    Test parsing an InkML file with UIM parser.
    """
    parser: UIMParser = UIMParser()
    with pytest.raises(Exception):
        parser.parse(test_data_dir / 'inkml' / 'msft.inkml')


def test_does_not_exists():
    """
    Test parsing a file that does not exist.
    """
    parser: UIMParser = UIMParser()
    with pytest.raises(Exception):
        parser.parse(test_data_dir / 'does_not_exists.uim')

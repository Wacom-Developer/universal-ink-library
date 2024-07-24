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
import json
import math
import uuid
from pathlib import Path
from statistics import StatisticsError
from typing import Dict, Any, Tuple, List

import numpy as np
import pytest

from uim.codec.parser.base import SupportedFormats
from uim.codec.parser.uim import UIMParser
from uim.model import UUIDIdentifier
from uim.model.helpers.policy import HandleMissingDataPolicy
from uim.model.helpers.schema_content_extractor import uim_schema_semantics_from
from uim.model.helpers.text_extractor import uim_extract_text_and_semantics_from, uim_extract_text_and_semantics
from uim.model.ink import InkModel, InkTree, ViewTree
from uim.model.inkdata.brush import VectorBrush, BrushPolygonUri
from uim.model.inkdata.strokes import Spline, LayoutMask, Style, Stroke, InkStrokeAttributeType
from uim.model.inkinput.inputdata import InkSensorType, InputDevice, Environment, InkInputProvider, InkInputType, \
    SensorChannel, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext
from uim.model.inkinput.sensordata import SensorData, InkState, ChannelData
from uim.model.semantics import schema
from uim.model.semantics.node import StrokeNode, StrokeGroupNode
from uim.model.semantics.schema import (CommonViews, SemanticTriple, DEVICE_MANUFACTURER_PROPERTY,
                                        DEVICE_MODEL_PROPERTY, DEVICE_SERIAL_NUMBER_PROPERTY, DOCUMENT_AUTHOR_OBJECT,
                                        DOCUMENT_LOCALE_OBJECT)
from uim.utils.analyser import as_strided_array
from uim.utils.matrix import Matrix4x4
from uim.utils.statistics import StatisticsAnalyzer
from uim.utils.stroke_resampling import CurvatureBasedInterpolationCalculator, SplineHandler, \
    StrokeResamplerInkModelWrapper

# Test data directory
ink_dir: Path = Path(__file__).parent / '../ink'
uim300_data_dir: Path = ink_dir / 'uim_3.0.0'
uim310_data_dir: Path = ink_dir / 'uim_3.1.0'
schema_data_dir: Path = ink_dir / 'schemas'
reference_text_dir: Path = ink_dir / 'reference_text.uim_3.0.0_json'
ENVIRONMENT: str = "qa-environment"
LANGUAGE: str = "en_US"
AUTHOR: str = "John Doe"


def uim_300_files() -> list:
    return [f for f in uim300_data_dir.iterdir() if f.is_file() and f.name.endswith('.uim')]


def uim_310_files() -> list:
    return [f for f in uim310_data_dir.iterdir() if f.is_file() and f.name.endswith('.uim')]




def simulate_pressure(num_points: int, max_pressure: float = 1.0, noise_level: float = 0.1):
    x = np.linspace(0, np.pi, num_points)
    pressure = (np.sin(x) + 1) / 2 * max_pressure

    # Add a small constant to start at 0.01
    pressure = np.clip(pressure, 0.01, None)

    # Add Gaussian noise to simulate variation
    pressure += np.random.normal(0, noise_level, num_points)

    # Ensure no negative values and start from 0.01
    pressure = np.clip(pressure, 0.01, None)
    return pressure


def create_random_sensor_data(x_0: float = 100., y_0: float = 100., pressure_0: float = 0.3, noise_level: float = 1,
                              num_points: int = 5, sample_rate: int = 120) \
        -> Tuple[List[float], List[float], List[float], List[float]]:
    timestamps = np.linspace(0., num_points * (1. / sample_rate), num_points)
    # Add Gaussian noise to simulate handwriting variation
    x_values: List[float] = []
    y_values: List[float] = []
    last_x: float = x_0
    last_y: float = y_0
    for i in range(num_points):
        x_val = last_x + abs(np.random.normal(0, noise_level))
        y_val = last_y + np.random.normal(0, noise_level)
        x_values.append(x_val)
        y_values.append(y_val)
        last_x = x_val
        last_y = y_val
    pressure = simulate_pressure(num_points, max_pressure=pressure_0, noise_level=0.1)
    return timestamps.tolist(), x_values, y_values, pressure.tolist()


def created_model(num_point: int = 100, number_strokes: int = 1, with_timestamps: bool = True,
                  with_pressure: bool = True, add_sensor_data: bool = True) -> InkModel:
    # Create the model
    ink_model: InkModel = InkModel(version=SupportedFormats.UIM_VERSION_3_1_0.value)
    # Setting a unit scale factor
    ink_model.unit_scale_factor = 1.
    # Using a 4x4 matrix for scaling
    ink_model.transform = Matrix4x4.create_scale(1.)

    # Properties are added as key-value pairs
    ink_model.properties.append((DOCUMENT_AUTHOR_OBJECT, AUTHOR))
    ink_model.properties.append((DOCUMENT_LOCALE_OBJECT, LANGUAGE))

    # Create an environment
    env: Environment = Environment()
    env.properties.append(("env.name", ENVIRONMENT))
    ink_model.input_configuration.environments.append(env)

    # Ink input provider pen
    provider: InkInputProvider = InkInputProvider(input_type=InkInputType.PEN)
    ink_model.input_configuration.ink_input_providers.append(provider)

    # Input device is the sensor (pen tablet, screen, etc.)
    input_device: InputDevice = InputDevice()
    input_device.properties.append((DEVICE_SERIAL_NUMBER_PROPERTY, uuid.uuid4().hex))
    input_device.properties.append((DEVICE_MANUFACTURER_PROPERTY, "Wacom"))
    input_device.properties.append((DEVICE_MODEL_PROPERTY, "Artificial Data"))

    ink_model.input_configuration.devices.append(input_device)

    # Create a group of sensor channels
    sensor_channels: list = [
        SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0)
    ]
    time_idx: int = 0
    pressure_idx: int = 0
    idx: int = 2
    if with_pressure:
        sensor_channels.append(SensorChannel(channel_type=InkSensorType.PRESSURE, metric=InkSensorMetricType.FORCE,
                                             resolution=1.0))
        pressure_idx = idx
        idx += 1
    if with_timestamps:
        sensor_channels.append(SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME,
                                             resolution=1.0))
        time_idx = idx
    scc: SensorChannelsContext = SensorChannelsContext(channels=sensor_channels,
                                                       ink_input_provider_id=provider.id,
                                                       input_device_id=input_device.id)

    # Add all sensor channel contexts
    sensor_context: SensorContext = SensorContext()
    sensor_context.add_sensor_channels_context(scc)
    ink_model.input_configuration.sensor_contexts.append(sensor_context)

    # Create the input context using the Environment and the Sensor Context
    input_context: InputContext = InputContext(environment_id=env.id, sensor_context_id=sensor_context.id)
    ink_model.input_configuration.input_contexts.append(input_context)

    # We need to define a brush polygon
    # Add a brush specified with shape Uris
    poly_uris: list = [
        BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=1", 0.),
        BrushPolygonUri("will://brush/3.0/shape/Ellipse?precision=20&radiusX=1&radiusY=0.5", 4.0)
    ]

    # Create a vector brush
    vector_brush_0: VectorBrush = VectorBrush("app://qa-test-app/vector-brush/Brush", poly_uris)

    # Add it to the model
    ink_model.brushes.add_vector_brush(vector_brush_0)

    # Create some style
    style: Style = Style(brush_uri=vector_brush_0.name)
    style.path_point_properties.red = 0.
    style.path_point_properties.green = 0.0
    style.path_point_properties.blue = 1.0
    style.path_point_properties.alpha = 1.0
    # First you need a root group to contain the strokes
    root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    # Create a view tree for the HWR
    hwr_tree: ViewTree = ViewTree(CommonViews.HWR_VIEW.value)
    # Create an ink tree
    ink_model.ink_tree = InkTree()
    # Assign the group as the root of the main ink tree
    ink_model.ink_tree.root = root
    hwr_root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    hwr_tree.root = hwr_root
    # The hwr root denotes a word
    hwr_text_line: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    hwr_text_region: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    hwr_root.add(hwr_text_region)
    hwr_text_region.add(hwr_text_line)

    x_offset: float = 0.
    y_offset: float = 0.
    for _ in range(number_strokes):
        hwr_word: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
        # Generate a unique identifier for the sensor data
        sensor_data_id: uuid.UUID = UUIDIdentifier.id_generator()
        # Create sensor data
        sensor_data_i: SensorData = SensorData(sensor_data_id, input_context_id=input_context.id,
                                               state=InkState.PLANE)
        # Generate some random sensor data
        timestamps, x_new, y_new, pressure = create_random_sensor_data(x_0=x_offset, y_0=y_offset, num_points=num_point)
        sensor_data_i.add_data(sensor_channels[0], x_new)
        sensor_data_i.add_data(sensor_channels[1], y_new)
        if with_pressure:
            sensor_data_i.add_data(sensor_channels[pressure_idx], pressure)
        if with_timestamps:
            sensor_data_i.add_timestamp_data(sensor_channels[time_idx], timestamps)
        if add_sensor_data:
            # Add sensor data to the model
            ink_model.sensor_data.add(sensor_data_i)

        # Specify the layout of the stroke data, in this case the stroke will have variable X, Y and Size properties.
        layout_mask: int = LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value

        # Provide the stroke data - in this case 4 data points, each consisting of X, Y, Size
        path: list = [x_new[0], y_new[0], 1.0]
        for x, y, p in zip(x_new, y_new, pressure):
            path.append(x)
            path.append(y)
            path.append(1. + p)
        path.append(x_new[-1])
        path.append(y_new[-1])
        path.append(1.0)
        # Create a spline object from the path data
        spline: Spline = Spline(layout_mask, path)
        # Create a stroke object. Note that it just exists, but is not in the model yet.
        stroke_i: Stroke = Stroke(sid=UUIDIdentifier.id_generator(), spline=spline, style=style,
                                  sensor_data_id=sensor_data_id if add_sensor_data else None)
        # Add a node for stroke
        root.add(StrokeNode(stroke_i))
        hwr_word.add(StrokeNode(stroke_i))
        hwr_text_line.add(hwr_word)
        ink_model.knowledge_graph.append(SemanticTriple(hwr_word.uri, schema.IS, schema.SegmentationSchema.WORD))
        ink_model.knowledge_graph.append(SemanticTriple(hwr_word.uri, schema.SegmentationSchema.HAS_CONTENT, '-'))
        x_offset += 100.
        y_offset += 100.
    ink_model.add_view(hwr_tree)
    ink_model.knowledge_graph.append(SemanticTriple(hwr_text_region.uri, schema.IS,
                                                    schema.SegmentationSchema.TEXT_REGION))
    ink_model.knowledge_graph.append(SemanticTriple(hwr_text_line.uri, schema.IS, schema.SegmentationSchema.TEXT_LINE))
    ink_model.calculate_bounds_recursively(ink_model.ink_tree.root)
    ink_model.calculate_bounds_recursively(hwr_tree.root)
    return ink_model


@pytest.mark.parametrize('path', uim_310_files())
def test_uim_3_1_0_semantics(path: Path):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    if reference_text_dir.exists():
        with open(reference_text_dir, 'r') as f:
            reference_text: Dict[str, str] = json.loads(f.read())
    else:
        reference_text: Dict[str, str] = {}
    if ink_model.has_knowledge_graph() and ink_model.has_tree(CommonViews.HWR_VIEW.value):
        words, entities, text = uim_extract_text_and_semantics_from(ink_model, CommonViews.HWR_VIEW.value)
        assert len(words) > 0
        assert len(entities) > 0
        assert len(text) > 0
        if path.name in reference_text:
            assert text == reference_text[path.name]


def test_uim_3_1_0_math_structures():
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(schema_data_dir / 'math-structures.uim')
    if ink_model.has_knowledge_graph() and ink_model.has_tree(CommonViews.HWR_VIEW.value):
        elements = uim_schema_semantics_from(ink_model, CommonViews.HWR_VIEW.value)
        for element in elements:
            assert isinstance(element, Dict)
            assert 'type' in element
            assert element['type'] in [schema.SegmentationSchema.ROOT, schema.MathStructureSchema.MATH_BLOCK_STRUCTURES,
                                       schema.MathStructureSchema.SYMBOL,
                                       schema.MathStructureSchema.NUMBER,
                                       schema.MathStructureSchema.DIGIT,
                                       schema.MathStructureSchema.OPERATION,
                                       schema.MathStructureSchema.GROUP,
                                       schema.MathStructureSchema.FRACTION,
                                       schema.MathStructureSchema.RELATION,
                                       schema.MathStructureSchema.FENCE,
                                       schema.MathStructureSchema.MATHEMATICAL_TERM,
                                       schema.MathStructureSchema.SEPARATOR,
                                       schema.MathStructureSchema.SUPERSCRIPT,
                                       schema.MathStructureSchema.RELATION_SYMBOL,
                                       schema.MathStructureSchema.OPERATOR_SYMBOL]
            for path_id in element['path_id']:
                assert isinstance(path_id, uuid.UUID)
            assert 'bounding_box' in element
            assert isinstance(element['bounding_box'], Dict)
            assert isinstance(element['bounding_box']['x'], float)
            assert isinstance(element['bounding_box']['y'], float)
            assert isinstance(element['bounding_box']['width'], float)
            assert isinstance(element['bounding_box']['height'], float)
            assert 'attributes' in element
            for attribute in element['attributes']:
                assert isinstance(attribute[0], str)
                assert isinstance(attribute[1], (str, int, float))
  

@pytest.mark.parametrize('path', uim_310_files())
def test_uim_3_1_0_semantics(path: Path):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    if reference_text_dir.exists():
        with open(reference_text_dir, 'r') as f:
            reference_text: Dict[str, str] = json.loads(f.read())
    else:
        reference_text: Dict[str, str] = {}
    if ink_model.has_knowledge_graph() and ink_model.has_tree(CommonViews.HWR_VIEW.value):
        words, entities, text = uim_extract_text_and_semantics_from(ink_model, CommonViews.HWR_VIEW.value)
        if words is None or len(words) == 0:
            print()
        assert len(words) > 0
        assert len(entities) > 0
        assert len(text) > 0
        if path.name in reference_text:
            assert text == reference_text[path.name]
        with path.open('rb') as f:
            uim_bytes: bytes = f.read()
            words_2, entities_2, text_2 = uim_extract_text_and_semantics(uim_bytes, CommonViews.HWR_VIEW.value)
            assert text == text_2
            assert len(words) == len(words_2)
            for w1, w2 in zip(words, words_2):
                assert w1['text'] == w2['text']
                assert w1['path_id'] == w2['path_id']
                assert w1['bounding_box'] == w2['bounding_box']
            assert len(entities) == len(entities_2)
            assert entities == entities_2


@pytest.mark.parametrize('path', uim_300_files())
def test_uim_semantics_schema(path: Path):
    """
    Test the semantics schema extraction.
    """
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    if ink_model.has_knowledge_graph() and ink_model.has_tree(CommonViews.HWR_VIEW.value):
        elements = uim_schema_semantics_from(ink_model, CommonViews.HWR_VIEW.value)
        assert len(elements) > 0
        for element in elements:
            assert isinstance(element, Dict)
            assert 'type' in element
            for path_id in element['path_id']:
                assert isinstance(path_id, uuid.UUID)
            assert 'bounding_box' in element
            assert isinstance(element['bounding_box'], Dict)
            assert isinstance(element['bounding_box']['x'], float)
            assert isinstance(element['bounding_box']['y'], float)
            assert isinstance(element['bounding_box']['width'], float)
            assert isinstance(element['bounding_box']['height'], float)
            assert 'attributes' in element
            for attribute in element['attributes']:
                assert isinstance(attribute[0], str)
                assert isinstance(attribute[1], (str, int, float))


@pytest.mark.parametrize('path', uim_310_files())
def test_uim_3_1_0_interpolation(path: Path, point_threshold: int = 15):
    """
    Test the strided array method.
    """
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    strokes_as_strided_array, strided_strokes_layout = ink_model.get_strokes_as_strided_array_extended()
    calculator: CurvatureBasedInterpolationCalculator = CurvatureBasedInterpolationCalculator()
    for si, stroke in enumerate(strokes_as_strided_array):
        resampled_stroke = SplineHandler.process(stroke, strided_strokes_layout, point_threshold, calculator)
        calculator.reset_state()
        assert len(resampled_stroke) > 0
        
        
def test_interpolation():
    """
    Test the strided array method.
    """
    calculator: CurvatureBasedInterpolationCalculator = CurvatureBasedInterpolationCalculator()
    layout: List[InkStrokeAttributeType] = [
        InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y, InkStrokeAttributeType.SENSOR_TIMESTAMP,
        InkStrokeAttributeType.SENSOR_PRESSURE
    ]
    ink_model = created_model(num_point=100, number_strokes=2)
    process_layout: List[InkStrokeAttributeType] = [l for l in InkStrokeAttributeType]
    for stroke in ink_model.strokes:
        strokes_as_strided_array = stroke.as_strided_array_extended(ink_model)
        resampled_stroke = SplineHandler.process(strokes_as_strided_array, process_layout, 15, calculator)
        assert len(resampled_stroke) > 0


@pytest.mark.parametrize('path', uim_310_files())
def test_uim_3_1_0_resample(path: Path, point_threshold: int = 20):
    stroke_resampler = StrokeResamplerInkModelWrapper()
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    stroke_resampler.resample_ink_model(ink_model, point_threshold)


def test_artificial_data():
    """
    Test the fix_spline method.
    """
    ink_model_art: InkModel = created_model()
    strokes_as_strided_array, strided_strokes_layout = ink_model_art.get_strokes_as_strided_array_extended()
    calculator: CurvatureBasedInterpolationCalculator = CurvatureBasedInterpolationCalculator()
    for point_threshold in range(5, 20):
        for si, stroke in enumerate(strokes_as_strided_array):
            resampled_stroke = SplineHandler.process(stroke, strided_strokes_layout, point_threshold, calculator)
            calculator.reset_state()
            assert len(resampled_stroke) > 0


def test_strided_array():
    """
    Test the strided array method.
    """
    ink_model: InkModel = created_model(with_timestamps=False)
    strokes_as_strided_array, _ = ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.SKIP_STROKE)
    assert len(strokes_as_strided_array) == 0
    # Check exception
    with pytest.raises(ValueError):
        ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.THROW_EXCEPTION)
    ink_model: InkModel = created_model(with_pressure=False)
    strokes_as_strided_array, _ = ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.SKIP_STROKE)
    assert len(strokes_as_strided_array) == 0
    # Check all exceptions
    with pytest.raises(ValueError):
        ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.THROW_EXCEPTION)
    with pytest.raises(ValueError):
        ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.FILL_WITH_NAN)
    with pytest.raises(ValueError):
        ink_model.get_strokes_as_strided_array([InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y])
    ink_model: InkModel = created_model()
    strokes_as_strided_array, strided_strokes_layout = ink_model.get_strokes_as_strided_array()
    assert len(strokes_as_strided_array) > 0
    assert len(strided_strokes_layout) > 0


def test_strided_array_extended():
    """
    Test the strided array method.
    """
    num_points: int = 100
    ink_model: InkModel = created_model(num_point=num_points)
    # Spline x, y are mandatory
    with pytest.raises(ValueError):
        ink_model.get_strokes_as_strided_array_extended([InkStrokeAttributeType.SENSOR_TIMESTAMP,
                                                         InkStrokeAttributeType.SENSOR_PRESSURE])
    strokes_as_strided_array, strided_strokes_layout = ink_model.get_strokes_as_strided_array_extended()
    for array in strokes_as_strided_array:
        assert len(array) == num_points * len(strided_strokes_layout)
    assert len(strided_strokes_layout) > 0
    ink_model: InkModel = created_model(with_timestamps=False)
    strokes_as_strided_array, _ = ink_model.get_strokes_as_strided_array_extended(
        policy=HandleMissingDataPolicy.SKIP_STROKE
    )
    assert len(strokes_as_strided_array) == 0
    # Check exception
    with pytest.raises(ValueError):
        ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.THROW_EXCEPTION)
    ink_model: InkModel = created_model(with_pressure=False)
    strokes_as_strided_array, _ = ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.SKIP_STROKE)
    assert len(strokes_as_strided_array) == 0
    # Check exception
    with pytest.raises(ValueError):
        ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.THROW_EXCEPTION)


def test_sensor_lookup():
    """
    Test the sensor lookup method.
    """
    num_points: int = 100
    ink_model: InkModel = created_model(num_point=num_points)
    for stroke in ink_model.strokes:
        res = ink_model.sensor_data_lookup(stroke=stroke, ink_sensor_type=InkSensorType.TIMESTAMP)
        assert len(res) == num_points
        res = ink_model.sensor_data_lookup(stroke=stroke, ink_sensor_type=InkSensorType.PRESSURE)
        assert len(res) == num_points
    ink_model: InkModel = created_model(with_timestamps=False)
    for stroke in ink_model.strokes:
        res = ink_model.sensor_data_lookup(stroke=stroke, ink_sensor_type=InkSensorType.TIMESTAMP)
        assert len(res) == 0
        inst = ink_model.sensor_data_lookup(stroke=stroke, ink_sensor_type=InkSensorType.TIMESTAMP,
                                            return_channel_data_instance=True)
        assert inst is None
        res = ink_model.sensor_data_lookup(stroke=stroke, ink_sensor_type=InkSensorType.PRESSURE)
        assert len(res) == num_points
        inst = ink_model.sensor_data_lookup(stroke=stroke, ink_sensor_type=InkSensorType.PRESSURE,
                                            return_channel_data_instance=True)
        assert isinstance(inst, ChannelData)


def test_two_strokes():
    """
    Test the two strokes method.
    """
    model_analyser: StatisticsAnalyzer = StatisticsAnalyzer()
    artificial_model: InkModel = created_model(number_strokes=2)
    try:
        stats: Dict[str, Any] = model_analyser.analyze(artificial_model)

        assert len(stats) > 0
        assert len(stats['properties']) == 2
        # Check the properties
        assert stats['properties'][DOCUMENT_AUTHOR_OBJECT]['documents_count'] == 0
        assert stats['properties'][DOCUMENT_AUTHOR_OBJECT]['values'][AUTHOR]['count'] == 1
        assert stats['properties'][DOCUMENT_AUTHOR_OBJECT]['values'][AUTHOR]['percent'] == 0.0
        assert stats['properties'][DOCUMENT_LOCALE_OBJECT]['documents_count'] == 0
        assert stats['properties'][DOCUMENT_LOCALE_OBJECT]['values'][LANGUAGE]['count'] == 1
        assert stats['properties'][DOCUMENT_LOCALE_OBJECT]['values'][LANGUAGE]['percent'] == 0.0
        first_key = list(stats['input_devices'].keys())[0]
        assert stats['input_devices'][first_key]['strokes_count'] == 2
        assert stats['input_devices'][first_key]['percent'] == 100.0
        assert len(stats['sensor_channels']) == 4
        assert len(stats['document_bounds']) == 6
        # Check the sensor channels
        assert stats['sensor_channels']['X']['min'] > 0.
        assert stats['sensor_channels']['PRESSURE']['min'] > 0.
        assert stats['sensor_channels']['TIMESTAMP']['min'] == 0.0
        assert stats['sensor_channels']['X']['max'] > 0.
        assert stats['sensor_channels']['Y']['max'] > 0.
        assert stats['sensor_channels']['PRESSURE']['max'] > 0.
        assert stats['sensor_channels']['TIMESTAMP']['max'] > 0.
        assert stats['sensor_channels']['X']['mean'] > 0.
        assert stats['sensor_channels']['Y']['mean'] > 0.
        assert stats['sensor_channels']['PRESSURE']['mean'] > 0.
        assert stats['sensor_channels']['TIMESTAMP']['mean'] > 0.
        assert stats['sensor_channels']['X']['median'] > 0.
        assert stats['sensor_channels']['Y']['median'] > 0.
        assert stats['sensor_channels']['PRESSURE']['median'] > 0.
        assert stats['sensor_channels']['TIMESTAMP']['median'] > 0.
        # Check the strokes
        assert stats['strokes_count'] == 2
        assert stats['points_count']['total'] == 204
        assert stats['points_count']['min'] == 102
        assert stats['points_count']['max'] == 102
        assert stats['points_count']['mean'] == 102
        assert stats['points_count']['std'] == 0.0
        assert stats['points_count']['median'] == 102.0
        assert stats['document_stats']['min_area'] > 0.
        assert stats['document_stats']['max_area'] > 0.
        assert stats['sampling_rate'] == 0.01
        # Check the brush, env, input devices and input providers
        first_key = list(stats['brushes'].keys())[0]
        assert stats['brushes'][first_key]['strokes_count'] == 2
        assert stats['brushes'][first_key]['percent'] == 100.0
        first_key = list(stats['envs'].keys())[0]
        assert stats['envs'][first_key]['strokes_count'] == 2
        assert stats['envs'][first_key]['percent'] == 100.0
        assert len(stats['input_devices']) == 1
        first_key = list(stats['input_devices'].keys())[0]
        assert stats['input_devices'][first_key]['strokes_count'] == 2
        assert stats['input_devices'][first_key]['percent'] == 100.0
        assert len(stats['input_providers']) == 1
        first_key = list(stats['input_providers'].keys())[0]
        assert stats['input_providers'][first_key]['strokes_count'] == 2
        assert stats['input_providers'][first_key]['percent'] == 100.0
        assert len(stats['properties']) == 2
        assert len(stats['sensor_channels']) == 4
        assert len(stats['document_bounds']) == 6
        assert stats['knowledge_graph']['statements_count'] == 6
        assert len(stats['views']) == 1
        assert stats['uim_version'] == '3.1.0'

    except Exception as e:
        pytest.fail(f"StatisticsAnalyzer should not raise an exception: {e}")
    # The model should have a knowledge graph and a tree
    assert artificial_model.has_knowledge_graph()
    # The model should have a tree
    assert artificial_model.has_tree(CommonViews.HWR_VIEW.value)
    words, entities, text = uim_extract_text_and_semantics_from(artificial_model, CommonViews.HWR_VIEW.value)
    assert len(words) > 0
    assert len(entities) == 0
    assert len(text) > 0
    assert text == '--'
    for word in words:
        assert word['text'] == '-'


@pytest.mark.parametrize('path', uim_310_files() + uim_300_files())
def test_uim_analyzer(path: Path):
    """
    Test the statistics analyzer.
    """
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    try:
        model_analyser: StatisticsAnalyzer = StatisticsAnalyzer()
        stats: Dict[str, Any] = model_analyser.analyze(ink_model)
        assert len(stats) > 0
    except StatisticsError as e:
        if len(ink_model.strokes) > 1:
            pytest.fail(f"StatisticsAnalyzer should not raise a StatisticsError: {e}")
        # Single stroke models are expected to raise a StatisticsError


def test_analyzer_to_few_strokes():
    """
    Test the statistics analyzer.
    """
    artificial_model: InkModel = created_model(num_point=10, number_strokes=1, with_timestamps=False,
                                               with_pressure=False)
    with pytest.raises(StatisticsError):
        model_analyser: StatisticsAnalyzer = StatisticsAnalyzer()
        model_analyser.analyze(artificial_model)


def test_analyzer_to_no_pressure():
    """
    Test the statistics analyzer.
    """
    artificial_model: InkModel = created_model(num_point=10, number_strokes=2, with_pressure=False)
    model_analyser: StatisticsAnalyzer = StatisticsAnalyzer()
    stats = model_analyser.analyze(artificial_model)


def test_analyzer_as_strided_array():
    """
    Test the statistics analyzer.
    """
    num_points: int = 100
    artificial_model: InkModel = created_model(num_point=num_points, number_strokes=2, with_pressure=False)
    pressure_nans = lambda lst: all(math.isnan(lst[i]) for i in range(3, len(lst), 4))
    pressure_zero = lambda lst: all(lst[i] == 0. for i in range(3, len(lst), 4))
    timestamps_nans = lambda lst: all(math.isnan(lst[i]) for i in range(2, len(lst), 4))
    timestamps_zero = lambda lst: all(lst[i] == 0. for i in range(2, len(lst), 4))
    for stroke in artificial_model.strokes:
        ref = as_strided_array(artificial_model, stroke=stroke,
                               handle_missing_data=HandleMissingDataPolicy.SKIP_STROKE)
        assert ref is None
        with pytest.raises(ValueError):
            as_strided_array(artificial_model, stroke=stroke,
                             handle_missing_data=HandleMissingDataPolicy.THROW_EXCEPTION)
        ref = as_strided_array(artificial_model, stroke=stroke,
                               handle_missing_data=HandleMissingDataPolicy.FILL_WITH_NAN)
        assert ref is not None
        assert len(ref) == num_points * 4  # X, Y, Size, Pressure
        assert pressure_nans(ref)
        ref = as_strided_array(artificial_model, stroke=stroke,
                               handle_missing_data=HandleMissingDataPolicy.FILL_WITH_ZEROS)
        assert ref is not None
        assert len(ref) == num_points * 4
        assert pressure_zero(ref)
    artificial_model: InkModel = created_model(num_point=num_points, number_strokes=2, with_timestamps=False)
    for stroke in artificial_model.strokes:
        ref = as_strided_array(artificial_model, stroke=stroke,
                               handle_missing_data=HandleMissingDataPolicy.SKIP_STROKE)
        assert ref is None
        with pytest.raises(ValueError):
            as_strided_array(artificial_model, stroke=stroke,
                             handle_missing_data=HandleMissingDataPolicy.THROW_EXCEPTION)
        ref = as_strided_array(artificial_model, stroke=stroke,
                               handle_missing_data=HandleMissingDataPolicy.FILL_WITH_NAN)
        assert ref is not None
        assert len(ref) == num_points * 4  # X, Y, Size, Pressure
        assert timestamps_nans(ref)
        ref = as_strided_array(artificial_model, stroke=stroke,
                               handle_missing_data=HandleMissingDataPolicy.FILL_WITH_ZEROS)
        assert ref is not None
        assert len(ref) == num_points * 4
        assert timestamps_zero(ref)
    artificial_model: InkModel = created_model(num_point=num_points, number_strokes=2, with_pressure=False,
                                               with_timestamps=False, add_sensor_data=False)
    for stroke in artificial_model.strokes:
        ref = as_strided_array(artificial_model, stroke=stroke,
                               handle_missing_data=HandleMissingDataPolicy.FILL_WITH_ZEROS)
        assert timestamps_zero(ref)
        assert pressure_zero(ref)



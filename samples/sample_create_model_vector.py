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
import csv
import uuid
from collections import defaultdict
from pathlib import Path
from typing import List, Dict

from uim.codec.parser.base import SupportedFormats
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.base import UUIDIdentifier
from uim.model.helpers.serialize import json_encode
from uim.model.ink import InkModel, InkTree, ViewTree
from uim.model.inkdata.brush import VectorBrush, BrushPolygon, BrushPolygonUri
from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask
from uim.model.inkinput.inputdata import Environment, InkInputProvider, InkInputType, InputDevice, SensorChannel, \
    InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext, unit2unit, Unit
from uim.model.inkinput.sensordata import SensorData, InkState
from uim.model.semantics import schema
from uim.model.semantics.node import StrokeGroupNode, StrokeNode, URIBuilder
from uim.utils.matrix import Matrix4x4


def create_sensor_data(data_collection: Dict[str, List[float]],
                       input_context_id: uuid.UUID, channels: List[SensorChannel]) -> SensorData:
    """
    Create sensor data from a data collection.
    Parameters
    ----------
    data_collection: Dict[str, List[float]]

    input_context_id
    channels

    Returns
    -------
    SensorData
        Instance of SensorData
    """
    sd: SensorData = SensorData(UUIDIdentifier.id_generator(), input_context_id=input_context_id, state=InkState.PLANE)
    sd.add_data(channels[0], [unit2unit(Unit.DIP, Unit.M, v) for v in data_collection['SPLINE_X']])
    sd.add_data(channels[1], [unit2unit(Unit.DIP, Unit.M, v) for v in data_collection['SPLINE_Y']])
    sd.add_timestamp_data(channels[2], data_collection['SENSOR_TIMESTAMP'])
    sd.add_data(channels[3], data_collection['SENSOR_PRESSURE'])
    sd.add_data(channels[4], data_collection['SENSOR_AZIMUTH'])
    sd.add_data(channels[5], data_collection['SENSOR_ALTITUDE'])
    return sd


def load_sensor_data(csv_path: Path, input_context_id: uuid.UUID, channels: List[SensorChannel]) -> List[SensorData]:
    """
    Load sensor data from a CSV file.

    Parameters
    ----------
    csv_path: Path
        Path to the CSV file
    input_context_id: uuid.UUID
        Input context ID
    channels: List[SensorChannel]
        List of sensor channels

    Returns
    -------
    List[SensorData]
        List of sensor data
    """
    sensor_data_values: List[SensorData] = []
    data_collection: Dict[str, List[float]] = defaultdict(list)

    with csv_path.open('r') as f:
        reader = csv.reader(f)
        header: List[str] = next(reader)
        if header != ['idx', 'SPLINE_X', 'SPLINE_Y',
                      'SENSOR_TIMESTAMP', 'SENSOR_PRESSURE', 'SENSOR_ALTITUDE', 'SENSOR_AZIMUTH']:
            raise ValueError("Invalid CSV file format")
        last_idx: int = 0
        for row in reader:
            row_idx: int = int(row[0])
            if row_idx != last_idx:
                sensor_data_values.append(create_sensor_data(data_collection, input_context_id, channels))
                data_collection.clear()
            for idx, value in enumerate(row[1:], start=1):
                data_collection[header[idx]].append(float(value))
            last_idx = row_idx
        if len(data_collection) > 0:
            sensor_data_values.append(create_sensor_data(data_collection, input_context_id, channels))
    return sensor_data_values


def create_strokes(sensor_data_items: List[SensorData], style_stroke: Style, x_id: uuid.UUID, y_id: uuid.UUID) \
        -> List[Stroke]:
    """
    Create strokes from sensor data.

    Parameters
    ----------
    sensor_data_items: List[SensorData]
        List of sensor data
    style_stroke: Style
        Style of the stroke
    x_id: uuid.UUID
        Reference id of x sensor channel
    y_id: uuid.UUID
        Reference id of y sensor channel

    Returns
    -------
    List[Stroke]
        List of strokes
    """
    stroke_items: List[Stroke] = []
    for sensor_data_i in sensor_data_items:
        path: List[float] = []
        # The spline path contains x, y values
        mask: int = LayoutMask.X.value | LayoutMask.Y.value
        for x, y in zip(sensor_data_i.get_data_by_id(x_id).values, sensor_data_i.get_data_by_id(y_id).values):
            path.append(unit2unit(Unit.M, Unit.DIP, x))
            path.append(unit2unit(Unit.M, Unit.DIP, y))

        spline: Spline = Spline(layout_mask=mask, data=path)
        # Create a stroke from spline
        s_i: Stroke = Stroke(sid=UUIDIdentifier.id_generator(), spline=spline, style=style_stroke)
        stroke_items.append(s_i)
    return stroke_items


if __name__ == '__main__':
    # Creates an ink model from the scratch.
    ink_model: InkModel = InkModel(version=SupportedFormats.UIM_VERSION_3_1_0.value)
    # Setting a unit scale factor
    ink_model.unit_scale_factor = 1.5
    # Using a 4x4 matrix for scaling
    ink_model.transform = Matrix4x4.create_scale(1.5)

    # Properties are added as key-value pairs
    ink_model.properties.append(("Author", "Markus"))
    ink_model.properties.append(("Locale", "en_US"))

    # Create an environment
    env: Environment = Environment()
    # This should describe the environment in which the ink was captured
    env.properties.append(("wacom.ink.sdk.lang", "js"))
    env.properties.append(("wacom.ink.sdk.version", "2.0.0"))
    env.properties.append(("runtime.type", "WEB"))
    env.properties.append(("user.agent.brands", "Chromium 126, Google Chrome 126"))
    env.properties.append(("user.agent.platform", "macOS"))
    env.properties.append(("user.agent.mobile", "false"))
    env.properties.append(("app.id", "sample_create_model_vector"))
    env.properties.append(("app.version", "1.0.0"))
    ink_model.input_configuration.environments.append(env)

    # Ink input provider can be pen, mouse or touch.
    provider: InkInputProvider = InkInputProvider(input_type=InkInputType.PEN)
    ink_model.input_configuration.ink_input_providers.append(provider)

    # Input device is the sensor (pen tablet, screen, etc.)
    input_device: InputDevice = InputDevice()
    input_device.properties.append(("dev.manufacturer", "Wacom"))
    input_device.properties.append(("dev.model", "Wacom One"))
    input_device.properties.append(("dev.product.code", "DTC-133"))
    input_device.properties.append(("dev.graphics.resolution", "1920x1080"))
    ink_model.input_configuration.devices.append(input_device)
    # Create a group of sensor channels
    sensor_channels: list = [
        SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0,
                      ink_input_provider_id=provider.id, input_device_id=input_device.id),
        SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0,
                      ink_input_provider_id=provider.id,  input_device_id=input_device.id),
        SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1000.0,
                      precision=0,
                      ink_input_provider_id=provider.id, input_device_id=input_device.id),
        SensorChannel(channel_type=InkSensorType.PRESSURE, metric=InkSensorMetricType.NORMALIZED, resolution=1.0,
                      channel_min=0., channel_max=1.0,
                      ink_input_provider_id=provider.id, input_device_id=input_device.id),
        SensorChannel(channel_type=InkSensorType.ALTITUDE, metric=InkSensorMetricType.ANGLE, resolution=1.0,
                      channel_min=0., channel_max=1.5707963705062866,
                      ink_input_provider_id=provider.id, input_device_id=input_device.id),
        SensorChannel(channel_type=InkSensorType.AZIMUTH, metric=InkSensorMetricType.ANGLE, resolution=1.0,
                      channel_min=-3.1415927410125732, channel_max=3.1415927410125732,
                      ink_input_provider_id=provider.id, input_device_id=input_device.id)
    ]
    # Create a sensor channels context
    scc_wacom_one: SensorChannelsContext = SensorChannelsContext(channels=sensor_channels,
                                                                 ink_input_provider_id=provider.id,
                                                                 input_device_id=input_device.id,
                                                                 latency=0,
                                                                 sampling_rate_hint=240)

    # Add sensor channel contexts
    sensor_context: SensorContext = SensorContext()
    sensor_context.add_sensor_channels_context(scc_wacom_one)
    ink_model.input_configuration.sensor_contexts.append(sensor_context)

    # Create the input context using the Environment and the Sensor Context
    input_context: InputContext = InputContext(environment_id=env.id, sensor_context_id=sensor_context.id)
    ink_model.input_configuration.input_contexts.append(input_context)

    # Create sensor data
    # The CSV file contains sensor data for strokes
    # idx,SPLINE_X,SPLINE_Y,SENSOR_TIMESTAMP,SENSOR_PRESSURE,SENSOR_ALTITUDE,SENSOR_AZIMUTH
    sensor_data = load_sensor_data(Path(__file__).parent / '..' / 'ink' / 'sensor_data' / 'ink.csv', input_context.id,
                                   sensor_channels)
    # Add sensor data to the model
    for sensor_data_i in sensor_data:
        ink_model.sensor_data.add(sensor_data_i)

    # We need to define a brush polygon
    points: list = [(10, 10), (0, 10), (0, 0), (10, 0)]
    brush_polygons: list = [BrushPolygon(min_scale=0., points=points)]

    # Create the brush object using polygons
    vector_brush_0: VectorBrush = VectorBrush(
        "app://qa-test-app/vector-brush/MyTriangleBrush",
        brush_polygons)

    # Add it to the model
    ink_model.brushes.add_vector_brush(vector_brush_0)

    # Add a brush specified with shape Uris
    poly_uris: list = [
        BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=1", 0.),
        BrushPolygonUri("will://brush/3.0/shape/Ellipse?precision=20&radiusX=1&radiusY=0.5", 4.0)
    ]
    # Define a second brush
    vector_brush_1: VectorBrush = VectorBrush(
        "app://qa-test-app/vector-brush/MyEllipticBrush",
        poly_uris)
    # Add it to the model
    ink_model.brushes.add_vector_brush(vector_brush_1)

    # Specify the layout of the stroke data, in this case the stroke will have variable X, Y and Size properties.
    layout_mask: int = LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value

    # Create some style
    style: Style = Style(brush_uri=vector_brush_1.name)
    # Set the color of the strokes
    style.path_point_properties.red = 0.1
    style.path_point_properties.green = 0.2
    style.path_point_properties.blue = 0.4
    style.path_point_properties.alpha = 1.0

    # Create the strokes
    strokes = create_strokes(sensor_data, style, sensor_channels[0].id, sensor_channels[1].id)
    # First you need a root group to contain the strokes
    root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())

    # Assign the group as the root of the main ink tree
    ink_model.ink_tree = InkTree()
    ink_model.ink_tree.root = root

    # Adding the strokes to the root group
    for stroke in strokes:
        root.add(StrokeNode(stroke))

    # Adding view for handwriting recognition results
    hwr_tree: ViewTree = ViewTree(schema.CommonViews.HWR_VIEW.value)
    # Add view right after creation, to avoid warnings that tree is not yet attached
    ink_model.add_view(hwr_tree)
    # Create a root node for the HWR view
    hwr_root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    hwr_tree.root = hwr_root
    ink_model.knowledge_graph.append(schema.SemanticTriple(hwr_root.uri, schema.IS, schema.SegmentationSchema.ROOT))
    ink_model.knowledge_graph.append(schema.SemanticTriple(hwr_root.uri, schema.SegmentationSchema.REPRESENTS_VIEW,
                                                           schema.CommonViews.HWR_VIEW.value))

    # Here you can add the same strokes as in the main tree, but you can organize them in a different way
    # (put them in different groups)
    # You are not supposed to add strokes that are not already in the main tree.
    text_region: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    hwr_root.add(text_region)
    ink_model.knowledge_graph.append(schema.SemanticTriple(text_region.uri, schema.IS,
                                                           schema.SegmentationSchema.TEXT_REGION))

    # The text_line root denotes the text line
    text_line: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    text_region.add(text_line)
    ink_model.knowledge_graph.append(schema.SemanticTriple(text_line.uri, schema.IS,
                                                           schema.SegmentationSchema.TEXT_LINE))

    # The word node denotes a word
    word: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    text_line.add(word)
    ink_model.knowledge_graph.append(schema.SemanticTriple(word.uri, schema.IS, schema.SegmentationSchema.WORD))
    ink_model.knowledge_graph.append(schema.SemanticTriple(word.uri, schema.SegmentationSchema.HAS_CONTENT, "ink"))
    ink_model.knowledge_graph.append(schema.SemanticTriple(word.uri, schema.SegmentationSchema.HAS_LANGUAGE, "en_US"))

    # Add the strokes to the word
    for stroke_i in strokes:
        word.add(StrokeNode(stroke_i))

    # We need a URI builder
    uri_builder: URIBuilder = URIBuilder()

    # Create a named entity
    named_entity_uri: str = uri_builder.build_named_entity_uri(UUIDIdentifier.id_generator())
    ink_model.knowledge_graph.append(schema.SemanticTriple(word.uri,
                                                           schema.NamedEntityRecognitionSchema.PART_OF_NAMED_ENTITY,
                                                           named_entity_uri))

    # Add knowledge for the named entity
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri, "hasPart-0", word.uri))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri,
                                                           schema.NamedEntityRecognitionSchema.HAS_LABEL, "Ink"))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri,
                                                           schema.NamedEntityRecognitionSchema.HAS_LANGUAGE, "en_US"))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri,
                                                           schema.NamedEntityRecognitionSchema.HAS_CONFIDENCE, "0.95"))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri,
                                                           schema.NamedEntityRecognitionSchema.HAS_ARTICLE_URL,
                                                       'https://en.wikipedia.org/wiki/Ink'))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri,
                                                           schema.NamedEntityRecognitionSchema.HAS_UNIQUE_ID, 'Q127418'))
    # Save the model, this will overwrite an existing file
    with open('3_1_0_vector.uim', 'wb') as uim:
        # unicode(data) auto-decodes data to unicode if str
        uim.write(UIMEncoder310().encode(ink_model))
    # Convert the model to JSON
    with open('ink.json', 'w') as f:
        # json_encode is a helper function to convert the model to JSON
        f.write(json_encode(ink_model))
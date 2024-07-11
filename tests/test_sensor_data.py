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
import uuid
from typing import List, Tuple

import pytest

from uim.codec.parser.base import SupportedFormats
from uim.model import UUIDIdentifier
from uim.model.base import InkModelException
from uim.model.ink import InkModel, InkTree
from uim.model.inkdata.brush import VectorBrush, BrushPolygon, BrushPolygonUri, RasterBrush, RotationMode, BlendMode
from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask, PathPointProperties
from uim.model.inkinput.inputdata import Environment, InkInputProvider, InkInputType, InputDevice, SensorChannel, \
    InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext, DataType, \
    InputContextRepository
from uim.model.inkinput.sensordata import SensorData, InkState
from uim.model.semantics import schema
from uim.model.semantics.node import StrokeGroupNode, StrokeNode, StrokeFragment
from uim.model.semantics.schema import SemanticTriple
from uim.utils.matrix import Matrix4x4


def pen_sensor_context(ink_model: InkModel, provider: InkInputProvider) -> Tuple[SensorChannelsContext,
                                                                                 List[SensorChannel]]:
    """
    Create a sensor context for a pen.

    Parameters
    ----------
    ink_model: InkModel
        The ink model.
    provider: InkInputProvider
        The input provider.

    Returns
    -------
    Tuple[SensorChannelsContext, List[SensorChannel]]
        Sensor channels context and the list of sensor channels.
    """
    input_device_pen: InputDevice = InputDevice()
    input_device_pen.properties.append(("dev.id", "345456567"))
    input_device_pen.properties.append(("dev.manufacturer", "Wacom"))
    ink_model.input_configuration.devices.append(input_device_pen)
    # Sensor channels
    sensor_channels_bluetooth: list = [
        SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.PRESSURE, metric=InkSensorMetricType.FORCE, resolution=1.0)
    ]
    # Create a sensor channel context
    scc_bluetooth: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_pen.id,
                                                                 ink_input_provider_id=provider.id,
                                                                 channels=sensor_channels_bluetooth)
    assert input_device_pen != provider
    return scc_bluetooth, sensor_channels_bluetooth


def create_ink_model() -> InkModel:
    # Create the model
    ink_model: InkModel = InkModel(version=SupportedFormats.UIM_VERSION_3_1_0.value)
    # Setting a unit scale factor
    ink_model.unit_scale_factor = 1.5
    # Using a 4x4 matrix for scaling
    ink_model.transform = Matrix4x4.create_scale(1.5)
    # Create an environment
    env: Environment = Environment()
    env.add_environment_property("env.id", uuid.uuid4().hex)
    assert str(env)
    assert env != ink_model
    ink_model.input_configuration.environments.append(env)
    # Ink input provider can be pen, mouse or touch.
    provider: InkInputProvider = InkInputProvider(input_type=InkInputType.MOUSE)
    provider.properties.append(("dev.id", "1234567"))
    assert provider != env
    ink_model.input_configuration.ink_input_providers.append(provider)
    # Input device is the sensor (pen tablet, screen, etc.)
    input_device: InputDevice = InputDevice()
    input_device.properties.append(("dev.manufacturer", "Wacom"))
    ink_model.input_configuration.devices.append(input_device)
    # Create a group of sensor channels
    sensor_channels_tablet: list = [
        SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.PRESSURE, metric=InkSensorMetricType.FORCE, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.AZIMUTH, metric=InkSensorMetricType.ANGLE, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.ALTITUDE, metric=InkSensorMetricType.ANGLE, resolution=1.0)
    ]
    # Create a sensor channel context
    scc_tablet: SensorChannelsContext = SensorChannelsContext(channels=sensor_channels_tablet,
                                                              ink_input_provider_id=provider.id,
                                                              input_device_id=input_device.id)
    # We can create an additional input device, for example one providing pressure via Bluetooth
    scc_bluetooth, _ = pen_sensor_context(ink_model, provider)
    # Add all sensor channel contexts
    sensor_context: SensorContext = SensorContext()
    sensor_context.add_sensor_channels_context(scc_tablet)
    sensor_context.add_sensor_channels_context(scc_bluetooth)
    ink_model.input_configuration.sensor_contexts.append(sensor_context)
    # Create the input context using the Environment and the Sensor Context
    input_context: InputContext = InputContext(environment_id=env.id, sensor_context_id=sensor_context.id)
    ink_model.input_configuration.input_contexts.append(input_context)
    sensor_data_id: uuid.UUID = UUIDIdentifier.id_generator()
    # Create sensor data
    sensor_data_0: SensorData = SensorData(sensor_data_id, input_context_id=input_context.id,
                                           state=InkState.PLANE)
    sensor_data_0.add_timestamp_data(sensor_channels_tablet[2], [0., 0.1, 0.2, 0.3, 0.4])
    sensor_data_0.add_data(sensor_channels_tablet[0], [100.4, 103.7, 110.1])
    sensor_data_0.add_data(sensor_channels_tablet[1], [200.1, 202.0, 207.0])
    sensor_data_0.add_data(sensor_channels_tablet[3], [0.1, 0.4, 0.2])
    sensor_data_0.add_data(sensor_channels_tablet[4], [50., 51.0, 52.0])
    sensor_data_0.add_data(sensor_channels_tablet[5], [50., 51.0, 52.0])

    # Add sensor data to the model
    ink_model.sensor_data.add(sensor_data_0)
    # We need to define a brush polygon
    points: list = [(10, 10), (0, 10), (0, 0)]
    brush_polygons: list = [BrushPolygon(min_scale=0., points=points)]
    # PathPointProperties
    path_point_properties = PathPointProperties(
        size=1.0,
        red=0.0,
        green=1.0,
        blue=0.0,
        alpha=1.0,
        rotation=0.0,
        scale_x=1.0,
        scale_y=1.0,
        scale_z=1.0,
        offset_x=0.0,
        offset_y=0.0,
        offset_z=0.0
    )
    # Create the brush object using polygons
    vector_brush_0: VectorBrush = VectorBrush("app://qa-test-app/vector-brush/MyTriangleBrush", brush_polygons)
    # Add it to the model
    ink_model.brushes.add_vector_brush(vector_brush_0)
    # Add a brush specified with shape Uris
    poly_uris: list = [
        BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=1", 0.),
        BrushPolygonUri("will://brush/3.0/shape/Ellipse?precision=20&radiusX=1&radiusY=0.5", 4.0)
    ]
    vector_brush_1: VectorBrush = VectorBrush(
        "app://qa-test-app/vector-brush/MyEllipticBrush",
        poly_uris)
    raster_brush_0: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush",
        spacing=10., scattering=5., rotation=RotationMode.TRAJECTORY, shape_textures=[bytes([10, 20]),
                                                                                      bytes([30, 20])],
        fill_width=2.0, fill_height=0.3,
        fill_texture=bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255]),
        randomize_fill=False, blend_mode=BlendMode.SOURCE_OVER)
    assert input_context != raster_brush_0
    # Add it to the model
    ink_model.brushes.add_raster_brush(raster_brush_0)
    raster_brush_1: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.TRAJECTORY, fill_width=2., fill_height=0.3,
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
        ], randomize_fill=False, blend_mode=BlendMode.SOURCE_OVER)
    ink_model.brushes.add_raster_brush(raster_brush_1)
    ink_model.brushes.add_vector_brush(vector_brush_1)
    # Specify the layout of the stroke data, in this case the stroke will have variable X, Y and Size properties.
    layout_mask: int = LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value
    # Provide the stroke data - in this case 4 data points, each consisting of X, Y, Size
    path: list = [10., 10.7, 1.0, 21.0, 20.2, 2.0, 30.0, 12.4, 2.1, 40.0, 15.0, 1.5]
    # Create a spline object from the path data
    spline: Spline = Spline(layout_mask, path)
    # Create some style
    style: Style = Style(brush_uri=vector_brush_0.name)
    style.path_point_properties.red = 1.0
    style.path_point_properties.green = 0.0
    style.path_point_properties.blue = 0.0
    style.path_point_properties.alpha = 1.0
    # Create a stroke object. Note that it just exists, but is not in the model yet.
    stroke_0: Stroke = Stroke(sid=UUIDIdentifier.id_generator(), spline=spline, style=style)
    # Create a spline object - 9 data points, each consisting of X, Y, Size, Red, Green, Blue, Alpha
    spline_1: Spline = Spline(
        LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value | LayoutMask.RED.value | LayoutMask.GREEN.value
        | LayoutMask.BLUE.value | LayoutMask.ALPHA.value,
        [10.0, 10.7, 1.0, 0.5, 0.0, 0.1, 1.0,
         21.0, 20.2, 2.0, 0.9, 0.4, 0.2, 0.8,
         30.0, 12.4, 2.1, 0.7, 0.1, 0.1, 0.7,
         40.0, 15.0, 1.5, 0.3, 0.5, 0.4, 1.0,
         50.0, 45.0, 1.0, 0.3, 0.5, 0.4, 1.0,
         41.0, 53.0, 1.1, 0.2, 0.3, 0.5, 0.9,
         33.0, 73.0, 1.2, 0.6, 0.7, 0.4, 0.8,
         20.0, 84.0, 1.3, 0.7, 0.8, 0.3, 0.7,
         10.0, 91.0, 1.1, 0.7, 0.9, 0.2, 0.6])
    spline_2: Spline = Spline(
        LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value,
        [20., 20., 1.0, 21.0, 20.2, 2.0, 30.0, 12.4, 2.1, 40.0, 15.0, 1.5])
    # Create a style
    style_1: Style = Style(brush_uri=raster_brush_0.name)
    style_1.path_point_properties.rotation = 0.35
    # Create another style
    style_2: Style = Style(properties=path_point_properties,
                           brush_uri=vector_brush_1.name)

    # The render mode URI can also be app specific like app://blabla
    # The URI will://rasterization/3.0/blend-mode/SourceOver is assumed and must not be set.
    style_1.render_mode_uri = "will://rasterization/3.0/blend-mode/DestinationOver"
    # Create a stroke object. Note that it just exists, but is not in the model yet.
    stroke_1: Stroke = Stroke(UUIDIdentifier.id_generator(), spline=spline_1, style=style_1)
    stroke_2: Stroke = Stroke(UUIDIdentifier.id_generator(), spline=spline_2, style=style_2)
    # First you need a root group to contain the strokes
    root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    main_tree: InkTree = InkTree()
    ink_model.add_tree(main_tree)
    # Assign the group as the root of the main ink tree
    ink_model.ink_tree.root = root
    # Add a node for stroke 0
    stroke_node_0: StrokeNode = StrokeNode(stroke_0, StrokeFragment(0, 1, 0.0, 1.0))
    root.add(stroke_node_0)
    ink_model.knowledge_graph.append(SemanticTriple(stroke_node_0.uri, schema.IS, "will:ml/0.2/MathStroke"))
    # Add a node for stroke 1
    root.add(StrokeNode(stroke_1, StrokeFragment(0, 1, 0.0, 1.0)))
    # Add third node
    root.add(StrokeNode(stroke_2))
    return ink_model


def test_sensor_channel():
    """
    Test the sensor channel structure.
    """
    channel_id: uuid.UUID = UUIDIdentifier.id_generator()
    input_provider_id: uuid.UUID = UUIDIdentifier.id_generator()
    input_device_id: uuid.UUID = UUIDIdentifier.id_generator()
    test_sensor_channel_1: SensorChannel = SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                         metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                         channel_min=0., channel_max=10., precision=2, index=0,
                                                         name="X Channel", data_type=DataType.FLOAT32,
                                                         ink_input_provider_id=input_provider_id,
                                                         input_device_id=input_device_id)
    assert test_sensor_channel_1 == SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=0., channel_max=10., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert str(test_sensor_channel_1)
    assert test_sensor_channel_1 == SensorChannel(channel_id=UUIDIdentifier.id_generator(),
                                                  channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=0., channel_max=10., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.Y,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=0., channel_max=10., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.TIME, resolution=1.,
                                                  channel_min=0., channel_max=10., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=10.,
                                                  channel_min=0., channel_max=10., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=5., channel_max=10., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=0., channel_max=15., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=0., channel_max=10., precision=4, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=0., channel_max=10., precision=2, index=0,
                                                  name="X-Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=0., channel_max=10., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.INT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=0., channel_max=10., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=UUIDIdentifier.id_generator(),
                                                  input_device_id=input_device_id)
    assert test_sensor_channel_1 != SensorChannel(channel_id=channel_id, channel_type=InkSensorType.X,
                                                  metric=InkSensorMetricType.LENGTH, resolution=1.,
                                                  channel_min=0., channel_max=10., precision=2, index=0,
                                                  name="X Channel", data_type=DataType.FLOAT32,
                                                  ink_input_provider_id=input_provider_id,
                                                  input_device_id=UUIDIdentifier.id_generator())


def test_input_configuration():
    """Creates an ink model from the scratch."""
    # Create the model
    ink_model: InkModel = create_ink_model()
    # Check the environment
    for env in ink_model.input_configuration.environments:
        assert str(env)
        for prop in env.properties:
            assert str(prop)
            if prop[0] == "env.name":
                assert prop[1] == "My Environment"
            if prop[0] == "os.id":
                assert prop[1] == "98765"
            if prop[0] == "os.name":
                assert prop[1] == "Windows"
            if prop[0] == "os.version":
                assert prop[1] == "10.0.18362.239"
            if prop[0] == "os.build":
                assert prop[1] == "239"
            if prop[0] == "os.platform":
                assert prop[1] == "whatever"
    # Check the input providers
    for provider in ink_model.input_configuration.ink_input_providers:
        assert str(provider)
        assert provider.type in [InkInputType.PEN, InkInputType.MOUSE]
        for prop in provider.properties:
            assert str(prop)
            if prop[0] == "dev.id":
                assert prop[1] == "1234567"
    # Check the input devices
    for device in ink_model.input_configuration.devices:
        assert str(device)
        for prop in device.properties:
            assert str(prop)
            if prop[0] == "dev.id":
                assert prop[1] in ["123454321", "345456567"]
            if prop[0] == "dev.manufacturer":
                assert prop[1] == "Wacom"
    # Check the sensor contexts
    for sensor_context in ink_model.input_configuration.sensor_contexts:
        assert str(sensor_context)
        assert sensor_context.id is not None
        for scc in sensor_context.sensor_channels_contexts:
            assert str(scc)

            for sc in scc.channels:
                assert str(sc)
    # Check the input contexts
    for input_context in ink_model.input_configuration.input_contexts:
        assert str(input_context)
        assert input_context.environment_id is not None
        assert input_context.sensor_context_id is not None


def test_input_and_sensor_context():
    """
    Test sensor context.
    """
    input_device_pen: InputDevice = InputDevice()
    input_device_pen.properties.append(("dev.id", "345456567"))
    input_device_pen.properties.append(("dev.manufacturer", "Wacom"))
    provider: InkInputProvider = InkInputProvider(input_type=InkInputType.PEN)
    environment: Environment = Environment()
    environment.properties.append(("env.name", "My Environment"))
    # Sensor channels
    sensor_channels: list = [
        SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.PRESSURE, metric=InkSensorMetricType.FORCE, resolution=1.0)
    ]
    # Create a sensor channel context
    scc: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_pen.id,
                                                       ink_input_provider_id=provider.id,
                                                       channels=sensor_channels)

    # Azimuth channel has not been added
    with pytest.raises(InkModelException):
        scc.get_channel_by_type(InkSensorType.AZIMUTH)
    scc.add_sensor_channel(SensorChannel(channel_type=InkSensorType.AZIMUTH, metric=InkSensorMetricType.ANGLE,
                                         resolution=1.0))
    azimuth_channel = scc.get_channel_by_type(InkSensorType.AZIMUTH)
    assert azimuth_channel is not None

    assert scc != provider
    # Different sensor channels
    sensor_channels_2: list = [
        SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0)
    ]
    scc_2: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_pen.id,
                                                         ink_input_provider_id=provider.id,
                                                         channels=sensor_channels_2)
    assert scc != scc_2
    # Different sensor channels
    sensor_channels_mod: list = [
        SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=2.0),
        SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.PRESSURE, metric=InkSensorMetricType.FORCE, resolution=1.0)
    ]
    scc_2_b: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_pen.id,
                                                           ink_input_provider_id=provider.id,
                                                           channels=sensor_channels_mod)
    assert scc != scc_2_b
    # Different sampling rate
    scc_3: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_pen.id,
                                                         ink_input_provider_id=provider.id,
                                                         channels=sensor_channels, sampling_rate_hint=512)
    assert scc != scc_3
    # Different latency
    scc_4: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_pen.id,
                                                         ink_input_provider_id=provider.id,
                                                         channels=sensor_channels, latency=100)
    assert scc != scc_4
    # Different input device id
    scc_5: SensorChannelsContext = SensorChannelsContext(input_device_id=UUIDIdentifier.id_generator(),
                                                         ink_input_provider_id=provider.id,
                                                         channels=sensor_channels)
    assert scc != scc_5
    # Different ink input provider
    scc_6: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_pen.id,
                                                         ink_input_provider_id=UUIDIdentifier.id_generator(),
                                                         channels=sensor_channels)
    assert scc != scc_6
    # Add all sensor channel contexts
    sensor_context: SensorContext = SensorContext()
    sensor_context.add_sensor_channels_context(scc)
    with pytest.raises(InkModelException):
        sensor_context.get_channel_by_id(UUIDIdentifier.id_generator())
    with pytest.raises(InkModelException):
        sensor_context.get_channel_by_type(InkSensorType.RADIUS_X)

    sensor_context_2: SensorContext = SensorContext()
    assert sensor_context != sensor_context_2
    sensor_context_2.add_sensor_channels_context(scc_2)
    assert sensor_context != scc
    assert sensor_context != sensor_context_2
    environment_id: uuid.UUID = UUIDIdentifier.id_generator()
    input_context: InputContext = InputContext(environment_id=environment_id,
                                               sensor_context_id=sensor_context.id)
    input_context_2: InputContext = InputContext(environment_id=environment_id,
                                                 sensor_context_id=UUIDIdentifier.id_generator())
    assert input_context != input_context_2
    input_context_repo: InputContextRepository = InputContextRepository()
    input_context_repo.add_sensor_context(sensor_context)
    input_context_repo.add_ink_device(input_device_pen)
    input_context_repo.add_input_context(input_context)
    input_context_repo.add_environment(environment)
    input_context_repo.add_input_provider(provider)
    assert str(input_context_repo)
    # Check if the sensor context can be retrieved
    assert input_context_repo.get_sensor_context(sensor_context.id) == sensor_context
    assert input_context_repo.get_input_device(input_device_pen.id) == input_device_pen
    # Unknown uuids should raise an exception
    with pytest.raises(InkModelException):
        input_context_repo.get_input_context(UUIDIdentifier.id_generator())
    with pytest.raises(InkModelException):
        input_context_repo.get_sensor_context(UUIDIdentifier.id_generator())
    with pytest.raises(InkModelException):
        input_context_repo.get_input_device(UUIDIdentifier.id_generator())
    # Check if the has configuration method works
    assert input_context_repo.has_configuration()
    assert input_context_repo != sensor_context
    # Now compare the repositories
    input_context_repo_2: InputContextRepository = InputContextRepository()
    assert input_context_repo != input_context_repo_2
    input_context_repo_2.add_input_context(input_context)
    assert input_context_repo != input_context_repo_2
    input_context_repo_2.add_sensor_context(sensor_context)
    assert input_context_repo != input_context_repo_2
    input_context_repo_2.add_input_provider(provider)
    assert input_context_repo != input_context_repo_2
    input_context_repo_2.add_ink_device(input_device_pen)
    assert input_context_repo != input_context_repo_2
    input_context_repo_2.add_environment(environment)
    # Now the repositories should be equal
    assert input_context_repo == input_context_repo_2
    # Setup different context: Sensor Context
    input_context_repo_other: InputContextRepository = InputContextRepository()
    input_context_repo_other.add_sensor_context(sensor_context_2)
    input_context_repo_other.add_ink_device(input_device_pen)
    input_context_repo_other.add_input_context(input_context)
    input_context_repo_other.add_environment(environment)
    input_context_repo_other.add_input_provider(provider)
    assert input_context_repo != input_context_repo_other
    # Setup different context: Input device
    input_context_repo_other: InputContextRepository = InputContextRepository()
    input_context_repo_other.add_sensor_context(sensor_context)
    input_context_repo_other.add_ink_device(InputDevice())
    input_context_repo_other.add_input_context(input_context)
    input_context_repo_other.add_environment(environment)
    input_context_repo_other.add_input_provider(provider)
    assert input_context_repo != input_context_repo_other
    # Setup different context: Input context
    input_context_repo_other: InputContextRepository = InputContextRepository()
    input_context_repo_other.add_sensor_context(sensor_context)
    input_context_repo_other.add_ink_device(input_device_pen)
    input_context_repo_other.add_input_context(InputContext())
    input_context_repo_other.add_environment(environment)
    input_context_repo_other.add_input_provider(provider)
    assert input_context_repo != input_context_repo_other
    # Setup different context: Environment
    input_context_repo_other: InputContextRepository = InputContextRepository()
    input_context_repo_other.add_sensor_context(sensor_context)
    input_context_repo_other.add_ink_device(input_device_pen)
    input_context_repo_other.add_input_context(input_context)
    input_context_repo_other.add_environment(Environment())
    input_context_repo_other.add_input_provider(provider)
    assert input_context_repo != input_context_repo_other
    # Setup different context: Input  Provider
    input_context_repo_other: InputContextRepository = InputContextRepository()
    input_context_repo_other.add_sensor_context(sensor_context)
    input_context_repo_other.add_ink_device(input_device_pen)
    input_context_repo_other.add_input_context(input_context)
    input_context_repo_other.add_environment(environment)
    input_context_repo_other.add_input_provider(InkInputProvider())
    assert input_context_repo != input_context_repo_other

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
import math
import uuid
from typing import Optional, List, Tuple

import pytest

from uim.codec.context.scheme import PrecisionScheme
from uim.codec.parser.base import SupportedFormats
from uim.model import UUIDIdentifier
from uim.model.base import InkModelException, IdentifiableMethod
from uim.model.helpers.policy import HandleMissingDataPolicy
from uim.model.ink import InkModel, InkTree, SensorDataRepository
from uim.model.inkdata.brush import VectorBrush, BrushPolygon, BrushPolygonUri, RasterBrush, RotationMode, BlendMode, \
    BlendModeURIs
from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask, PathPointProperties, InkStrokeAttributeType
from uim.model.inkinput.inputdata import Environment, InkInputProvider, InkInputType, InputDevice, SensorChannel, \
    InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext
from uim.model.inkinput.sensordata import SensorData, InkState, ChannelData
from uim.model.semantics import schema
from uim.model.semantics.node import StrokeGroupNode, StrokeNode, StrokeFragment, URIBuilder
from uim.model.semantics.schema import CommonViews, SemanticTriple
from uim.model.semantics.structures import BoundingBox
from uim.utils.matrix import Matrix4x4

# Default path point properties
DEFAULT_PATH_PROPERTY: PathPointProperties = PathPointProperties(size=1.0, red=0.5, green=0.5, blue=0.5, alpha=1.0,
                                                                 rotation=0.0, scale_x=1.0, scale_y=1.0, scale_z=1.0,
                                                                 offset_x=0.0, offset_y=0.0, offset_z=0.0)
# Default style
DEFAULT_STYLE = Style(properties=DEFAULT_PATH_PROPERTY, 
                      brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush", particles_random_seed=0, 
                      render_mode_uri=BlendModeURIs.SOURCE_OVER)
DEFAULT_MASK: int = LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.Z.value | LayoutMask.SIZE.value | \
                    LayoutMask.ROTATION.value | \
                    LayoutMask.RED.value | LayoutMask.GREEN.value | LayoutMask.BLUE.value | LayoutMask.ALPHA.value | \
                    LayoutMask.SCALE_X.value | LayoutMask.SCALE_Y.value | LayoutMask.SCALE_Z.value | \
                    LayoutMask.OFFSET_X.value | LayoutMask.OFFSET_Y.value | LayoutMask.OFFSET_Z.value | \
                    LayoutMask.TANGENT_X.value | LayoutMask.TANGENT_Y.value
# Default spline
DEFAULT_SPLINE = Spline(layout_mask=DEFAULT_MASK, 
                        data=[1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.], 
                        ts=2., tf=0.)


def create_spline() -> Spline:
    """
    Create a spline object.

    Returns
    -------
    Spline
        Spline object.
    """
    return Spline(
            layout_mask=LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.Z.value | LayoutMask.SIZE.value |
                        LayoutMask.ROTATION.value |
                        LayoutMask.RED.value | LayoutMask.GREEN.value | LayoutMask.BLUE.value | LayoutMask.ALPHA.value |
                        LayoutMask.SCALE_X.value | LayoutMask.SCALE_Y.value | LayoutMask.SCALE_Z.value |
                        LayoutMask.OFFSET_X.value | LayoutMask.OFFSET_Y.value | LayoutMask.OFFSET_Z.value,
            data=[
                1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15.
            ],
            ts=2.,
            tf=0.
        )


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


def test_stroke():
    """
    Test stroke structure.
    """
    id_stroke: uuid.UUID = UUIDIdentifier.id_generator()
    mask: int = LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.Z.value | LayoutMask.SIZE.value |\
                LayoutMask.ROTATION.value |\
                LayoutMask.RED.value | LayoutMask.GREEN.value | LayoutMask.BLUE.value | LayoutMask.ALPHA.value |\
                LayoutMask.SCALE_X.value | LayoutMask.SCALE_Y.value | LayoutMask.SCALE_Z.value |\
                LayoutMask.OFFSET_X.value | LayoutMask.OFFSET_Y.value | LayoutMask.OFFSET_Z.value |\
                LayoutMask.TANGENT_X.value | LayoutMask.TANGENT_Y.value
    stroke: Stroke = Stroke(
        sid=id_stroke,
        spline=Spline(
            layout_mask=DEFAULT_MASK,
            data=[
                1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.
            ],
            ts=2.,
            tf=0.
        ), style=Style(
            properties=PathPointProperties(
                size=1.0,
                red=0.5,
                green=0.5,
                blue=0.5,
                alpha=1.0,
                rotation=0.0,
                scale_x=1.0,
                scale_y=1.0,
                scale_z=1.0,
                offset_x=0.0,
                offset_y=0.0,
                offset_z=0.0
            ),
            brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush",
            particles_random_seed=0,
            render_mode_uri=BlendModeURIs.SOURCE_OVER
        )
    )
    stroke.precision_scheme = PrecisionScheme(PrecisionScheme.ROTATION_SHIFT_BITS | PrecisionScheme.SIZE_SHIFT_BITS)
    assert stroke.id == id_stroke
    assert stroke.splines_x == [1.]
    assert stroke.splines_y == [2.]
    assert stroke.splines_z == [3.]
    assert stroke.sizes == [4.]
    assert stroke.rotations == [5.]
    assert stroke.red == [int(255 * 0.6)]
    assert stroke.green == [int(255 * 0.7)]
    assert stroke.blue == [int(255 * 0.8)]
    assert stroke.alpha == [int(255 * 0.9)]
    assert stroke.scales_x == [10.]
    assert stroke.scales_y == [11.]
    assert stroke.scales_z == [12.]
    assert stroke.offsets_x == [13.]
    assert stroke.offsets_y == [14.]
    assert stroke.offsets_z == [15.]
    assert str(stroke.precision_scheme)
    assert stroke.precision_scheme.value == PrecisionScheme.ROTATION_SHIFT_BITS | PrecisionScheme.SIZE_SHIFT_BITS
    assert stroke.precision_scheme.size_precision == 0
    assert stroke.precision_scheme.position_precision == 12
    assert stroke.precision_scheme.rotation_precision == 0
    assert stroke.precision_scheme.scale_precision == 0
    assert stroke.precision_scheme.offset_precision == 0
    stroke.sizes = [2.]
    stroke.scales_x = [20.]
    stroke.scales_y = [21.]
    stroke.scales_z = [22.]
    assert stroke.layout_mask == mask


def test_stroke_policy():
    """
    Test stroke policy.
    """
    ink_model: InkModel = create_ink_model()
    input_context = ink_model.input_configuration.input_contexts[0]
    sensor_context = ink_model.input_configuration.get_sensor_context(input_context.sensor_context_id)
    sensor_data: SensorData = SensorData(UUIDIdentifier.id_generator(),
                                         input_context_id=input_context.id)
    timestamps: List[float] = [0., 0.1, 0.2, 0.3, 0.4]
    if sensor_context.has_channel_type(InkSensorType.X):
        sc_x = sensor_context.get_channel_by_type(InkSensorType.X)
        sensor_data.add_data(sc_x, [0, 1, 2, 3, 4])
    if sensor_context.has_channel_type(InkSensorType.Y):
        sc_y = sensor_context.get_channel_by_type(InkSensorType.Y)
        sensor_data.add_data(sc_y, [0, 1, 2, 3, 4])
    if sensor_context.has_channel_type(InkSensorType.TIMESTAMP):
        sc_ts = sensor_context.get_channel_by_type(InkSensorType.TIMESTAMP)
        sensor_data.add_data(sc_ts, timestamps)
    if sensor_context.has_channel_type(InkSensorType.PRESSURE):
        sc_pressure = sensor_context.get_channel_by_type(InkSensorType.PRESSURE)
        sensor_data.add_data(sc_pressure, [0.1, 0.3, 1.0, 0.2])
    # Adding non timestamp data should raise an exception
    with pytest.raises(ValueError):
        sensor_data.add_timestamp_data(SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH,
                                                     resolution=1.0), [0, 1, 2, 3, 4])

    stroke: Stroke = Stroke(
        sid=UUIDIdentifier.id_generator(),
        sensor_data_id=sensor_data.id
    )
    stroke.tangent_x = []
    stroke.tangent_y = []
    stroke_node_0: StrokeNode = StrokeNode(stroke)
    # If the sensor data is not in the model, an exception should be raised

    ink_model.ink_tree.root.add(stroke_node_0)
    assert stroke.uri is not None
    stroke.properties_index = stroke.properties_index
    # If the sensor data is not in the model, an exception should be raised
    with pytest.raises(InkModelException):
        ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.FILL_WITH_ZEROS)
    ink_model.sensor_data.add(sensor_data)
    with pytest.raises(ValueError):
        ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.THROW_EXCEPTION)

    # Check sensor data lookup
    value_list = ink_model.sensor_data_lookup(stroke, InkSensorType.TIMESTAMP)
    assert isinstance(value_list, list)
    assert len(value_list) == 5
    value_list = ink_model.sensor_data_lookup(stroke, InkSensorType.TIMESTAMP)
    assert value_list == timestamps
    value_time_inst = ink_model.sensor_data_lookup(stroke, InkSensorType.TIMESTAMP, return_channel_data_instance=True)
    assert isinstance(value_time_inst, ChannelData)
    value_list = ink_model.sensor_data_lookup(stroke, InkSensorType.AZIMUTH)
    assert len(value_list) == 0
    value_pressure_inst = ink_model.sensor_data_lookup(stroke, InkSensorType.AZIMUTH, return_channel_data_instance=True)
    assert len(value_pressure_inst.values) == 0
    assert value_pressure_inst != value_time_inst
    assert value_pressure_inst != ink_model
    values, layout = ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.SKIP_STROKE)
    assert len(values) == 1
    values, layout = ink_model.get_strokes_as_strided_array(policy=HandleMissingDataPolicy.FILL_WITH_ZEROS)
    assert len(values) == 4


def test_stroke_structures():
    """
    Test the stroke structures.
    """
    # Create the model
    ink_model: InkModel = create_ink_model()
    assert ink_model.version == SupportedFormats.UIM_VERSION_3_1_0.value
    assert ink_model.unit_scale_factor == 1.5
    assert all(ink_model.transform[0] == [1.5, 0., 0., 0.])
    assert all(ink_model.transform[1] == [0., 1.5, 0., 0.])
    assert all(ink_model.transform[2] == [0., 0, 1.5, 0.])
    assert all(ink_model.transform[3] == [0., 0, 0., 1.])
    # Check the properties
    for brush in ink_model.brushes.vector_brushes:
        assert str(brush)
        assert len(brush.prototypes) > 0
        assert brush.spacing == 1.
    # Check the raster brushes
    for brush in ink_model.brushes.raster_brushes:
        assert str(brush)
        if brush.name == "app://qa-test-app/raster-brush/MyRasterBrush":
            assert brush.name == "app://qa-test-app/raster-brush/MyRasterBrush"
            assert brush.spacing == 10.
            assert brush.scattering == 5.
            assert brush.rotation == RotationMode.TRAJECTORY
            assert brush.fill_width == 2.
            assert brush.fill_height == 0.3
            assert brush.fill_texture == bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255])
            assert brush.randomize_fill is False
            assert brush.blend_mode == BlendMode.SOURCE_OVER
        elif brush.name == "app://qa-test-app/raster-brush/MyRasterBrush1":
            assert brush.name == "app://qa-test-app/raster-brush/MyRasterBrush1"
            assert brush.spacing == 10.
            assert brush.scattering == 5.
            assert brush.rotation == RotationMode.TRAJECTORY
            assert brush.fill_width == 2.
            assert brush.fill_height == 0.3
            assert brush.fill_texture_uri == "app://qa-test-app/raster-brush-fill/mixedShapesGL"
            assert brush.shape_texture_uris == [
                "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
                "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
                "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
                "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
            ]

            assert brush.randomize_fill is False

    for sc in ink_model.input_configuration.sensor_contexts:
        assert str(sc)
        for scc in sc.sensor_channels_contexts:
            assert str(scc)
            last_channel: Optional[SensorChannel] = None
            for sc in scc.channels:
                assert str(sc)
                if last_channel:
                    assert last_channel != sc
                last_channel = sc
    # Check the sensor data
    for sensor_data in ink_model.sensor_data.sensor_data:
        assert str(sensor_data)
        for channel in sensor_data.data_channels:
            assert str(channel)

    different_sensor_data = SensorDataRepository()
    different_sensor_data.add(ink_model.sensor_data.sensor_data[0])
    assert ink_model.sensor_data == different_sensor_data
    different_sensor_data.add(SensorData())
    assert ink_model.sensor_data != different_sensor_data
    with pytest.raises(InkModelException):
        ink_model.sensor_data.sensor_data_by_id(UUIDIdentifier.id_generator())
    assert ink_model.sensor_data != ink_model.input_configuration
    assert str(ink_model.sensor_data)
    sd: SensorData = ink_model.sensor_data.sensor_data[0]
    stroke: Stroke = ink_model.strokes[0]
    with pytest.raises(ValueError):
        stroke.get_sensor_point(index=-1)
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_X)) > 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_Y)) > 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_SIZES)) > 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_ROTATIONS)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_RED)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_GREEN)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_BLUE)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_ALPHA)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_OFFSETS_X)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_OFFSETS_Y)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_ROTATIONS)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_SCALES_X)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SPLINE_SCALES_Y)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SENSOR_ALTITUDE)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SENSOR_AZIMUTH)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SENSOR_PRESSURE)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SENSOR_ROTATION)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SENSOR_RADIUS_X)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SENSOR_RADIUS_Y)) == 0
    assert len(stroke.get_spline_attribute_values(InkStrokeAttributeType.SENSOR_TIMESTAMP)) == 0
    assert stroke.bounding_box == BoundingBox(10., 10.7, 30., 9.5)
    # Test find by id
    for stroke in ink_model.strokes:
        assert str(stroke)
        find_stroke: Stroke = ink_model.stroke_by_id(stroke.id)
        assert stroke.id == find_stroke.id
        with pytest.raises(InkModelException):
            ink_model.build_stroke_cache(stroke)

        new_stroke: Stroke = Stroke(UUIDIdentifier.id_generator(), sensor_data_id=sd.id,
                                    spline=create_spline())
        assert new_stroke.get_timestamp_values() is None
        assert new_stroke.get_pressure_values() is None
        ink_model.build_stroke_cache(new_stroke)
        assert len(new_stroke.get_timestamp_values()) > 0
        assert len(new_stroke.get_pressure_values()) > 0
    with pytest.raises(InkModelException):
        ink_model.stroke_by_id(UUIDIdentifier.id_generator())

    ink_model.input_configuration = None
    assert ink_model.input_configuration is None

    for ink_node in ink_model.ink_tree:
        if isinstance(ink_node, StrokeNode):
            stroke_node: StrokeNode = ink_node
            if len(ink_model.knowledge_graph.filter(subject=stroke_node.uri)) > 0:
                with pytest.raises(InkModelException):
                    ink_model.clone_stroke_node(stroke_node)
            else:
                new_node = ink_model.clone_stroke_node(stroke_node)
                assert new_node == stroke_node
            new_node_no_semantics = ink_model.clone_stroke_node(stroke_node, clone_semantics=False)
            assert new_node_no_semantics == stroke_node
            ink_model.clear_stroke_cache(stroke_node.stroke)
        else:
            stroke_group_node: StrokeGroupNode = ink_node
            with pytest.raises(InkModelException):
                ink_model.clone_stroke_group_node(stroke_group_node)
            ink_model.clone_stroke_group_node(stroke_group_node, clone_semantics=False)

    channel_id: uuid.UUID = UUIDIdentifier.id_generator()
    x_channel: SensorChannel = SensorChannel(channel_type=InkSensorType.X,
                                             metric=InkSensorMetricType.LENGTH,
                                             resolution=1.0)
    assert str(x_channel)

    cd1 = ChannelData(channel_id, values=[1.0, 2.0, 3.0])
    cd2 = ChannelData(channel_id, values=[1.0, 2.0, 4.0])
    cd3 = ChannelData(UUIDIdentifier.id_generator(), values=[1.0, 2.0, 4.0])
    assert cd1 != cd2
    assert cd2 != cd3
    sensor_data = SensorData(UUIDIdentifier.id_generator())
    with pytest.raises(ValueError):
        sensor_data.add_timestamp_data(None, [1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        sensor_data.add_timestamp_data(SensorChannel(channel_type=InkSensorType.TIMESTAMP,
                                                     metric=InkSensorMetricType.TIME,
                                                     resolution=1.0), None)
    sensor_data.add_timestamp_data(SensorChannel(channel_type=InkSensorType.TIMESTAMP,
                                                 metric=InkSensorMetricType.TIME,
                                                 resolution=1.0), [])
    with pytest.raises(ValueError):
        sensor_data.add_data(None, [1.0, 2.0, 3.0])
    with pytest.raises(ValueError):
        sensor_data.add_data(SensorChannel(channel_type=InkSensorType.X,
                                           metric=InkSensorMetricType.LENGTH,
                                           resolution=1.0), None)
    sensor_data.add_data(x_channel, values=[])
    sd_id: uuid.UUID = UUIDIdentifier.id_generator()
    input_context_id: uuid.UUID = UUIDIdentifier.id_generator()
    sd_1 = SensorData(sd_id)
    sd_2 = SensorData(sd_id)
    assert sd_1 != ink_model
    assert sd_1 == sd_2
    sd_2.add_data(sensor_channel=x_channel, values=[1., 2., 3.])
    assert sd_1 != sd_2
    sd_1.add_data(x_channel, values=[1., 2., 3.])
    sd_2.input_context_id = input_context_id
    assert sd_1 != sd_2
    sd_1.input_context_id = input_context_id
    sd_3 = SensorData(UUIDIdentifier.id_generator())
    assert sd_1 != sd_3


def test_stroke_equivalence():
    """
    Test stroke equivalence
    """
    stroke_id: uuid.UUID = UUIDIdentifier.id_generator()
    sensor_data_id: uuid.UUID = UUIDIdentifier.id_generator()

    # Reference stroke
    stroke: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id, spline=DEFAULT_SPLINE, style=DEFAULT_STYLE)
    # Different stroke id
    stroke_other: Stroke = Stroke(
        sid=UUIDIdentifier.id_generator(),
        sensor_data_id=sensor_data_id,
        spline=DEFAULT_SPLINE, style=DEFAULT_STYLE
    )
    assert stroke != stroke_other
    # Different sensor data id
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=UUIDIdentifier.id_generator(), spline=DEFAULT_SPLINE, 
                                  style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different path point properties
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id, spline=DEFAULT_SPLINE, 
                                  style=Style(
                                      properties=PathPointProperties(
                                            size=2.0,
                                            red=0.5,
                                            green=0.5,
                                            blue=0.5,
                                            alpha=1.0,
                                            rotation=0.0,
                                            scale_x=1.0,
                                            scale_y=1.0,
                                            scale_z=1.0,
                                            offset_x=0.0,
                                            offset_y=0.0,
                                            offset_z=0.0
                                        ),
                                      brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush",
                                      particles_random_seed=0,
                                      render_mode_uri=BlendModeURIs.SOURCE_OVER
                                  ))
    assert stroke != stroke_other
    # Different brush uri
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id, spline=DEFAULT_SPLINE, 
                                  style=Style(
                                    properties=DEFAULT_PATH_PROPERTY,
                                    brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush_2",
                                    particles_random_seed=0,
                                    render_mode_uri=BlendModeURIs.SOURCE_OVER
                                  ))
    assert stroke != stroke_other
    # Different particles random seed
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id, spline=DEFAULT_SPLINE,
                                  style=Style(
                                    properties=DEFAULT_PATH_PROPERTY,
                                    brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush",
                                    particles_random_seed=4,
                                    render_mode_uri=BlendModeURIs.SOURCE_OVER
                                 ))
    assert stroke != stroke_other
    # Different render mode
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
        spline=DEFAULT_SPLINE, style=Style(
            properties=DEFAULT_PATH_PROPERTY,
            brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush",
            particles_random_seed=0,
            render_mode_uri=BlendModeURIs.COPY
        )
    )
    assert stroke != stroke_other
    # Different render mode
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
        spline=DEFAULT_SPLINE, style=Style(
            properties=DEFAULT_PATH_PROPERTY,
            brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush",
            particles_random_seed=0,
            render_mode_uri=BlendModeURIs.COPY
        ),
        random_seed=42
    )
    assert stroke != stroke_other
    # Different spline data x
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        5., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data y
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 5., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data z
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 5., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data size
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                      layout_mask=DEFAULT_MASK,
                                      data=[
                                         1., 2., 3., 5., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.
                                      ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data rotation
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                      layout_mask=DEFAULT_MASK,
                                      data=[
                                          1., 2., 3., 4., 9., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.
                                      ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data red color component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                      layout_mask=DEFAULT_MASK,
                                      data=[
                                        1., 2., 3., 4., 5., 0.9, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.
                                      ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data green color component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.9, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data blue color component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.5, 0.9, 10., 11., 12., 13., 14., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data alpha component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.5, 10., 11., 12., 13., 14., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data scale x component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 19., 11., 12., 13., 14., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data scale y component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 19., 12., 13., 14., 15., 16., 17.
                                    ],
                                    ts=2.,
                                    tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data scale z component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 19., 13., 14., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data offset x component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 19., 14., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data offset y component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 19., 15., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data offset z component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 19., 16., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data tangent x component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 19., 17.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different spline data tangent y component
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(
                                    layout_mask=DEFAULT_MASK,
                                    data=[
                                        1., 2., 3., 4., 5., 0.6, 0.7, 0.8, 0.9, 10., 11., 12., 13., 14., 15., 16., 19.
                                    ], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different start parameter
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id, spline=DEFAULT_SPLINE,
                                  style=DEFAULT_STYLE)
    stroke_other.start_parameter = 1.
    assert stroke != stroke_other
    stroke_other.start_parameter = 2.
    # Different end parameter
    stroke_other.end_parameter = 1.
    assert stroke != stroke_other
    stroke_other.end_parameter = 0.
    # Different sensor data mapping
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id, sensor_data_mapping=[1, 2],
                                  spline=DEFAULT_SPLINE, style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different sensor data offset
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id, sensor_data_offset=4,
                                  spline=DEFAULT_SPLINE, style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different length of spline data
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id,
                                  spline=Spline(layout_mask=DEFAULT_MASK, data=[], ts=2., tf=0.), style=DEFAULT_STYLE)
    assert stroke != stroke_other
    # Different random data offset
    stroke_other: Stroke = Stroke(sid=stroke_id, sensor_data_id=sensor_data_id, spline=DEFAULT_SPLINE,
                                  style=DEFAULT_STYLE, random_seed=42)
    assert stroke != stroke_other


def test_stroke_fragment():
    """
    Test the stroke fragment structure.
    """
    with pytest.raises(ValueError):
        StrokeFragment(-1, 1, 0.0, 1.0)
    with pytest.raises(ValueError):
        StrokeFragment(0, 1, 1.0, 0.0)
    with pytest.raises(ValueError):
        StrokeFragment(1, 0, 1.0, 0.0)
    with pytest.raises(ValueError):
        StrokeFragment(0, 1, 0., 2.0)

    fragment: StrokeFragment = StrokeFragment(0, 1, 0.0, 1.0)
    assert str(fragment)
    assert fragment.from_point_index == 0
    assert fragment.to_point_index == 1
    assert fragment.from_t_value == 0.0
    assert fragment.to_t_value == 1.0
    fragment_2: StrokeFragment = StrokeFragment(0, 1, 0.0, 1.0)
    assert fragment == fragment_2
    fragment.from_point_index = 1
    assert fragment != fragment_2
    fragment.from_point_index = 0
    fragment.to_point_index = 2
    assert fragment != fragment_2
    fragment.to_point_index = 1
    fragment.from_t_value = 0.1
    assert fragment != fragment_2
    fragment.from_t_value = 0.0
    fragment.to_t_value = 0.9
    assert fragment != fragment_2
    assert fragment != StrokeGroupNode(UUIDIdentifier.id_generator())


def test_stroke_node():
    """
    Test the stroke node structure.
    """
    main_tree: InkTree = InkTree(CommonViews.MAIN_INK_TREE.value)
    root_node: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    main_tree.root = root_node
    fragment: StrokeFragment = StrokeFragment(0, 1, 0.0, 1.0)
    stroke_id: uuid.UUID = UUIDIdentifier.id_generator()
    stroke: Stroke = Stroke(stroke_id)
    stroke_node: StrokeNode = StrokeNode(stroke)
    assert str(stroke_node)
    main_tree.root.add(stroke_node)
    assert root_node.child_group_nodes_count() == 0
    assert root_node.child_stroke_nodes_count() == 1
    test_group_node: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    test_group_node.add(StrokeNode(Stroke(UUIDIdentifier.id_generator())))
    test_group_node.add(StrokeNode(Stroke(UUIDIdentifier.id_generator())))
    main_tree.root.add(test_group_node)
    assert root_node.child_group_nodes_count() == 1
    assert root_node.child_stroke_nodes_count() == 1
    root_node.sort_children(lambda x, y: 0 if isinstance(x, StrokeNode) else 1)
    assert stroke != root_node
    assert stroke_node.stroke == stroke
    assert stroke_node.uri == URIBuilder().build_node_uri_from(stroke_node.stroke.id,
                                                               view_name=CommonViews.MAIN_INK_TREE.value,
                                                               uri_format=SupportedFormats.UIM_VERSION_3_1_0)
    stroke_node_2: StrokeNode = StrokeNode(stroke)
    assert stroke_node == stroke_node_2
    assert stroke_node != stroke_id
    stroke_node_2.fragment = fragment
    assert stroke_node != stroke_node_2
    stroke_2: Stroke = Stroke(UUIDIdentifier.id_generator())
    stroke_node_3: StrokeNode = StrokeNode(stroke_2)
    assert stroke_node != stroke_node_3

    group_node: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    assert group_node != stroke_node
    with pytest.raises(InkModelException):
        # Setting the parent of a stroke node to a group node
        stroke_node_2.parent = StrokeGroupNode(UUIDIdentifier.id_generator())
        group_node.add(stroke_node_2)
    stroke_node.stroke = Stroke(UUIDIdentifier.id_generator())


def test_stroke_attribute():
    """
    Test stroke attribute.
    """
    assert InkStrokeAttributeType.get_attribute_type_by_sensor(InkSensorType.X) == InkStrokeAttributeType.SPLINE_X
    assert InkStrokeAttributeType.get_attribute_type_by_sensor(InkSensorType.Y) == InkStrokeAttributeType.SPLINE_Y
    assert InkStrokeAttributeType.get_attribute_type_by_sensor(InkSensorType.Z) is None
    assert (InkStrokeAttributeType.get_attribute_type_by_sensor(InkSensorType.PRESSURE) ==
            InkStrokeAttributeType.SENSOR_PRESSURE)
    assert (InkStrokeAttributeType.get_attribute_type_by_sensor(InkSensorType.RADIUS_X) ==
            InkStrokeAttributeType.SENSOR_RADIUS_X)
    assert (InkStrokeAttributeType.get_attribute_type_by_sensor(InkSensorType.RADIUS_Y) ==
            InkStrokeAttributeType.SENSOR_RADIUS_Y)
    assert (InkStrokeAttributeType.get_attribute_type_by_sensor(InkSensorType.AZIMUTH) ==
            InkStrokeAttributeType.SENSOR_AZIMUTH)
    assert (InkStrokeAttributeType.get_attribute_type_by_sensor(InkSensorType.ALTITUDE) ==
            InkStrokeAttributeType.SENSOR_ALTITUDE)
    assert (InkStrokeAttributeType.get_attribute_type_by_sensor(InkSensorType.ROTATION) ==
            InkStrokeAttributeType.SENSOR_ROTATION)
    # Test the attribute type
    assert (InkStrokeAttributeType.get_sensor_type_by_attribute(InkStrokeAttributeType.SPLINE_X) ==
            InkSensorType.X)
    assert InkStrokeAttributeType.get_sensor_type_by_attribute(InkStrokeAttributeType.SPLINE_Y) == InkSensorType.Y
    assert (InkStrokeAttributeType.get_sensor_type_by_attribute(InkStrokeAttributeType.SENSOR_PRESSURE) ==
            InkSensorType.PRESSURE)
    assert (InkStrokeAttributeType.get_sensor_type_by_attribute(InkStrokeAttributeType.SENSOR_RADIUS_X) ==
            InkSensorType.RADIUS_X)
    assert (InkStrokeAttributeType.get_sensor_type_by_attribute(InkStrokeAttributeType.SENSOR_RADIUS_Y) ==
            InkSensorType.RADIUS_Y)
    assert (InkStrokeAttributeType.get_sensor_type_by_attribute(InkStrokeAttributeType.SENSOR_AZIMUTH) ==
            InkSensorType.AZIMUTH)
    assert (InkStrokeAttributeType.get_sensor_type_by_attribute(InkStrokeAttributeType.SENSOR_ALTITUDE) ==
            InkSensorType.ALTITUDE)
    assert (InkStrokeAttributeType.get_sensor_type_by_attribute(InkStrokeAttributeType.SENSOR_ROTATION)
            == InkSensorType.ROTATION)
    assert InkStrokeAttributeType.get_sensor_type_by_attribute(InkStrokeAttributeType.SPLINE_SIZES) is None
    properties = PathPointProperties(
        size=1.0,
        red=0.1,
        green=0.2,
        blue=0.3,
        alpha=0.4,
        rotation=5.0,
        scale_x=6.0,
        scale_y=7.0,
        scale_z=8.0,
        offset_x=9.0,
        offset_y=10.0,
        offset_z=11.0
    )
    assert InkStrokeAttributeType.SPLINE_SIZES.resolve_path_point_property(properties) == 1.0
    assert InkStrokeAttributeType.SPLINE_RED.resolve_path_point_property(properties) == 0.1
    assert InkStrokeAttributeType.SPLINE_GREEN.resolve_path_point_property(properties) == 0.2
    assert InkStrokeAttributeType.SPLINE_BLUE.resolve_path_point_property(properties) == 0.3
    assert InkStrokeAttributeType.SPLINE_ALPHA.resolve_path_point_property(properties) == 0.4
    assert InkStrokeAttributeType.SPLINE_ROTATIONS.resolve_path_point_property(properties) == 5.0
    assert InkStrokeAttributeType.SPLINE_SCALES_X.resolve_path_point_property(properties) == 6.0
    assert InkStrokeAttributeType.SPLINE_SCALES_Y.resolve_path_point_property(properties) == 7.0
    assert InkStrokeAttributeType.SPLINE_OFFSETS_X.resolve_path_point_property(properties) == 9.0
    assert InkStrokeAttributeType.SPLINE_OFFSETS_Y.resolve_path_point_property(properties) == 10.0
    assert InkStrokeAttributeType.SENSOR_PRESSURE.resolve_path_point_property(properties) is None


def test_stroke_strided_array():
    """
    Test the strided array structure.
    """
    ink_model: InkModel = InkModel(version=SupportedFormats.UIM_VERSION_3_1_0.value)
    input_device_pen: InputDevice = InputDevice()
    assert input_device_pen.method == IdentifiableMethod.MD5
    ink_model.input_configuration.devices.append(input_device_pen)
    # Sensor channels
    sensor_channels: list = [
        SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0)
    ]
    ink_input_provider: InkInputProvider = InkInputProvider()
    # Create a sensor channel context
    scc: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_pen.id,
                                                       ink_input_provider_id=ink_input_provider.id,
                                                       channels=sensor_channels)
    sensor_context: SensorContext = SensorContext()
    sensor_context.add_sensor_channels_context(scc)
    ink_model.input_configuration.sensor_contexts.append(sensor_context)
    input_context: InputContext = InputContext(sensor_context_id=sensor_context.id)
    ink_model.input_configuration.input_contexts.append(input_context)
    sensor_data_id: uuid.UUID = UUIDIdentifier.id_generator()
    sensor_data: SensorData = SensorData(sid=sensor_data_id, input_context_id=input_context.id)
    sensor_data.add_data(SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH,
                                       resolution=1.0), [1., 2., 3., 2., 1.])
    sensor_data.add_data(SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH,
                                       resolution=1.0), [1., 2., 3., 2., 1.])
    ink_model.sensor_data.add(sensor_data)
    # Default path point properties
    props: PathPointProperties = PathPointProperties(size=1.0, red=0.0, green=0.5, blue=0.5, alpha=1.0,
                                                     rotation=0.0, scale_x=1.0, scale_y=1.0,
                                                     scale_z=1.0,
                                                     offset_x=0.0, offset_y=0.0, offset_z=0.0)
    # Default style
    style = Style(properties=props,
                  brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush", particles_random_seed=0,
                  render_mode_uri=BlendModeURIs.SOURCE_OVER)
    stroke: Stroke = Stroke(sid=UUIDIdentifier.id_generator(), sensor_data_id=sensor_data_id,
                            style=style)
    stroke.splines_x = [1., 1., 2., 3., 2., 1., 1.]
    stroke.splines_y = [1., 1., 2., 3., 2., 1., 1.]
    # First you need a root group to contain the strokes
    root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    main_tree: InkTree = InkTree()
    ink_model.add_tree(main_tree)
    # Assign the group as the root of the main ink tree
    ink_model.ink_tree.root = root
    root.add(StrokeNode(stroke))
    # Stoke must be skipped so None
    assert stroke.as_strided_array_extended(ink_model, handle_missing_data=HandleMissingDataPolicy.SKIP_STROKE) is None

    array = stroke.as_strided_array_extended(ink_model, handle_missing_data=HandleMissingDataPolicy.FILL_WITH_ZEROS)
    # The missing data is filled with zeros
    assert array == [1.0, 1.0, 0, 0, 2.0, 2.0, 0, 0, 3.0, 3.0, 0, 0, 2.0, 2.0, 0, 0, 1.0, 1.0, 0, 0]
    # Here an exception is thrown because the missing data is not handled
    with pytest.raises(ValueError):
        stroke.as_strided_array_extended(ink_model, handle_missing_data=HandleMissingDataPolicy.THROW_EXCEPTION)
        
    array = stroke.as_strided_array_extended(ink_model, handle_missing_data=HandleMissingDataPolicy.FILL_WITH_NAN)
    expected: List[float] = [1.0, 1.0, float("nan"), float("nan"), 2.0, 2.0, float("nan"), float("nan"),
                             3.0, 3.0, float("nan"), float("nan"), 2.0, 2.0, float("nan"), float("nan"),
                             1.0, 1.0, float("nan"), float("nan")]
    assert len(array) == len(expected)
    for v1, v2 in zip(array, expected):
        if math.isnan(v1):
            assert math.isnan(v2)
        else:
            assert v1 == v2
    with pytest.raises(ValueError):
        stroke.as_strided_array_extended(ink_model, handle_missing_data="Not a valid policy")
    layout_different: List[InkStrokeAttributeType] = [
        InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y, InkStrokeAttributeType.SPLINE_RED,
        InkStrokeAttributeType.SPLINE_GREEN, InkStrokeAttributeType.SPLINE_BLUE
    ]
    stroke.as_strided_array_extended(ink_model, layout=layout_different)

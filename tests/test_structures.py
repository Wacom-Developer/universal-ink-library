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
from uim.codec.parser.uim import UIMParser
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model import UUIDIdentifier
from uim.model.base import InkModelException, Identifier, IdentifiableMethod
from uim.model.helpers.treeiterator import PreOrderEnumerator
from uim.model.ink import InkModel, ViewTree, InkTree
from uim.model.inkdata.brush import VectorBrush, BrushPolygon, BrushPolygonUri, RasterBrush, RotationMode, BlendMode, \
    BlendModeURIs
from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask, PathPointProperties
from uim.model.inkinput.inputdata import Environment, InkInputProvider, InkInputType, InputDevice, SensorChannel, \
    InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext
from uim.model.inkinput.sensordata import SensorData, InkState
from uim.model.semantics import schema
from uim.model.semantics.node import StrokeGroupNode, StrokeNode, StrokeFragment, URIBuilder, InkNode
from uim.model.semantics.schema import CommonViews, SemanticTriple, DOCUMENT_AUTHOR_OBJECT, DOCUMENT_LOCALE_OBJECT
from uim.model.semantics.structures import BoundingBox
from uim.utils.matrix import Matrix4x4


def create_ink_model(with_sensor_data: bool = True) -> InkModel:
    # Create the model
    ink_model: InkModel = InkModel(version=SupportedFormats.UIM_VERSION_3_1_0.value)
    # Setting a unit scale factor
    ink_model.unit_scale_factor = 1.5
    # Using a 4x4 matrix for scaling
    ink_model.transform = Matrix4x4.create_scale(1.5)
    # Properties are added as key-value pairs
    ink_model.properties.append((DOCUMENT_AUTHOR_OBJECT, "John"))
    ink_model.properties.append((DOCUMENT_LOCALE_OBJECT, "en_US"))
    ink_model.properties.append(("OtherStuff", "Yes"))
    # Create an environment
    env: Environment = Environment()
    env.properties.append(("env.name", "My Environment"))
    env.properties.append(("os.id", "98765"))
    env.properties.append(("os.name", "Windows"))
    env.properties.append(("os.version", "10.0.18362.239"))
    env.properties.append(("os.build", "239"))
    env.properties.append(("os.platform", "whatever"))
    env.add_environment_property("app.id", "123456")
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
    input_device.properties.append(("dev.id", "123454321"))
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
    assert sensor_channels_tablet[0] != sensor_channels_tablet[1]
    assert sensor_channels_tablet[0] != ink_model
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
    if with_sensor_data:
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

    # Adding view for handwriting recognition results
    hwr_tree: ViewTree = ViewTree(CommonViews.HWR_VIEW.value)
    hwr_root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    hwr_tree.root = hwr_root
    # Here you can add the same strokes as in the main tree, but you can organize them in a different way
    # (put them in different groups)
    # You are not supposed to add strokes that are not already in the main tree.
    hwr_root.add(StrokeNode(stroke_0, StrokeFragment(0, 1, 0.0, 1.0)))
    # A view node can refer to a fragment of a stroke.
    hwr_root.add(StrokeNode(stroke_1, StrokeFragment(0, 1, 0.0, 1.0)))
    node: InkNode = hwr_root.children[0]
    hwr_root.remove(node)
    hwr_tree.unregister_node(node)
    hwr_root.add(node)
    ink_model.add_view(hwr_tree)
    # The hwr root denotes a word
    ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, schema.IS, schema.SegmentationSchema.WORD))
    ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, schema.SegmentationSchema.HAS_CONTENT, "Wacom"))
    # We need a URI builder
    uri_builder: URIBuilder = URIBuilder()
    # Create a named entity
    named_entity_uri = uri_builder.build_named_entity_uri(UUIDIdentifier.id_generator())
    ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, schema.NamedEntityRecognitionSchema.HAS_NAMED_ENTITY,
                                                    named_entity_uri))
    # Add knowledge for the named entity
    ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "entityType", "Organization"))
    ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "basedIn", "Japan"))
    ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "hasConfidence", "0.85"))
    return ink_model


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


def test_spline():
    """
    Test spline structure.
    """
    spline = Spline(
        layout_mask=LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value,
        data=[],
        ts=2.,
        tf=0.
    )
    assert spline.layout_mask == LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value
    assert spline.ts == 2.
    assert spline.tf == 0.
    assert spline.data == []
    assert str(spline) == "<Spline : [mask:=11]>"


def test_identifier():
    """
    Test UUID identifier.
    """
    with pytest.raises(TypeError):
        InputDevice(identifier="Not valid")
    pen_device = InputDevice(UUIDIdentifier.id_generator())
    assert pen_device.method == IdentifiableMethod.MD5
    assert Identifier.uimid_to_h_form(None) == ""
    with pytest.raises(InkModelException):
        Identifier.str_to_uimid("Not valid")
    with pytest.raises(InkModelException):
        Identifier.from_bytes(b"12345678-1234-5678-1234-567812345678")
    uuid_identifier = UUIDIdentifier(UUIDIdentifier.id_generator())
    assert uuid_identifier.method == IdentifiableMethod.UUID
    assert str(uuid_identifier)


def test_path_point_properties():
    """
    Test path point properties structure.
    """
    path_point_properties = PathPointProperties(
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
    )
    path_point_properties_2 = PathPointProperties(
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
    )
    assert path_point_properties == path_point_properties_2
    assert path_point_properties != 1.0
    path_point_properties_2.size = 2.0
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.size = 1.0
    path_point_properties_2.red = 0.7
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.red = 0.5
    path_point_properties_2.green = 0.7
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.green = 0.5
    path_point_properties_2.blue = 0.7
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.blue = 0.5
    path_point_properties_2.alpha = 0.7
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.alpha = 1.0
    path_point_properties_2.rotation = 0.7
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.rotation = 0.0
    path_point_properties_2.scale_x = 2.0
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.scale_x = 1.0
    path_point_properties_2.scale_y = 2.0
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.scale_y = 1.0
    path_point_properties_2.scale_z = 2.0
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.scale_z = 1.0
    path_point_properties_2.offset_x = 2.0
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.offset_x = 0.0
    path_point_properties_2.offset_y = 2.0
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.offset_y = 0.0
    path_point_properties_2.offset_z = 2.0
    assert path_point_properties != path_point_properties_2
    path_point_properties_2.offset_z = 0.0


def test_style():
    """
    Test style structure.
    """
    path_point_properties = PathPointProperties(
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
    )
    # Test the properties
    assert path_point_properties.size == 1.0
    assert path_point_properties.red == 0.5
    assert path_point_properties.green == 0.5
    assert path_point_properties.blue == 0.5
    assert path_point_properties.alpha == 1.0
    assert path_point_properties.rotation == 0.0
    assert path_point_properties.scale_x == 1.0
    assert path_point_properties.scale_y == 1.0
    assert path_point_properties.scale_z == 1.0
    assert path_point_properties.offset_x == 0.0
    assert path_point_properties.offset_y == 0.0
    assert path_point_properties.offset_z == 0.0

    style = Style(
        properties=path_point_properties,
        brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush",
        particles_random_seed=0,
        render_mode_uri=BlendModeURIs.SOURCE_OVER
    )
    # Test the properties
    assert style.path_point_properties.size == 1.0
    assert style.path_point_properties.red == 0.5
    assert style.path_point_properties.green == 0.5
    assert style.path_point_properties.blue == 0.5
    assert style.path_point_properties.alpha == 1.0
    assert style.path_point_properties.rotation == 0.0
    assert style.path_point_properties.scale_x == 1.0
    assert style.path_point_properties.scale_y == 1.0
    assert style.path_point_properties.scale_z == 1.0
    assert style.path_point_properties.offset_x == 0.0
    assert style.path_point_properties.offset_y == 0.0
    assert style.path_point_properties.offset_z == 0.0
    assert style.brush_uri == "app://qa-test-app/vector-brush/MyTriangleBrush"
    assert style.particles_random_seed == 0
    assert style.render_mode_uri == BlendModeURIs.SOURCE_OVER
    assert str(style) == ('<Style : [id:=app://qa-test-app/vector-brush/MyTriangleBrush, '
                          'particles_random_seed:=0, render mode:=will://rasterization/3.0/blend-mode/SourceOver>')
    path_point_properties_2 = PathPointProperties(
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
    )
    style_other = Style(
        properties=path_point_properties_2,
        brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush",
        particles_random_seed=0,
        render_mode_uri=BlendModeURIs.SOURCE_OVER
    )
    assert style != style_other
    style_other = Style(
        properties=path_point_properties,
        brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush2",
        particles_random_seed=0,
        render_mode_uri=BlendModeURIs.SOURCE_OVER
    )
    assert style != style_other
    style_other = Style(
        properties=path_point_properties,
        brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush",
        particles_random_seed=3,
        render_mode_uri=BlendModeURIs.SOURCE_OVER
    )
    assert style != style_other
    style_other = Style(
        properties=path_point_properties,
        brush_uri="app://qa-test-app/vector-brush/MyTriangleBrush",
        particles_random_seed=0,
        render_mode_uri=BlendModeURIs.COPY
    )
    assert style != style_other
    assert style != path_point_properties


def test_knowledge_graph():
    """Creates an ink model from the scratch."""
    # Create the model
    ink_model: InkModel = create_ink_model()
    hwr_root: StrokeGroupNode = ink_model.view_root(name=CommonViews.HWR_VIEW.value)
    # Check statement filters
    assert str(ink_model.knowledge_graph)
    assert len(ink_model.knowledge_graph.all_statements_for(subject=hwr_root.uri)) == 3
    assert len(ink_model.knowledge_graph.filter(obj="Wacom")) == 1
    assert len(ink_model.knowledge_graph.filter(obj="Not found")) == 0
    assert len(ink_model.knowledge_graph.filter(predicate=schema.IS)) == 2
    for stmt in ink_model.knowledge_graph:
        assert str(stmt)
        assert stmt.subject is not None
        assert stmt.predicate is not None
        assert stmt.object is not None

    triples: List[SemanticTriple] = ink_model.knowledge_graph.filter(predicate=schema.SegmentationSchema.HAS_CONTENT,
                                                                     obj="Wacom")
    assert len(triples) == 1
    triple: SemanticTriple = triples[0]
    ink_model.remove_semantic_triple(triple.subject, triple.predicate, triple.object)
    assert len(ink_model.knowledge_graph.filter(predicate=schema.SegmentationSchema.HAS_CONTENT, obj="Wacom")) == 0
    assert (ink_model.knowledge_graph.determine_sem_type(hwr_root, typedef_pred=schema.IS)
            == schema.SegmentationSchema.WORD)
    ink_model.clear_knowledge_graph()
    assert len(ink_model.knowledge_graph.statements) == 0
    assert ink_model.knowledge_graph.determine_sem_type(hwr_root) is None


def test_semantic_triple():
    """
    Test the semantic triple structure.
    """
    uri: str = uuid.uuid4().hex
    triple: SemanticTriple = SemanticTriple(subject=uri, predicate=schema.IS,
                                            obj=schema.SegmentationSchema.WORD)
    triple_2: SemanticTriple = SemanticTriple(subject=uri, predicate=schema.IS,
                                              obj=schema.SegmentationSchema.WORD)
    assert triple == triple_2
    triple_2.predicate = schema.SegmentationSchema.HAS_CONTENT
    triple_2.object = "Wacom"
    assert triple != triple_2
    assert triple != "Different type"
    assert triple.__json__() == {
        "subject": uri,
        "predicate": schema.IS,
        "object": schema.SegmentationSchema.WORD
    }


def test_empty_ink_model():
    """
    Test the empty ink model.
    """
    ink_model: InkModel = InkModel(SupportedFormats.UIM_VERSION_3_1_0.value)
    assert not ink_model.has_ink_data()
    assert not ink_model.has_ink_structure()
    assert not ink_model.has_brushes()
    assert not ink_model.has_knowledge_graph()
    assert not ink_model.has_properties()
    assert len(ink_model.views) == 0
    assert ink_model != InkModel(SupportedFormats.UIM_VERSION_3_0_0.value)
    assert ink_model != SupportedFormats.UIM_VERSION_3_1_0
    ink_model.transform = [[1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.], [0., 0., 0., 1.]]
    ink_model_2: InkModel = InkModel(SupportedFormats.UIM_VERSION_3_1_0.value)
    ink_model_2.transform = [[2., 0., 0., 0.], [0., 2., 0., 0.], [0., 0., 2., 0.], [0., 0., 0., 1.]]
    assert ink_model != ink_model_2
    assert SupportedFormats.UIM_VERSION_3_1_0.value != ink_model
    assert str(ink_model)


def test_ink_tree():
    """
    Test the empty ink model.
    """
    ink_model: InkModel = InkModel(SupportedFormats.UIM_VERSION_3_1_0.value)
    assert ink_model.ink_tree is None
    ink_tree: InkTree = InkTree()
    assert str(ink_tree)
    with pytest.raises(InkModelException):
        ink_tree.root = None
    with pytest.raises(ValueError):
        PreOrderEnumerator(ink_tree.root)
    ink_model.add_tree(ink_tree)
    assert ink_model.ink_tree == ink_tree
    assert len(ink_model.views) == 0
    root_id: uuid.UUID = UUIDIdentifier.id_generator()
    ink_tree_2: InkTree = InkTree()
    ink_tree_2.root = StrokeGroupNode(root_id)
    root_node: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    ink_tree_2.root = root_node
    ink_tree_2.root.add(StrokeNode(Stroke(UUIDIdentifier.id_generator())))
    assert ink_tree != ink_tree_2
    ink_tree.root = StrokeGroupNode(root_id)
    ink_tree.root.add(StrokeNode(Stroke(UUIDIdentifier.id_generator())))
    assert ink_tree != ink_tree_2
    ink_tree_2.unregister_node(root_node)


def test_bounding_boxes():
    """Test to calculate bounding boxes."""
    # Create the model
    ink_model: InkModel = create_ink_model()
    hwr_root: StrokeGroupNode = ink_model.view_root(name=CommonViews.HWR_VIEW.value)
    assert hwr_root.group_bounding_box == BoundingBox(0., 0, 0, 0)
    for stroke in ink_model.ink_tree:
        assert stroke.group_bounding_box == BoundingBox(0., 0, 0, 0)

    ink_model.calculate_bounds_recursively(hwr_root)
    ink_model.calculate_bounds_recursively(ink_model.ink_tree.root)
    assert hwr_root.group_bounding_box == BoundingBox(x=10., y=10.7, width=40., height=80.3)
    enclosing = hwr_root.group_bounding_box.enclosing_bounding_box(BoundingBox(0., 0., 10., 10.))
    # The enclosing bounding box from 0., 0. and the width is 50, as the width of the stroke is 40 and the x is 10
    # so the rightmost point is 50. The height is 91.0, as the height of the stroke is 80.3 and the y is 10.7 so the
    # topmost point is 91.0
    assert enclosing == BoundingBox(0., 0., 50., 91.0)
    assert enclosing != ink_model
    for stroke in ink_model.ink_tree:
        bbox: BoundingBox = stroke.group_bounding_box
        assert bbox.x > 0.
        assert bbox.y > 0.
        assert bbox.width > 0.
        assert bbox.height > 0.
    for stroke in ink_model.view(CommonViews.HWR_VIEW.value):
        bbox: BoundingBox = stroke.group_bounding_box
        assert bbox.x > 0.
        assert bbox.y > 0.
        assert bbox.width > 0.
        assert bbox.height > 0.


def test_sensor_data():
    """
    Test the sensor data structures.
    """
    ink_model: InkModel = create_ink_model(with_sensor_data=False)
    ink_model_2: InkModel = create_ink_model(with_sensor_data=False)
    input_context = ink_model_2.input_configuration.input_contexts[0]

    # Adding additional sensor data
    sensor_data_id: uuid.UUID = UUIDIdentifier.id_generator()
    sensor_data_1: SensorData = SensorData(sensor_data_id, input_context_id=input_context.id,  state=InkState.PLANE)
    sensor_channels_tablet = ink_model.input_configuration.sensor_contexts[0].sensor_channels_contexts[0].channels
    sensor_data_1.add_timestamp_data(sensor_channels_tablet[2], [0., 0.1, 0.2, 0.3, 0.4])
    sensor_data_1.add_data(sensor_channels_tablet[0], [100.4, 103.7, 110.1])
    sensor_data_1.add_data(sensor_channels_tablet[1], [200.1, 202.0, 207.0])
    sensor_data_1.add_data(sensor_channels_tablet[3], [0.1, 0.4, 0.2])
    sensor_data_1.add_data(sensor_channels_tablet[4], [40., 51.0, 52.0])
    sensor_data_1.add_data(sensor_channels_tablet[5], [40., 51.0, 52.0])
    ink_model.sensor_data.add(sensor_data_1)
    sensor_data_2: SensorData = SensorData(sensor_data_id, input_context_id=input_context.id,
                                           state=InkState.PLANE)
    sensor_channels_tablet = ink_model_2.input_configuration.sensor_contexts[0].sensor_channels_contexts[0].channels
    sensor_data_2.add_timestamp_data(sensor_channels_tablet[2], [1., 0.1, 0.2, 0.3, 0.4])
    sensor_data_2.add_data(sensor_channels_tablet[0], [200.4, 103.7, 110.1])
    sensor_data_2.add_data(sensor_channels_tablet[1], [300.1, 202.0, 207.0])
    sensor_data_2.add_data(sensor_channels_tablet[3], [4.1, 0.4, 0.2])
    sensor_data_2.add_data(sensor_channels_tablet[4], [60., 51.0, 52.0])
    sensor_data_2.add_data(sensor_channels_tablet[5], [60., 51.0, 52.0])
    ink_model_2.sensor_data.add(sensor_data_2)
    assert ink_model.sensor_data != ink_model_2.sensor_data
    assert sensor_data_1 != sensor_data_2
    sensor_data_3: SensorData = SensorData(UUIDIdentifier.id_generator(), input_context_id=input_context.id,
                                           state=InkState.PLANE)
    sensor_channels_tablet = ink_model_2.input_configuration.sensor_contexts[0].sensor_channels_contexts[0].channels
    sensor_data_3.add_timestamp_data(sensor_channels_tablet[2], [1., 0.1, 0.2, 0.3, 0.4])
    sensor_data_3.add_data(sensor_channels_tablet[0], [200.4, 103.7, 110.1])
    sensor_data_3.add_data(sensor_channels_tablet[1], [300.1, 202.0, 207.0])
    sensor_data_3.add_data(sensor_channels_tablet[3], [4.1, 0.4, 0.2])
    sensor_data_3.add_data(sensor_channels_tablet[4], [60., 51.0, 52.0])
    sensor_data_3.add_data(sensor_channels_tablet[5], [60., 51.0, 52.0])
    assert sensor_data_2 != sensor_data_3


def test_brushes():
    """
    Test the brush structures.
    """
    ink_model: InkModel = InkModel(SupportedFormats.UIM_VERSION_3_1_0.value)
    points_1: list = [(10, 20), (0, 20), (0, 0)]
    points_2: list = [(1, 1), (0, 1), (0, 0)]
    bp_1: BrushPolygon = BrushPolygon(min_scale=0., points=points_1)
    bp_2: BrushPolygon = BrushPolygon(min_scale=0., points=points_2)
    bp_3: BrushPolygon = BrushPolygon(min_scale=1., points=points_1, indices=[0, 1, 2])
    bp_4: BrushPolygon = BrushPolygon(min_scale=1., points=points_1, indices=[0, 1, 3])
    brush_polygons: list = [bp_1, bp_2]
    # Check all variants of __eq__
    assert bp_1 != bp_2
    assert bp_1 != ink_model
    assert bp_1 != bp_3
    assert bp_3 != bp_4
    assert str(bp_1)
    assert bp_1 == bp_1
    assert bp_2 == bp_2
    assert bp_1.min_scale == 0.
    assert bp_1.points == points_1
    assert bp_2.min_scale == 0.
    assert bp_2.points == points_2
    assert bp_1.coord_x == [10, 0, 0]
    assert bp_1.coord_y == [20, 20, 0]
    assert bp_2.coord_x == [1, 0, 0]
    assert bp_2.coord_y == [1, 1, 0]

    b = BrushPolygon(min_scale=0., points=[])
    assert b.coord_x == []

    b = BrushPolygon(min_scale=0., points=[])
    assert b.coord_y == []
    assert b.coord_z == []
    assert b.indices == []

    with pytest.raises(InkModelException):
        b = BrushPolygon(min_scale=0., points=[1, 2, 3])
        assert b.coord_x

    with pytest.raises(InkModelException):
        b = BrushPolygon(min_scale=0., points=[1, 2, 3])
        assert b.coord_y

    points_3d: list = [(10, 20, 30), (0, 20, 30), (0, 0, 30)]
    bp_3: BrushPolygon = BrushPolygon(min_scale=0., points=points_3d)
    assert bp_3.coord_x == [10, 0, 0]
    assert bp_3.coord_y == [20, 20, 0]
    assert bp_3.coord_z == [30, 30, 30]

    # Create the brush object using polygons
    vector_brush_0: VectorBrush = VectorBrush(
        name="app://qa-test-app/vector-brush/MyTriangleBrush",
        prototypes=brush_polygons,
        spacing=4
    )
    assert str(vector_brush_0)
    assert vector_brush_0.name == "app://qa-test-app/vector-brush/MyTriangleBrush"
    assert vector_brush_0.spacing == 4
    assert vector_brush_0.prototypes == brush_polygons
    # Add a brush specified with shape Uris
    bpu_1: BrushPolygonUri = BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=1", min_scale=0.)
    bpu_2: BrushPolygonUri = BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=0.5", min_scale=4.)

    poly_uris: list = [
        bpu_1, bpu_2
    ]
    assert bpu_1 != bpu_2
    assert bpu_1 != ink_model
    assert bpu_1 == bpu_1
    assert bpu_2 == bpu_2
    assert str(bpu_1)
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
    assert vector_brush_0 != raster_brush_0
    assert raster_brush_0 != vector_brush_0
    # Add it to the model
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
    raster_brush_2: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.TRAJECTORY, fill_width=2.5, fill_height=0.3,
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32"
        ], randomize_fill=False, blend_mode=BlendMode.SOURCE_OVER
    )
    raster_brush_3: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.TRAJECTORY, fill_width=2.5, fill_height=0.3,
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
        ], randomize_fill=False, blend_mode=BlendMode.COPY
    )
    raster_brush_4: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.TRAJECTORY, fill_width=2.5, fill_height=0.3,
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
        ], randomize_fill=True, blend_mode=BlendMode.COPY
    )
    raster_brush_5: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.TRAJECTORY, fill_width=2.6, fill_height=0.3,
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
        ], randomize_fill=True, blend_mode=BlendMode.COPY
    )
    raster_brush_6: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.TRAJECTORY, fill_width=2.6, fill_height=0.7,
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
        ], randomize_fill=True, blend_mode=BlendMode.COPY
    )
    raster_brush_7: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.RANDOM, fill_width=2.6, fill_height=0.7,
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
        ], randomize_fill=True, blend_mode=BlendMode.COPY
    )
    raster_brush_8: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.RANDOM, fill_width=2.6, fill_height=0.7,
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
        ], randomize_fill=True, blend_mode=BlendMode.SOURCE_OVER
    )
    raster_brush_9: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.RANDOM, fill_width=2.6, fill_height=0.7,
        fill_texture=bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255]),
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
        ], randomize_fill=True, blend_mode=BlendMode.SOURCE_OVER
    )
    raster_brush_10: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.RANDOM, fill_width=2.6, fill_height=0.7,
        fill_texture=bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255]),
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGLDiff",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
        ], randomize_fill=True, blend_mode=BlendMode.SOURCE_OVER
    )
    raster_brush_11: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5., rotation=RotationMode.RANDOM, fill_width=2.6, fill_height=0.7,
        fill_texture=bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255]),
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGLDiff",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32"
        ], randomize_fill=True, blend_mode=BlendMode.SOURCE_OVER
    )
    raster_brush_12: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=14.0, scattering=5., rotation=RotationMode.RANDOM, fill_width=2.6, fill_height=0.7,
        fill_texture=bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255]),
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGLDiff",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32"
        ], randomize_fill=True, blend_mode=BlendMode.SOURCE_OVER
    )
    raster_brush_13: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=14.0, scattering=7., rotation=RotationMode.RANDOM, fill_width=2.6, fill_height=0.7,
        fill_texture=bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255]),
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGLDiff",
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32"
        ], randomize_fill=True, blend_mode=BlendMode.SOURCE_OVER
    )
    raster_brush_14: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=14.0, scattering=7., rotation=RotationMode.RANDOM, fill_width=2.6, fill_height=0.7,
        fill_texture=bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255]),
        fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGLDiff",
        shape_textures=[
            bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255])
        ],
        shape_texture_uris=[
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
            "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32"
        ], randomize_fill=True, blend_mode=BlendMode.SOURCE_OVER
    )
    # Check all variants of __eq__
    assert raster_brush_0 != raster_brush_1
    assert raster_brush_1 != raster_brush_2
    assert raster_brush_2 != raster_brush_3
    assert raster_brush_3 != raster_brush_4
    assert raster_brush_4 != raster_brush_5
    assert raster_brush_5 != raster_brush_6
    assert raster_brush_6 != raster_brush_7
    assert raster_brush_7 != raster_brush_8
    assert raster_brush_8 != raster_brush_9
    assert raster_brush_9 != raster_brush_10
    assert raster_brush_10 != raster_brush_11
    assert raster_brush_11 != raster_brush_12
    assert raster_brush_12 != raster_brush_13
    assert raster_brush_13 != raster_brush_14
    # Check add and remove
    ink_model.brushes.add_raster_brush(raster_brush_0)
    ink_model.brushes.add_raster_brush(raster_brush_1)
    ink_model.brushes.add_vector_brush(vector_brush_0)
    ink_model.brushes.add_vector_brush(vector_brush_1)
    assert len(ink_model.brushes.vector_brushes) == 2
    assert len(ink_model.brushes.raster_brushes) == 2
    assert ink_model.brushes.vector_brushes[0] == vector_brush_0
    assert ink_model.brushes.raster_brushes[0] == raster_brush_0
    ink_model.brushes.remove_vector_brush(vector_brush_1.name)
    ink_model.brushes.remove_raster_brush(raster_brush_2.name)
    assert len(ink_model.brushes.vector_brushes) == 1
    assert len(ink_model.brushes.raster_brushes) == 1
    assert str(ink_model.brushes)


def test_validate_views():
    """
    Test the view structure.
    """
    # Create the model
    ink_model: InkModel = create_ink_model()
    # Check the views
    test_tree: ViewTree = ViewTree("Test")
    test_tree_2: ViewTree = ViewTree("Test")
    assert str(test_tree)
    root_node: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    test_tree.root = root_node
    test_tree_2.root = StrokeGroupNode(UUIDIdentifier.id_generator())
    assert test_tree != test_tree_2
    with pytest.raises(InkModelException):
        test_tree.root = None
    # Remove the tree
    root_node: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    test_tree.root = root_node
    assert str(root_node)
    with pytest.raises(InkModelException):
        test_tree.root.add(root_node)
    assert test_tree.model is None
    test_tree.root.add(StrokeNode(Stroke(UUIDIdentifier.id_generator())))
    test_tree_2.root.add(StrokeNode(Stroke(UUIDIdentifier.id_generator())))
    assert test_tree != test_tree_2
    for ch in test_tree.root.children:
        assert ch.root == test_tree.root
    main_tree: InkTree = ink_model.ink_tree
    assert str(main_tree)
    hwr_tree: ViewTree = ink_model.view(CommonViews.HWR_VIEW.value)
    with pytest.raises(InkModelException):
        ink_model.add_view(hwr_tree)
    assert len(ink_model.views) == 1
    assert main_tree != ink_model
    assert main_tree != hwr_tree
    assert main_tree != test_tree
    assert str(test_tree)
    assert str(hwr_tree)
    # Remove the tree
    ink_model.remove_tree(hwr_tree.name)
    ink_model.remove_tree(ink_model.ink_tree.name)
    assert ink_model.ink_tree is None
    assert len(ink_model.views) == 0
    # Remove a non-existing tree
    ink_model.remove_tree("Not found")
    # Add the view to the model
    ink_model.add_view(hwr_tree)
    ink_model.add_tree(main_tree)
    with pytest.raises(InkModelException):
        ink_model.add_tree(InkTree())
    assert len(ink_model.views) == 1
    assert ink_model.ink_tree is not None
    assert hwr_tree.model == ink_model
    ink_model.clear_views()
    assert len(ink_model.views) == 0
    ink_model.add_view(hwr_tree)
    assert len(ink_model.views) == 1
    with pytest.raises(KeyError):
        ink_model.view("Not found")
    ink_model.remove_node(main_tree.root.children[0])


def test_validate_serialise_deserialize():
    """Creates an ink model from the scratch."""
    # Create the model
    ink_model: InkModel = create_ink_model()
    # Save the model, this will overwrite an existing file
    new_model_3_1_0: InkModel = UIMParser().parse(UIMEncoder310().encode(ink_model))
    assert ink_model == new_model_3_1_0


def test_uri_builder():
    """
    Test the URI builder.
    """
    builder: URIBuilder = URIBuilder()
    model_id: uuid.UUID = UUIDIdentifier.id_generator()
    gen_uri: str = builder.build_uri(sub_path='sub', model_id=model_id)
    assert gen_uri == f'uim:{model_id}/sub/'
    gen_uri = builder.build_uri(sub_path='sub')
    assert gen_uri == f'uim:sub/'
    with pytest.raises(InkModelException):
        builder.build_named_entity_uri(uimid='uim:sub/', model_id=model_id)
    named_entity_id: uuid.UUID = UUIDIdentifier.id_generator()
    gen_uri = builder.build_named_entity_uri(uimid=named_entity_id, model_id=model_id)
    assert gen_uri == f'uim:{model_id}/ne/{named_entity_id}'
    stroke_uuid: uuid.UUID = UUIDIdentifier.id_generator()
    stroke_uri: str = builder.build_stroke_uri(stroke_uuid)
    assert stroke_uri == f'uim:stroke/{stroke_uuid}'
    ink_node: InkNode = StrokeNode(Stroke(UUIDIdentifier.id_generator()))
    ink_node.transient_tag = "tag"
    assert ink_node.transient_tag == "tag"
    with pytest.raises(InkModelException):
        assert ink_node.root
    assert str(ink_node)
    with pytest.raises(InkModelException):
        builder.build_node_uri(ink_node, SupportedFormats.UIM_VERSION_3_1_0)
    tree_uri = builder.build_tree_uri("test")
    assert tree_uri == "uim:tree/test"
    with pytest.raises(InkModelException):
        builder.build_node_uri(model_id, SupportedFormats.UIM_VERSION_3_1_0)
    builder.build_entity_uri(uimid=UUIDIdentifier.id_generator(), model_id=model_id)
    with pytest.raises(InkModelException):
        builder.build_entity_uri(uimid="uim:sub/", model_id=model_id)


def test_model_strokes():
    """
    Test the strokes in the model.
    """
    ink_model: InkModel = create_ink_model()
    # Get all strokes
    hwr_strokes = ink_model.collect_strokes(ink_model.views[0])
    assert len(hwr_strokes) == 2
    main_strokes = ink_model.collect_strokes(ink_model.ink_tree)
    assert len(main_strokes) == 3

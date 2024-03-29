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
import math
import uuid

from uim.codec.parser.uim import UIMParser
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.base import UUIDIdentifier, Identifier, InkModelException
from uim.model.ink import InkModel, InkTree
from uim.model.inkdata.brush import VectorBrush, BrushPolygon, BrushPolygonUri, RasterBrush, RotationMode, BlendMode
from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask, PathPointProperties
from uim.model.inkinput.inputdata import Environment, InkInputProvider, InkInputType, InputDevice, SensorChannel, \
    InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext
from uim.model.inkinput.sensordata import SensorData, InkState
from uim.model.semantics import schema
from uim.model.semantics.node import StrokeGroupNode, StrokeNode, StrokeFragment, URIBuilder
from uim.model.semantics.schema import SemanticTriple, CommonViews, HAS_NAMED_ENTITY
from uim.utils.matrix import Matrix4x4


def test_color_conversation():
    """Validate that the UimID can be converted from s-form to byte array."""
    color: int = -1  # white color
    r, g, b, a = PathPointProperties.color(color)
    c2: int = PathPointProperties.rgba(r, g, b, a)
    assert math.isclose(color, c2, rel_tol=0.1, abs_tol=0.0)
    red: float = 0.3
    green: float = 0.3
    blue: float = 0.3
    alpha: float = 1.
    color: int = PathPointProperties.rgba(red, green, blue, alpha)
    r2, g2, b2, a2 = PathPointProperties.color(color)
    assert math.isclose(red, r2, rel_tol=0.1, abs_tol=0.0)
    assert math.isclose(green, g2, rel_tol=0.1, abs_tol=0.0)
    assert math.isclose(blue, b2, rel_tol=0.1, abs_tol=0.0)
    assert math.isclose(alpha, a2, rel_tol=0.1, abs_tol=0.0)


def test_uimid_s_form_conversation():
    """Validate that the UimID can be converted from s-form to byte array."""
    uimid: uuid.UUID = UUIDIdentifier.id_generator()
    uimid_object: UUIDIdentifier = UUIDIdentifier(uimid)
    uimid_conv: uuid.UUID = UUIDIdentifier.str_to_uimid(uimid_object.id_s_form)
    assert uimid == uimid_conv


def test_uimid_h_form_conversation():
    """Validate that the UimID can be converted from s-form to byte array."""
    uimid: uuid.UUID = UUIDIdentifier.id_generator()
    uimid_object: UUIDIdentifier = UUIDIdentifier(uimid)
    assert uimid_object.id_s_form == uimid_object.id_h_form.replace('-', '')
    uimid_conv: uuid.UUID = UUIDIdentifier.str_to_uimid(uimid_object.id_h_form)
    assert uimid == uimid_conv


def test_uuid():
    uuid_str: str = 'd40ca4a8b8987d79895e62020fbc219c'
    uuid_obj: uuid.UUID = UUIDIdentifier.str_to_uimid(uuid_str)
    id_s_form: str = Identifier.uimid_to_s_form(uuid_obj)
    assert uuid_str == id_s_form
    uuid_2_str: str = '6d586b07-87b0-4a29-b9a0-7de8d0219bae'
    uuid_2_obj: uuid.UUID = UUIDIdentifier.str_to_uimid(uuid_2_str)
    id_h_form: str = str(uuid_2_obj)
    assert uuid_2_str == id_h_form


def test_create_ink_model():
    """Creates an ink model from the scratch."""
    # Create the model
    ink_model: InkModel = InkModel()
    # Setting a unit scale factor
    ink_model.unit_scale_factor = 1.5
    # Using a 4x4 matrix for scaling
    ink_model.transform = Matrix4x4.create_scale(1.5)

    # Properties are added as key-value pairs
    ink_model.properties.append(("Author", "John"))
    ink_model.properties.append(("PrimaryLanguage", "en_US"))
    ink_model.properties.append(("OtherStuff", "Yes"))

    # Create an environment
    env: Environment = Environment()
    env.properties.append(("env.name", "My Environment"))
    env.properties.append(("os.id", "98765"))
    env.properties.append(("os.name", "Windows"))
    env.properties.append(("os.version", "10.0.18362.239"))
    env.properties.append(("os.build", "239"))
    env.properties.append(("os.platform", "whatever"))
    ink_model.input_configuration.environments.append(env)

    # Ink input provider can be pen, mouse or touch.
    provider: InkInputProvider = InkInputProvider(input_type=InkInputType.MOUSE)
    provider.properties.append(("pen.id", "1234567"))
    ink_model.input_configuration.ink_input_providers.append(provider)

    # Input device is the sensor (pen tablet, screen, etc.)
    input_device: InputDevice = InputDevice()
    input_device.properties.append(("dev.id", "123454321"))
    input_device.properties.append(("dev.manufacturer", "Wacom"))
    input_device.properties.append(("dev.model", "Mobile Studio Pro"))
    input_device.properties.append(("dev.cpu", "Intel"))
    input_device.properties.append(("dev.graphics.display", "Dell 1920x1080 32bit"))
    input_device.properties.append(("dev.graphics.adapter", "NVidia"))
    ink_model.input_configuration.devices.append(input_device)

    # Create a group of sensor channels
    sensor_channels_tablet: list = [
        SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0)
    ]

    scc_tablet: SensorChannelsContext = SensorChannelsContext(channels=sensor_channels_tablet,
                                                              ink_input_provider_id=provider.id,
                                                              input_device_id=input_device.id)

    # We can create an additional input device, for example one providing pressure via Bluetooth
    input_device_bluetooth: InputDevice = InputDevice()
    input_device_bluetooth.properties.append(("dev.id", "345456567"))
    input_device_bluetooth.properties.append(("dev.manufacturer", "Apple"))
    ink_model.input_configuration.devices.append(input_device_bluetooth)

    sensor_channels_bluetooth: list = [
        SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
        SensorChannel(channel_type=InkSensorType.PRESSURE, metric=InkSensorMetricType.FORCE, resolution=1.0),
    ]

    scc_bluetooth: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_bluetooth.id,
                                                                 channels=sensor_channels_bluetooth)

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

    sensor_data_0.add_timestamp_data(sensor_channels_tablet[0], [0, 1, 2, 4, 5])
    sensor_data_0.add_data(sensor_channels_tablet[1], [100.4, 103.7, 110.1])
    sensor_data_0.add_data(sensor_channels_tablet[2], [200.1, 202.0, 207.0])

    sensor_data_0.add_timestamp_data(sensor_channels_bluetooth[0], [0, 1, 2])

    sensor_data_0.add_data(sensor_channels_bluetooth[1], [100, 200])

    # Add sensor data to the model
    ink_model.sensor_data.add(sensor_data_0)

    # We need to define a brush polygon
    points: list = [(10, 10), (0, 10), (0, 0)]
    brush_polygons: list = [BrushPolygon(min_scale=0., points=points)]

    # Create the brush object using polygons
    vector_brush_0: VectorBrush = VectorBrush(
        "app://qa-test-app/vector-brush/MyTriangleBrush",
        brush_polygons)

    # Add it to the model
    ink_model.brushes.add_vector_brush(vector_brush_0)

    # Add a brush specified with shape Uris
    poly_uris: list = [
        BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=1}", 0.),
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

    # Add it to the model
    ink_model.brushes.add_raster_brush(raster_brush_0)

    raster_brush_1: RasterBrush = RasterBrush(
        name="app://qa-test-app/raster-brush/MyRasterBrush1",
        spacing=10.0, scattering=5.0, rotation=RotationMode.TRAJECTORY, fill_width=2., fill_height=0.3,
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
    style.path_point_properties.blue = 0.4
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

    # Create a style
    style_1: Style = Style(brush_uri=raster_brush_0.name)
    style_1.path_point_properties.rotation = 0.35

    # The render mode URI can also be app specific like app://blabla
    # The URI will://rasterization/3.0/blend-mode/SourceOver is assumed and must not be set.
    style_1.render_mode_uri = "will://rasterization/3.0/blend-mode/DestinationOver"

    # Create a stroke object. Note that it just exists, but is not in the model yet.
    stroke_1: Stroke = Stroke(UUIDIdentifier.id_generator(), spline=spline_1, style=style_1)

    # First you need a root group to contain the strokes
    root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())

    # Assign the group as the root of the main ink tree
    ink_model.ink_tree = InkTree()
    ink_model.ink_tree.root = root

    # Add a node for stroke 0
    stroke_node_0: StrokeNode = StrokeNode(stroke_0, StrokeFragment(0, 1, 0.0, 1.0))
    root.add(stroke_node_0)

    # Add a node for stroke 1
    root.add(StrokeNode(stroke_1, StrokeFragment(0, 1, 0.0, 1.0)))

    # Adding view for handwriting recognition results
    hwr_tree: InkTree = InkTree(CommonViews.HWR_VIEW.value)
    ink_model.add_view(hwr_tree)

    hwr_root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    hwr_tree.root = hwr_root

    # Here you can add the same strokes as in the main tree, but you can organize them in a different way
    # (put them in different groups)
    # You are not supposed to add strokes that are not already in the main tree.
    hwr_root.add(StrokeNode(stroke_0, StrokeFragment(0, 1, 0.0, 1.0)))

    # A view node can refer to a fragment of a stroke.
    hwr_root.add(StrokeNode(stroke_1, StrokeFragment(0, 1, 0.0, 1.0)))

    # The hwr root denotes a word
    ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, schema.CommonRDF.PRED_RDF_HAS_TYPE,
                                                    schema.WORD))
    ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, schema.IS, "Wacom"))

    # We need an URI builder
    uri_builder: URIBuilder = URIBuilder()

    # Create a named entity
    named_entity_uri = uri_builder.build_named_entity_uri(UUIDIdentifier.id_generator())
    ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, HAS_NAMED_ENTITY, named_entity_uri))

    # Add knowledge for the named entity
    ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "entityType", "Organization"))
    ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "basedIn", "Japan"))
    ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "hasConfidence", "0.85"))

    # Save the model, this will overwrite an existing file
    new_model_3_1_0: InkModel = UIMParser().parse(UIMEncoder310().encode(ink_model))

    assert ink_model == new_model_3_1_0
    assert ink_model.sensor_data.sensor_data_by_id(sensor_data_id) is not None
    try:
        ink_model.sensor_data.sensor_data_by_id(UUIDIdentifier.id_generator())
        raise Exception("Sensor data is not available. Exception should have been thrown.")
    except InkModelException:
        pass

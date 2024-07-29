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
import logging
import sys
import uuid
from abc import ABC
from typing import List, Any, Dict, Tuple, Optional, Union

import numpy

from uim.codec.context.version import Version
from uim.model.base import InkModelException, UUIDIdentifier, node_registration_debug
from uim.model.helpers.policy import HandleMissingDataPolicy
from uim.model.helpers.treeiterator import PreOrderEnumerator
from uim.model.inkdata.brush import Brushes
from uim.model.inkdata.strokes import Stroke, InkStrokeAttributeType, DEFAULT_EXTENDED_LAYOUT
from uim.model.inkinput.inputdata import SensorChannel, \
    InkSensorType, InkSensorMetricType, InputContext, InputContextRepository
from uim.model.inkinput.sensordata import SensorData, ChannelData
from uim.model.semantics import schema
from uim.model.semantics.node import InkNode, BoundingBox, StrokeNode, StrokeGroupNode, StrokeFragment
from uim.model.semantics.schema import CommonViews, SemanticTriple

# Create the Logger
logger: Optional[logging.Logger] = None

if logger is None:
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    logger.info('Completed configuring logger()!')


class SensorDataRepository(ABC):
    """
    SensorDataRepository
    ====================
    A collection of data repositories, holding raw sensor input, input device/provider configurations, sensor channel
    configurations, etc. Each data repository keeps certain data-sets isolated and is responsible for
    specific type(s) of data.

    Parameters
    ----------
    sensor_data: List[SensorData]
            List of sensor data items. [optional]
    """

    def __init__(self, sensor_data: List[SensorData] = None):
        self.__sensor_data: List[SensorData] = sensor_data or []
        self.__map_id: Dict[uuid.UUID, int] = {}

    @property
    def sensor_data(self) -> List[SensorData]:
        """List of SensorData objects. (`List[SensorData]`)"""
        return self.__sensor_data

    @sensor_data.setter
    def sensor_data(self, sensor_data: list):
        self.__sensor_data = sensor_data
        self.__build_idx_map()

    def add(self, sensor_data: SensorData):
        """
        Adding a sensor sample.

        Parameters
        ----------
        sensor_data: `SensorData`
            Adding a sensor data sample
        """
        self.__sensor_data.append(sensor_data)
        self.__map_id[sensor_data.id] = len(self.__sensor_data) - 1

    def sensor_data_by_id(self, uimid: uuid.UUID) -> SensorData:
        """
        Returns the sensor data samples for a specific id.

        Parameters
        ----------
        uimid: `UUID`
            Id of the sensor data

        Returns
        -------
        instance: `SensorData`
            instance of the sensor data sample

        Raises
        ------
        InkModelException
            If `SensorData` for the id is not available.
        """
        if uimid not in self.__map_id:
            raise InkModelException(f'No sensor data with id:={uimid}')
        return self.__sensor_data[self.__map_id[uimid]]

    def __build_idx_map(self):
        """Building an index to map the UUID to index in a list."""
        self.__map_id = {}
        for idx, el in enumerate(self.sensor_data):
            self.__map_id[el.id] = idx

    def __dict__(self):
        return {
            'sensor_data': [sd.__dict__() for sd in self.sensor_data]
        }

    def __json__(self):
        return self.__dict__()

    def __iter__(self):
        return iter(self.sensor_data)

    def __eq__(self, other: Any):
        if not isinstance(other, SensorDataRepository):
            logger.warning(f"Comparing SensorDataRepository with incompatible type {type(other)}")
            return False
        if len(self.sensor_data) != len(other.sensor_data):
            logger.warning(f"SensorDataRepository sensor data length not equal.")
            return False
        for s1, s2 in zip(self.sensor_data, other.sensor_data):
            if s1 != s2:
                logger.warning(f"SensorDataRepository sensor data not equal.")
                return False
        return True

    def __repr__(self):
        return f'<InputData : [sensor:={self.__sensor_data}]>'


class InkTree(ABC):
    """
    InkTree
    =======
    The digital ink content, contained within a universal ink model, is organized in logical trees of ink nodes -
    they represent hierarchically organized ink-centric structures, and are also referred to as ink trees.

    Parameters
    ----------
    name: str -
        Name of the view
    """

    def __init__(self, name: str = CommonViews.MAIN_INK_TREE.value):
        self.__name: str = name
        self.__model: Optional[InkModel] = None
        self.__root: Optional[StrokeGroupNode] = None

    @property
    def model(self) -> 'InkModel':
        """Reference to the model. (`InkModel`)"""
        return self.__model

    @model.setter
    def model(self, value: 'InkModel'):
        self.__model = value

    @property
    def name(self) -> str:
        """The primary name associated with this ink tree. (`str`, read-only)"""
        return self.__name

    @property
    def root(self) -> StrokeGroupNode:
        """Root node of the tree. (`StrokeGroupNode`)"""
        return self.__root

    @root.setter
    def root(self, root: StrokeGroupNode):
        if root is None:
            logger.error(f"Root node cannot be None.")
            raise InkModelException(f"Root node cannot be set to None.")
        root.__assert_not_owned__()
        if self.__root is not None:
            self.unregister_sub_tree(self.__root)
            self.__root = None
        self.register_sub_tree(root)
        self.__root = root

    def __iter__(self):
        return PreOrderEnumerator(self.__root)

    def register_node(self, node: InkNode):
        """
        Register node.

        Parameters
        ----------
        node: `InkNode`
            Node that needs to be registered
        """
        if self.model is None:
            logger.warning(f"InkTree with name {self.name} not yet attached to a model.")

        node.tree = self

        if self.model is not None:
            self.__model.register_node(node)

    def unregister_node(self, node: InkNode):
        """
        Unregister node.

        Parameters
        ----------
        node: `InkNode`
            Node that needs to be unregistered
        """
        if self.__model is not None:
            self.__model.unregister_node(node)

    def register_sub_tree(self, node: InkNode):
        """
        Register sub tree.

        Parameters
        ----------
        node: `InkNode`
            Sub tree that needs to be registered
        """
        if node.child_nodes_count() == 0:
            self.register_node(node)
        else:
            for n in PreOrderEnumerator(node):
                self.register_node(n)

    def unregister_sub_tree(self, node: InkNode):
        """
        Unregister sub tree.

        Parameters
        ----------
        node: `InkNode`
            Sub tree that needs to be unregistered
        """
        if node.child_nodes_count() == 0:
            self.unregister_node(node)
        else:
            for n in PreOrderEnumerator(node):
                self.unregister_node(n)

    def __dict__(self):
        return {
            'name': self.name,
            'root': self.root.__dict__()
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, InkTree):
            logger.warning(f"Comparing InkTree with incompatible type {type(other)}")
            return False
        if self.name != other.name:
            logger.warning(f"InkTree names do not match: {self.name} != {other.name}")
            return False
        if self.root is not None and other.root is not None:
            for n1, n2 in zip(PreOrderEnumerator(self.root), PreOrderEnumerator(other.root)):
                if n1 != n2:
                    logger.warning(f"InkTree nodes do not match: {n1} != {n2}")
                    return False
        if self.root != other.root:
            logger.warning(f"InkTree roots do not match: {self.root} != {other.root}")
            return False
        return True

    def __repr__(self):
        if self.__root:
            return f'<Ink Tree: [name:={self.name},  root id:={self.root}]>'
        return f'<Ink Tree: [name:={self.name}] - Empty tree'


class ViewTree(InkTree):
    """
    View tree
    ----------
    The view is a tree structure.
    """

    def __init__(self, name: str):
        super().__init__(name=name)

    def __repr__(self):
        return f'<View Tree: [name:={self.name},  root id:={self.root}]>'


class InkModel(ABC):
    """
    InkModel
    ========
    The Ink Model has the following logical sections:

    - **Data repositories** - a collection of data repositories, holding raw sensor input,
                              input device/provider configurations, splines, sensor channel configurations,
                              rendering configurations, etc. Each data repository keeps certain data-set isolated
                              and is responsible for specific type(s) of data.
    - **Logical data trees** - a collection of logical trees, representing structures of hierarchically
                               organized strokes.
    - **Semantic triple store** - an RDF/WODL compliant triple store, holding semantic information.

    Parameters
    ----------
    version: Optional[Version]
            Version of the source (ink content file).

    Examples
    --------
    >>> from uim.codec.parser.uim import UIMParser
    >>> from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
    >>> from uim.model.base import UUIDIdentifier, Identifier, InkModelException
    >>> from uim.model.ink import InkModel, InkTree
    >>> from uim.model.inkdata.brush import VectorBrush, BrushPolygon, BrushPolygonUri, RasterBrush, RotationMode, \
    >>>      BlendMode
    >>> from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask, PathPointProperties
    >>> from uim.model.inkinput.inputdata import Environment, InkInputProvider, InkInputType, InputDevice, \
    >>>      SensorChannel, \
    >>>     InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext
    >>> from uim.model.inkinput.sensordata import SensorData, InkState
    >>> from uim.model.semantics import schema
    >>> from uim.model.semantics.node import StrokeGroupNode, StrokeNode, StrokeFragment, URIBuilder
    >>> from uim.model.semantics.schema import SemanticTriple, CommonViews, HAS_NAMED_ENTITY
    >>> from uim.utils.matrix import Matrix4x4
    >>> # Creates an ink model from the scratch.
    >>> ink_model: InkModel = InkModel()
    >>> # Setting a unit scale factor
    >>> ink_model.unit_scale_factor = 1.5
    >>> # Using a 4x4 matrix for scaling
    >>> ink_model.transform = Matrix4x4.create_scale(1.5)
    >>>
    >>> # Properties are added as key-value pairs
    >>> ink_model.properties.append(("Author", "John"))
    >>> ink_model.properties.append(("PrimaryLanguage", "en_US"))
    >>> ink_model.properties.append(("OtherStuff", "Yes"))
    >>>
    >>> # Create an environment
    >>> env: Environment = Environment()
    >>> env.properties.append(("env.name", "My Environment"))
    >>> env.properties.append(("os.id", "98765"))
    >>> env.properties.append(("os.name", "Windows"))
    >>> env.properties.append(("os.version", "10.0.18362.239"))
    >>> env.properties.append(("os.build", "239"))
    >>> env.properties.append(("os.platform", "whatever"))
    >>> ink_model.input_configuration.environments.append(env)
    >>>
    >>> # Ink input provider can be pen, mouse or touch.
    >>> provider: InkInputProvider = InkInputProvider(input_type=InkInputType.MOUSE)
    >>> provider.properties.append(("pen.id", "1234567"))
    >>> ink_model.input_configuration.ink_input_providers.append(provider)
    >>>
    >>> # Input device is the sensor (pen tablet, screen, etc.)
    >>> input_device: InputDevice = InputDevice()
    >>> input_device.properties.append(("dev.id", "123454321"))
    >>> input_device.properties.append(("dev.manufacturer", "Wacom"))
    >>> input_device.properties.append(("dev.model", "Mobile Studio Pro"))
    >>> input_device.properties.append(("dev.cpu", "Intel"))
    >>> input_device.properties.append(("dev.graphics.display", "Dell 1920x1080 32bit"))
    >>> input_device.properties.append(("dev.graphics.adapter", "NVidia"))
    >>> ink_model.input_configuration.devices.append(input_device)
    >>>
    >>> # Create a group of sensor channels
    >>> sensor_channels: list = [
    >>>     SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
    >>>     SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
    >>>     SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0)
    >>> ]
    >>>
    >>> scc_tablet: SensorChannelsContext = SensorChannelsContext(channels=sensor_channels,
    >>>                                                           ink_input_provider_id=provider.id,
    >>>                                                           input_device_id=input_device.id)
    >>>
    >>> # We can create an additional input device, for example one providing pressure via Bluetooth
    >>> input_device_bluetooth: InputDevice = InputDevice()
    >>> input_device_bluetooth.properties.append(("dev.id", "345456567"))
    >>> input_device_bluetooth.properties.append(("dev.manufacturer", "Apple"))
    >>> ink_model.input_configuration.devices.append(input_device_bluetooth)
    >>>
    >>> sensor_channels_bluetooth: list = [
    >>>     SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
    >>>     SensorChannel(channel_type=InkSensorType.PRESSURE, metric=InkSensorMetricType.FORCE, resolution=1.0),
    >>> ]
    >>>
    >>> scc_bluetooth: SensorChannelsContext = SensorChannelsContext(input_device_id=input_device_bluetooth.id,
    >>>                                                              channels=sensor_channels_bluetooth)
    >>>
    >>> # Add all sensor channel contexts
    >>> sensor_context: SensorContext = SensorContext()
    >>> sensor_context.add_sensor_channels_context(scc_tablet)
    >>> sensor_context.add_sensor_channels_context(scc_bluetooth)
    >>> ink_model.input_configuration.sensor_contexts.append(sensor_context)
    >>>
    >>> # Create the input context using the Environment and the Sensor Context
    >>> input_context: InputContext = InputContext(environment_id=env.id, sensor_context_id=sensor_context.id)
    >>> ink_model.input_configuration.input_contexts.append(input_context)
    >>>
    >>> # Create sensor data
    >>> sensor_data_0: SensorData = SensorData(UUIDIdentifier.id_generator(), input_context_id=input_context.id,
    >>>                                        state=InkState.PLANE)
    >>>
    >>> sensor_data_0.add_timestamp_data(sensor_channels[0], [0, 1, 2, 4, 5])
    >>> sensor_data_0.add_data(sensor_channels[1],  [100.4, 103.7, 110.1])
    >>> sensor_data_0.add_data(sensor_channels[2],  [200.1, 202.0, 207.0])
    >>>
    >>> sensor_data_0.add_timestamp_data(sensor_channels_bluetooth[0], [0, 1, 2])
    >>>
    >>> sensor_data_0.add_data(sensor_channels_bluetooth[1], [100, 200])
    >>>
    >>> # Add sensor data to the model
    >>> ink_model.sensor_data.add(sensor_data_0)
    >>>
    >>> # We need to define a brush polygon
    >>> points: list = [(10, 10), (0, 10), (0, 0)]
    >>> brush_polygons: list = [BrushPolygon(min_scale=0., points=points)]
    >>>
    >>> # Create the brush object using polygons
    >>> vector_brush_0: VectorBrush = VectorBrush(
    >>>     "app://qa-test-app/vector-brush/MyTriangleBrush",
    >>>     brush_polygons)
    >>>
    >>> # Add it to the model
    >>> ink_model.brushes.add_vector_brush(vector_brush_0)
    >>>
    >>> # Add a brush specified with shape Uris
    >>> poly_uris: list = [
    >>>     BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=1", 0.),
    >>>     BrushPolygonUri("will://brush/3.0/shape/Ellipse?precision=20&radiusX=1&radiusY=0.5", 4.0)
    >>> ]
    >>>
    >>> vector_brush_1: VectorBrush = VectorBrush(
    >>>     "app://qa-test-app/vector-brush/MyEllipticBrush",
    >>>     poly_uris)
    >>>
    >>> raster_brush_0: RasterBrush = RasterBrush(
    >>>     name="app://qa-test-app/raster-brush/MyRasterBrush",
    >>>     spacing=10., scattering=5., rotation=RotationMode.TRAJECTORY, shape_textures=[bytes([10, 20]),
    >>>                                                                                   bytes([30, 20])],
    >>>     fill_width=2.0, fill_height=0.3,
    >>>     fill_texture=bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255]),
    >>>     randomize_fill=False, blend_mode=BlendMode.SOURCE_OVER)
    >>>
    >>> # Add it to the model
    >>> ink_model.brushes.add_raster_brush(raster_brush_0)
    >>>
    >>> raster_brush_1: RasterBrush = RasterBrush(
    >>>     name="app://qa-test-app/raster-brush/MyRasterBrush1",
    >>>     spacing=10.0, scattering=5.0, rotation=RotationMode.TRAJECTORY, fill_width=2., fill_height=0.3,
    >>>     fill_texture_uri="app://qa-test-app/raster-brush-fill/mixedShapesGL",
    >>>     shape_texture_uris=[
    >>>         "app://qa-test-app/raster-brush-shape/mixedShapesGL_128x128",
    >>>         "app://qa-test-app/raster-brush-shape/mixedShapesGL_64x64",
    >>>         "app://qa-test-app/raster-brush-shape/mixedShapesGL_32x32",
    >>>         "app://qa-test-app/raster-brush-shape/mixedShapesGL_16x16"
    >>>     ], randomize_fill=False, blend_mode=BlendMode.SOURCE_OVER)
    >>>
    >>> ink_model.brushes.add_raster_brush(raster_brush_1)
    >>> ink_model.brushes.add_vector_brush(vector_brush_1)
    >>>
    >>> # Specify the layout of the stroke data, in this case the stroke will have variable X, Y and Size properties.
    >>> layout_mask: int = LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value
    >>>
    >>> # Provide the stroke data - in this case 4 data points, each consisting of X, Y, Size
    >>> path: list = [
    >>>     10., 10.7, 1.0,
    >>>     21.0, 20.2, 2.0,
    >>>     30.0, 12.4, 2.1,
    >>>     40.0, 15.0, 1.5
    >>> ]
    >>> # Create a spline object from the path data
    >>> spline: Spline = Spline(layout_mask, path)
    >>>
    >>> # Create some style
    >>> style: Style = Style(brush_uri=vector_brush_0.name)
    >>> style.path_point_properties.red = 1.0
    >>> style.path_point_properties.green = 0.0
    >>> style.path_point_properties.blue = 0.4
    >>> style.path_point_properties.alpha = 1.0
    >>>
    >>> # Create a stroke object. Note that it just exists, but is not in the model yet.
    >>> stroke_0: Stroke = Stroke(sid=UUIDIdentifier.id_generator(), spline=spline, style=style)
    >>> # Create a spline object - 9 data points, each consisting of X, Y, Size, Red, Green, Blue, Alpha
    >>> spline_1: Spline = Spline(
    >>>     LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value | LayoutMask.RED.value | \
    >>>     LayoutMask.GREEN.value
    >>>     | LayoutMask.BLUE.value | LayoutMask.ALPHA.value,
    >>>     [10.0, 10.7, 1.0, 0.5, 0.0, 0.1, 1.0,
    >>>      21.0, 20.2, 2.0, 0.9, 0.4, 0.2, 0.8,
    >>>      30.0, 12.4, 2.1, 0.7, 0.1, 0.1, 0.7,
    >>>      40.0, 15.0, 1.5, 0.3, 0.5, 0.4, 1.0,
    >>>      50.0, 45.0, 1.0, 0.3, 0.5, 0.4, 1.0,
    >>>      41.0, 53.0, 1.1, 0.2, 0.3, 0.5, 0.9,
    >>>      33.0, 73.0, 1.2, 0.6, 0.7, 0.4, 0.8,
    >>>      20.0, 84.0, 1.3, 0.7, 0.8, 0.3, 0.7,
    >>>      10.0, 91.0, 1.1, 0.7, 0.9, 0.2, 0.6]
    >>> )
    >>>
    >>> # Create a style
    >>> style_1: Style = Style(brush_uri=raster_brush_0.name)
    >>> style_1.path_point_properties.rotation = 0.35
    >>>
    >>> # The render mode URI can also be app specific like app://blabla
    >>> # The URI will://rasterization/3.0/blend-mode/SourceOver is assumed and must not be set.
    >>> style_1.render_mode_uri = "will://rasterization/3.0/blend-mode/DestinationOver"
    >>>
    >>> # Create a stroke object. Note that it just exists, but is not in the model yet.
    >>> stroke_1: Stroke = Stroke(UUIDIdentifier.id_generator(), spline=spline_1, style=style_1)
    >>>
    >>> # First you need a root group to contain the strokes
    >>> root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    >>>
    >>> # Assign the group as the root of the main ink tree
    >>> ink_model.ink_tree = InkTree()
    >>> ink_model.ink_tree.root = root
    >>>
    >>> # Add a node for stroke 0
    >>> stroke_node_0: StrokeNode = StrokeNode(stroke_0, StrokeFragment(0, 1, 0.0, 1.0))
    >>> root.add(stroke_node_0)
    >>>
    >>> # Add a node for stroke 1
    >>> root.add(StrokeNode(stroke_1, StrokeFragment(0, 1, 0.0, 1.0)))
    >>>
    >>> # Adding view for handwriting recognition results
    >>> hwr_tree: InkTree = InkTree(CommonViews.HWR_VIEW.value)
    >>> # Add view right after creation, to avoid warnings that tree is not yet attached
    >>> ink_model.add_view(hwr_tree)
    >>>
    >>> hwr_root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    >>> hwr_tree.root = hwr_root
    >>>
    >>> # Here you can add the same strokes as in the main tree, but you can organize them in a different way
    >>> # (put them in different groups)
    >>> # You are not supposed to add strokes that are not already in the main tree.
    >>> hwr_root.add(StrokeNode(stroke_0, StrokeFragment(0, 1, 0.0, 1.0)))
    >>>
    >>> # A view node can refer to a fragment of a stroke.
    >>> hwr_root.add(StrokeNode(stroke_1, StrokeFragment(0, 1, 0.0, 1.0)))
    >>>
    >>> # The hwr root denotes a word
    >>> ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, schema.CommonRDF.PRED_RDF_HAS_TYPE,
    >>>                                  schema.SegmentationSchema.WORD))
    >>> ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, schema.SegmentationSchema.HAS_CONTENT, "Wacom"))
    >>>
    >>> # We need an URI builder
    >>> uri_builder: URIBuilder = URIBuilder()
    >>>
    >>> # Create a named entity
    >>> named_entity_uri: str = uri_builder.build_named_entity_uri(UUIDIdentifier.id_generator())
    >>> ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri,
    >>>                                                 schema.NamedEntityRecognitionSchema.HAS_NAMED_ENTITY,
    >>>                                                 named_entity_uri))
    >>>
    >>> # Add knowledge for the named entity
    >>> ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "entityType", "Organization"))
    >>> ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "basedIn", "Japan"))
    >>> ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "hasConfidence", "0.85"))
    """

    def __init__(self, version: Optional[Version] = None):
        self.__input_data: SensorDataRepository = SensorDataRepository()
        self.__version: Version = version
        self.__brushes: Brushes = Brushes()
        self.__ink_tree: Optional[InkTree] = None
        self.__views: List[ViewTree] = []
        self.__knowledge_graph: schema.TripleStore = schema.TripleStore()
        self.__transform: numpy.ndarray = numpy.identity(4, dtype=float)
        self.__default_transform: bool = True
        self.__properties: List[Tuple[str, str]] = []
        self.__unit_scale_factor: float = 1.
        self.__input_configuration: InputContextRepository = InputContextRepository()
        self.__map: Dict[str, InkNode] = {}

    @property
    def version(self) -> Version:
        """Version of ink content file used to create the model. (`Version`, read-only)"""
        return self.__version

    @property
    def input_configuration(self) -> InputContextRepository:
        """Input context data repository. (`InputContextRepository`)"""
        return self.__input_configuration

    @input_configuration.setter
    def input_configuration(self, value: InputContextRepository):
        self.__input_configuration = value

    @property
    def unit_scale_factor(self) -> float:
        """ LocalUnit * UnitScaleFactor = DIP (DIP = 1/96 of a logical Inch). ('float')"""
        return self.__unit_scale_factor

    @unit_scale_factor.setter
    def unit_scale_factor(self, value: float):
        self.__unit_scale_factor = value

    @property
    def sensor_data(self) -> SensorDataRepository:
        """Input data repository; sensor data. (`SensorDataRepository`)"""
        return self.__input_data

    @property
    def brushes(self) -> Brushes():
        """All brushes (vector and raster brushes). (`Brushes`)"""
        return self.__brushes

    @property
    def ink_tree(self) -> Optional[InkTree]:
        """Main ink tree. (``InkTree)"""
        return self.__ink_tree

    @ink_tree.setter
    def ink_tree(self, ink_tree: InkTree):
        self.add_tree(ink_tree)

    @property
    def strokes(self) -> List[Stroke]:
        """List of all strokes. (`List[Stroke]`, read-only)"""
        strokes: List[Stroke] = []
        if self.ink_tree is not None:
            for node in PreOrderEnumerator(self.ink_tree.root):
                if isinstance(node, StrokeNode):
                    strokes.append(node.stroke)
        return strokes

    def stroke_by_id(self, stroke_uuid: uuid.UUID) -> Stroke:
        """
        Returns the stroke for a specific UUID.

        Parameters
        ----------
        stroke_uuid: `UUID`
            ID of the stroke

        Returns
        -------
        stroke: `Stroke`
            Instance of the  stroke
        """
        for node in PreOrderEnumerator(self.ink_tree.root):
            if isinstance(node, StrokeNode):
                if node.stroke.id == stroke_uuid:
                    return node.stroke
        raise InkModelException(f"Stroke with id {stroke_uuid} does not exist in main tree.")

    @staticmethod
    def collect_strokes(tree: InkTree) -> List[Stroke]:
        """
        Collecting strokes.

        Parameters
        ----------
        tree: `InkTree`
            Ink tree

        Returns
        -------
        strokes: `List[Stroke]`
            List of strokes
        """
        strokes: List[Stroke] = []
        for node in PreOrderEnumerator(tree.root):
            if isinstance(node, StrokeNode):
                strokes.append(node.stroke)
        return strokes

    @property
    def views(self) -> Tuple[InkTree]:
        """List of views. (Tuple[InkTree])"""
        return tuple(self.__views)

    def add_tree(self, tree: InkTree):
        """Adding an ink tree to the model.
        Parameters
        ----------
        tree: InkTree
            An instance of the ink tree

        Raises
        ------
        InkModelException
            If the tree is already assigned to an ink model.
        """
        if tree.model is not None:
            raise InkModelException(f"InkTree with name {tree.name} is already assigned to an ink model.")

        if self.has_tree(tree.name):
            raise InkModelException(f"InkTree with name {tree.name} is already assigned to the current ink model.")

        tree.model = self
        if tree.name in ('', CommonViews.MAIN_INK_TREE.value):
            self.__ink_tree = tree
        else:
            self.__views.append(tree)

        if tree.root is not None:
            tree.register_sub_tree(tree.root)

    def remove_tree(self, name: str):
        """Removing view tree from model.

        Parameters
        ----------
        name: str
            Name of the tree that should be removed. If the tree does not exist, nothing happens.
        """
        tree: Optional[InkTree] = self.tree(name)
        if tree is None:
            return
        tree.unregister_sub_tree(tree.root)
        if tree.name in ('', CommonViews.MAIN_INK_TREE.value):
            self.__ink_tree = None
        else:
            self.__views.remove(tree)
        # Detach the tree from the model
        tree.model = None

    def tree(self, name: str) -> Optional[InkTree]:
        """Return named tree.
        Returns
        -------
        Optional[InkTree]
            The main ink tree
        """
        if name == CommonViews.MAIN_INK_TREE.value:
            return self.ink_tree
        for v in self.views:
            if v.name == name:
                return v
        return None

    def has_tree(self, name: str) -> bool:
        """Check if the named tree exists.

        Parameters
        ----------
        name: str
            Name of the tree

        Returns
        -------
        bool
            Flag if the tree exists
        """
        if name == CommonViews.MAIN_INK_TREE.value:
            return self.ink_tree is not None
        return any(v.name == name for v in self.views)

    def clear_views(self):
        """Clears the views."""
        for v in self.views:
            v.unregister_sub_tree(v.root)
            v.model = None
        self.__views = []

    @property
    def knowledge_graph(self) -> schema.TripleStore:
        """Knowledge graph encoding all knowledge about the ink strokes."""
        return self.__knowledge_graph

    @property
    def transform(self) -> numpy.array:
        """Transformation matrix. (numpy.array)"""
        return self.__transform

    @transform.setter
    def transform(self, transform: List[List[float]]):
        self.__transform = numpy.array(transform)
        self.__default_transform = False

    @property
    def default_transform(self) -> bool:
        """Flag if the transform has been updated."""
        return self.__default_transform

    @property
    def properties(self) -> list:
        """Returns the properties for ink object."""
        return self.__properties

    @properties.setter
    def properties(self, properties: list):
        self.__properties = properties

    def add_property(self, name: str, value: str):
        """Adds a property.

        Parameters
        ----------
        name: str
            Name of the property
        value: str
            Value of the property
        """
        self.__properties.append((name, value))

    def view_root(self, name: str) -> StrokeGroupNode:
        """Returns the root for a view.

        Parameters
        ----------
        name: str
            Name of the view

        Returns
        -------
        StrokeGroupNode
            Root of the named view

        Raises
        ------
        KeyError
            View with name does not exist
        """
        return self.view(name).root

    def view(self, name: str) -> ViewTree:
        """Returns the view.

        Parameters
        ----------
        name: str
            Name of the view

        Returns
        -------
        ViewTree
            Instance of the view

        Raises
        ------
        KeyError
            View with name does not exist
        """
        for v in self.__views:
            if v.name == name:
                return v
        raise KeyError(f'No view with name:={name}')

    def add_view(self, view: ViewTree):
        """Adding a view to the InkObject.

        Parameters
        ----------
        view: ViewTree
            View to added to the ink model.
        """
        self.add_tree(view)

    def add_semantic_triple(self, subject: str, predicate: str, obj: str):
        """Adding a semantic triple to the object.

        Parameters
        ----------
        subject: str
            Subject of the statement. This might be the uri of a stroke, a group, a view, etc.

        predicate: str
            Predicate of the statement. This might be a property of the subject, a relationship, etc. Here check out the
            schema module for some predefined predicates.

        obj: str
            Object of the statement. This might be a value, a uri, etc.
        """
        self.__knowledge_graph.add_semantic_triple(subject, predicate, obj)

    def remove_semantic_triple(self, subject: str, predicate: str, obj: str):
        """Remove a semantic triple from the object.

        Parameters
        ----------
        subject: str
            Subject of the statement.

        predicate: str
            Predicate of the statement.

        obj: str
            Object of the statement.
        """
        self.__knowledge_graph.remove_semantic_triple(schema.SemanticTriple(subject, predicate, obj))

    def clear_knowledge_graph(self):
        """Clears the knowledge graph."""
        self.__knowledge_graph.clear_statements()

    def build_stroke_cache(self, stroke: Stroke):
        """
        Build stroke cache.

        Parameters
        ----------
        stroke: Stroke
            Stroke for cache

        """
        (ts, p) = self.get_stroke_timestamp_and_pressure_values(stroke)
        stroke.set_timestamp_values(ts)
        stroke.set_pressure_values(p)

    @staticmethod
    def clear_stroke_cache(stroke: Stroke):
        """
        Clear stroke cache.

        Parameters
        ----------
        stroke: `Stroke`
            Stroke to clear.
        """
        stroke.set_timestamp_values([])
        stroke.set_pressure_values([])

    def get_stroke_timestamp_and_pressure_values(self, stroke: Stroke, duplicate_first_and_last: bool = True) \
            -> Tuple[List[float], List[float]]:
        """
        Gets the timestamp and pressure values.

        Parameters
        ----------
        stroke: `Stroke`
            Stroke
        duplicate_first_and_last: `bool`
            Duplicate first and last

        Returns
        -------
        timestamps:  List[float]
            List of timestamp values
        pressure_values:  List[float]
            List of pressure values
        """
        sd: SensorData = self.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
        sensor_channels: list = self.input_configuration.sensor_contexts[0].sensor_channels_contexts[0] \
            .channels

        t_channel_id = [c.id for c in sensor_channels if c.type == InkSensorType.TIMESTAMP][0]
        p_channel_id = [c.id for c in sensor_channels if c.type == InkSensorType.PRESSURE][0]

        ts: list = []
        ps: list = []

        for cd in sd.data_channels:
            if cd.id == t_channel_id:
                ts = cd.values.copy()
            elif cd.id == p_channel_id:
                ps = cd.values.copy()

        if duplicate_first_and_last:
            ts.insert(0, ts[0])
            ts.append(ts[-1])

            ps.insert(0, ps[0])
            ps.append(ps[-1])

        return ts, ps

    def get_strokes_as_strided_array(self, layout: Optional[List[InkStrokeAttributeType]] = None,
                                     policy: HandleMissingDataPolicy = HandleMissingDataPolicy.FILL_WITH_ZEROS) \
            -> Tuple[List, List[InkStrokeAttributeType]]:
        """
        Returns all the strokes in the document, where each stroke is an array with stride 4.

        Parameters
        ----------
        layout: str -
            Layout string (x, y, timestamp, pressure).
        policy: HandleMissingDataPolicy -
            Policy to handle missing data.

        Returns
        -------
        array: `List`
            Strided array
        layout: List[InkStrokeAttributeType]]
            Layout structure
        """
        if layout is None:
            layout = DEFAULT_EXTENDED_LAYOUT
        if InkStrokeAttributeType.SPLINE_X not in layout or InkStrokeAttributeType.SPLINE_Y not in layout or \
                InkStrokeAttributeType.SENSOR_TIMESTAMP not in layout \
                or InkStrokeAttributeType.SENSOR_PRESSURE not in layout:
            raise ValueError("X, Y, Timestamp and Pressure channels are mandatory.")
        if policy not in [HandleMissingDataPolicy.SKIP_STROKE, HandleMissingDataPolicy.THROW_EXCEPTION,
                          HandleMissingDataPolicy.FILL_WITH_ZEROS]:
            raise ValueError(f"Unsupported policy: {policy}")

        strokes: List[Stroke] = self.strokes
        result: List = []
        for stroke in strokes:
            # Remove the first and last element, which are added by the spline producer
            xs = stroke.splines_x[1:-1]
            ys = stroke.splines_y[1:-1]

            if stroke.sensor_data_id is None:
                if policy == HandleMissingDataPolicy.SKIP_STROKE:
                    logger.warning(f"Skipping stroke (id:= {stroke.id}) without sensor data.")
                    continue
                if policy == HandleMissingDataPolicy.THROW_EXCEPTION:
                    raise ValueError(f"Stroke (id:= {stroke.id}) does not have sensor data.")
                if policy == HandleMissingDataPolicy.FILL_WITH_ZEROS:
                    result.append([0, 0, 0, 0])
                    continue

            sd: SensorData = self.sensor_data.sensor_data_by_id(stroke.sensor_data_id)

            sc_ts: Optional[SensorChannel] = None
            sc_pressure: Optional[SensorChannel] = None

            input_context: InputContext = self.input_configuration.get_input_context(sd.input_context_id)
            if input_context is not None:
                sensor_context = self.input_configuration.get_sensor_context(input_context.sensor_context_id)
                if sensor_context is not None:
                    sc_ts: Optional[SensorChannel] = None
                    sc_pressure: Optional[SensorChannel] = None
                    # Find the timestamp and pressure channels
                    if sensor_context.has_channel_type(InkSensorType.TIMESTAMP):
                        sc_ts = sensor_context.get_channel_by_type(InkSensorType.TIMESTAMP)
                    if sensor_context.has_channel_type(InkSensorType.PRESSURE):
                        sc_pressure = sensor_context.get_channel_by_type(InkSensorType.PRESSURE)
            if sd is None or sc_ts is None or sd.get_data_by_id(sc_ts.id) is None:
                ts = []
            else:
                ts = sd.get_data_by_id(sc_ts.id).values.copy()

            if sd is None or sc_pressure is None or sd.get_data_by_id(sc_pressure.id) is None:
                ps = []
            else:
                ps = sd.get_data_by_id(sc_pressure.id).values.copy()

            xs = xs[0:len(ts)]
            ys = ys[0:len(ts)]

            # Handle missing timestamp according to policy
            if len(ts) == 0:
                if policy == HandleMissingDataPolicy.SKIP_STROKE:
                    continue
                if policy == HandleMissingDataPolicy.THROW_EXCEPTION:
                    raise ValueError("There is no timestamp data for this stroke.")

            # Handle missing pressure according to policy
            if len(ps) == 0:
                if policy == HandleMissingDataPolicy.SKIP_STROKE:
                    continue
                if policy == HandleMissingDataPolicy.THROW_EXCEPTION:
                    raise ValueError("There is no pressure data for this stroke.")

            points = []
            sensor_data_mapping = stroke.sensor_data_mapping
            if len(sensor_data_mapping) == 0:  # Mapping is 1:1
                limit = min(stroke.sensor_data_offset + len(xs), len(ts))
                sensor_data_mapping = range(stroke.sensor_data_offset, limit)

            i = 0
            for map_i in sensor_data_mapping:
                points.append(xs[i])
                points.append(ys[i])

                if len(ts) == 0:
                    points.append(0)
                else:
                    points.append(ts[map_i])

                if len(ps) == 0:
                    points.append(0)
                else:
                    points.append(ps[map_i])
                i += 1
            result.append(points)
        return result, layout

    def get_strokes_as_strided_array_extended(self, layout: Optional[List[InkStrokeAttributeType]] = None,
                                              policy: HandleMissingDataPolicy =
                                              HandleMissingDataPolicy.FILL_WITH_ZEROS,
                                              include_stroke_idx: bool = False) \
            -> Tuple[List[List[float]], List[InkStrokeAttributeType]]:
        """
        Returns all the strokes in the document, where each stroke is an array with stride len(layout)

        Parameters
        ----------
        layout: List[InkStrokeAttributeType]
            Layout of the extended stroke data
        policy: HandleMissingDataPolicy
            Policy to handle missing data
        include_stroke_idx: bool (default: False)
            Flag if stroke idx should be included in the output

        Returns
        -------
        array: List[List]
            Strided array
        layout: List[InkStrokeAttributeType]
            Layout of the extended stroke data

        Raises
        ------
        ValueError
            If X and Y channels are not present in the layout
        """
        if layout is None:
            layout = DEFAULT_EXTENDED_LAYOUT
        if InkStrokeAttributeType.SPLINE_X not in layout or InkStrokeAttributeType.SPLINE_Y not in layout:
            raise ValueError("X and Y channels are mandatory")
        strokes = self.strokes
        result: List[List[float]] = []

        for idx, stroke in enumerate(strokes):
            points = stroke.as_strided_array_extended(self, layout=layout, handle_missing_data=policy)
            if points:
                if include_stroke_idx:
                    result.append([float(idx)] + points)
                else:
                    result.append(points)
        return result, layout

    def sensor_data_lookup(self, stroke: Stroke, ink_sensor_type: InkSensorType,
                           return_channel_data_instance: bool = False) -> Union[List[float], ChannelData]:
        """
        Sensor data lookup.

        Parameters
        ----------
        stroke: Stroke
            Stroke
        ink_sensor_type: InkSensorType
            Sensor type
        return_channel_data_instance: bool
            Flag if channel data instance should be returned

        Returns
        -------
        data: Union[List[float], ChannelData]
            List of data or channel data instance
        """
        sd: SensorData = self.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
        sc: Optional[SensorChannel] = None
        input_context: InputContext = self.input_configuration.get_input_context(sd.input_context_id)
        if input_context is not None:
            sensor_context = self.input_configuration.get_sensor_context(input_context.sensor_context_id)
            if sensor_context is not None and sensor_context.has_channel_type(ink_sensor_type):
                sc = sensor_context.get_channel_by_type(ink_sensor_type)
        if sd is None or sc is None or sd.get_data_by_id(sc.id) is None:
            return None if return_channel_data_instance else []
        return sd.get_data_by_id(sc.id) if return_channel_data_instance else sd.get_data_by_id(sc.id).values.copy()

    def calculate_bounds_recursively(self, node: InkNode):
        """
        Calculates the bounds recursively.

        Parameters
        ----------
        node: Node
            Node of the tree
        """
        x_min: float = sys.float_info.max
        x_max: float = 0.
        y_min: float = sys.float_info.max
        y_max: float = 0.
        if isinstance(node, StrokeNode):
            stroke_node: StrokeNode = node
            x_min: float = min(stroke_node.stroke.spline_min_x, x_min)
            x_max: float = max(stroke_node.stroke.spline_max_x, x_max)
            y_min: float = min(stroke_node.stroke.spline_min_y, y_min)
            y_max: float = max(stroke_node.stroke.spline_max_y, y_max)
            node.group_bounding_box = BoundingBox(x_min, y_min, x_max - x_min, y_max - y_min)
        elif isinstance(node, StrokeGroupNode):
            for child_node in node.children:
                self.calculate_bounds_recursively(child_node)
                child_bbox: BoundingBox = child_node.group_bounding_box
                x_min: float = min(child_bbox.x, x_min)
                x_max: float = max(child_bbox.x + child_bbox.width, x_max)
                y_min: float = min(child_bbox.y, y_min)
                y_max: float = max(child_bbox.y + child_bbox.height, y_max)
            bbox: BoundingBox = BoundingBox(x_min, y_min, x_max - x_min, y_max - y_min)
            node.group_bounding_box = bbox

    def has_properties(self) -> bool:
        """
        Checks if the Ink Model has properties configured.

        Returns
        --------
        flag: `bool`
            Flag if properties have been configured for InkModel
        """
        return len(self.properties) > 0

    def has_input_data(self) -> bool:
        """
        Checks if the Ink Model has input data configured.

        Returns
        -------
        flag: `bool`
            Flag if input data have been configured for InkModel
        """
        return len(self.sensor_data.sensor_data) > 0 or self.input_configuration.has_configuration()

    def has_brushes(self) -> bool:
        """
        Checks if the Ink Model has brushes configured.

        Returns
        -------
        flag: `bool`
            Flag if brushes have been configured for InkModel
        """
        return len(self.brushes.vector_brushes) > 0 or len(self.brushes.raster_brushes) > 0

    def has_ink_data(self) -> bool:
        """
        Checks if the Ink Model has ink data configured.

        Returns
        -------
        flag: `bool`
            Flag if ink data have been configured for InkModel
        """
        return self.ink_tree is not None

    def has_knowledge_graph(self) -> bool:
        """
        Checks if the Ink Model has knowledge graph configured.

        Returns
        -------
        flag: `bool`
            Flag if knowledge graph have been configured for InkModel
        """
        return len(self.knowledge_graph.statements) > 0

    def has_ink_structure(self) -> bool:
        """
        Checks if the Ink Model has ink structure configured.

        Returns
        -------
        flag: `bool`
            Flag if input data have been configured for InkModel
        """
        if self.ink_tree is None:
            return False
        return self.ink_tree.root is not None

    def clone_stroke_node(self, stroke_node: StrokeNode,  target_parent_node: StrokeGroupNode = None,
                          clone_semantics: bool = True) -> StrokeNode:
        """
        Cloning a stroke node.

        Parameters
        ----------
        stroke_node: `StrokeNode`
            Stroke node which shall be cloned

        target_parent_node: `StrokeGroupNode`
            Target node

        clone_semantics: `bool`
            Cloning semantics

        Returns
        -------
            stroke: `StrokeNode`
                Cloned stroke
        """
        if not isinstance(stroke_node, StrokeNode):
            raise InkModelException(f"Cloning aborted: Stroke node is not an instance of StrokeNode. "
                                    f"(type:={type(stroke_node)})")
        if stroke_node.fragment is not None:
            f = stroke_node.fragment
            fragment = StrokeFragment(f.from_point_index, f.to_point_index, f.from_t_value, f.to_t_value)
        else:
            fragment = None

        new_node: StrokeNode = StrokeNode(stroke=stroke_node.stroke, fragment=fragment)

        if clone_semantics:
            triples = self.knowledge_graph.filter(stroke_node.uri)
            t: SemanticTriple
            for t in triples:
                self.knowledge_graph.add_semantic_triple(new_node.uri, t.predicate, t.object)

        if target_parent_node is not None:
            target_parent_node.add(new_node)

        return new_node

    def clone_stroke_group_node(self, stroke_group_node: StrokeGroupNode,
                                target_parent_node: StrokeGroupNode = None,
                                clone_semantics: bool = True,
                                clone_child_stroke_nodes: bool = True,
                                clone_child_group_nodes: bool = False,
                                raise_exception: bool = False,
                                store_source_node_reference_transient_key: str = None) -> StrokeGroupNode:
        """
        Clone stroke group node.

        Parameters
        ----------
        stroke_group_node: `StrokeGroupNode`
            StrokeGroupNode to be cloned.
        target_parent_node: `StrokeGroupNode`
            Target node
        clone_semantics: `bool`
            Clone semantics [default:=True]
        clone_child_stroke_nodes: `bool`
            Clone child stroke nodes [default:=True]
        clone_child_group_nodes: bool
            Clone child group nodes [default:=False]
        raise_exception: bool
            Raise exceptions [default:=False]
        store_source_node_reference_transient_key: str
            Store source node reference.

        Returns
        -------
        new_stroke_group_node: `StrokeGroupNode`
            Cloned `StrokeGroupNode`

        Raises
        ------
        InkModelException
            If cloning needs to be aborted.
        """
        new_node: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())

        if target_parent_node is not None:
            target_parent_node.add(new_node)

        if clone_semantics:
            triples = self.knowledge_graph.filter(stroke_group_node.uri)
            t: SemanticTriple
            for t in triples:
                self.knowledge_graph.add_semantic_triple(new_node.uri, t.predicate, t.object)

        if clone_child_stroke_nodes or clone_child_group_nodes:
            for n in stroke_group_node.children:
                child_clone: Optional[Union[StrokeNode, StrokeGroupNode]] = None
                if isinstance(n, StrokeNode):
                    if clone_child_stroke_nodes:
                        child_clone = self.clone_stroke_node(n, target_parent_node=new_node,
                                                             clone_semantics=clone_semantics)
                    elif raise_exception:
                        raise InkModelException("Cloning aborted: Stroke node would be left behind if we continue.")

                elif isinstance(n, StrokeGroupNode):
                    if clone_child_group_nodes:
                        child_clone = self.clone_stroke_group_node(n, target_parent_node=new_node,
                                                                   clone_semantics=clone_semantics,
                                                                   clone_child_stroke_nodes=clone_child_stroke_nodes,
                                                                   clone_child_group_nodes=clone_child_group_nodes,
                                                                   raise_exception=raise_exception)
                    elif raise_exception:
                        raise InkModelException("Cloning aborted: Group node would be left behind if we continue.")

                if store_source_node_reference_transient_key is not None:
                    child_clone.transient_tag = {store_source_node_reference_transient_key: n}
        return new_node

    def get_channel_data_instance(self, stroke: Stroke, ink_sensor_type: Union[InkSensorType, str]) \
            -> Optional[ChannelData]:
        """
        Get channel data instance.

        Parameters
        ----------
        stroke: Stroke
            Stroke
        ink_sensor_type: Union[InkSensorType, str]
            Sensor type

        Returns
        -------
        Optional[ChannelData]
            Channel data
        """
        if isinstance(ink_sensor_type, str):
            ink_sensor_type = InkSensorType(ink_sensor_type)
        sd: SensorData = self.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
        sc: Optional[SensorChannel] = None

        input_context = self.input_configuration.get_input_context(sd.input_context_id)
        if input_context is not None:
            sensor_context = self.input_configuration.get_sensor_context(input_context.sensor_context_id)
            if sensor_context is not None:
                if sensor_context.has_channel_type(ink_sensor_type):
                    sc = sensor_context.get_channel_by_type(ink_sensor_type)
        if sd is None or sc is None or sd.get_data_by_id(sc.id) is None:
            return None
        return sd.get_data_by_id(sc.id)

    def get_channel_data_values(self, stroke: Stroke, ink_sensor_type: Union[InkSensorType, str]) -> List[float]:
        """
        Get channel data values.

        Parameters
        ----------
        stroke: Stroke
            Stroke
        ink_sensor_type: str
            Sensor type

        Returns
        -------
        values:  List[float]
            List of values
        """
        if isinstance(ink_sensor_type, str):
            ink_sensor_type = InkSensorType(ink_sensor_type)
        channel_data = self.get_channel_data_instance(stroke, ink_sensor_type)

        if channel_data is None:
            # No data available
            return []
        # If the sensor type is TIMESTAMP, we need to add the timestamp to the values
        if ink_sensor_type == InkSensorType.TIMESTAMP:
            sd: SensorData = self.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
            return [v + sd.timestamp for v in channel_data.values]
        return channel_data.values.copy()

    def get_sensor_channel_types(self, stroke: Stroke):
        """
        Get sensor channel types.

        Parameters
        ----------
        stroke: `Stroke`
            Stroke object

        Returns
        -------
        sensor_channel_types: `List`
            List of sensor channel types
        """
        sensor_channel_types: List[InkSensorType] = []

        if stroke.sensor_data_id is None:
            return sensor_channel_types

        sd: SensorData = self.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
        input_context = self.input_configuration.get_input_context(sd.input_context_id)
        if input_context is not None:
            sensor_context = self.input_configuration.get_sensor_context(input_context.sensor_context_id)
            if sensor_context is not None:
                for dc in sd.data_channels:
                    channel = sensor_context.get_channel_by_id(dc.id)
                    sensor_channel_types.append(channel.type)

        return sensor_channel_types

    def register_node(self, node: InkNode):
        """
        Register ink node.

        Parameters
        ----------
        node: `InkNode`
            Reference to node.

        Raises
        ------
        InkModelException
            If Node with URI already exist in the tree
        """
        if self.__map.get(node.uri) is not None:
            raise InkModelException(f'An ink node with uri {node.uri} already exists in the model.')
        if node_registration_debug:
            logger.debug(f"Registering node {node.uri}")

        self.__map[node.uri] = node

    def is_node_registered(self, node: InkNode):
        """
        Check if node is registered.

        Parameters
        ----------
        node: `InkNode`
            Node to check

        Returns
        -------
        flag: `bool`
            Flag if node is already registered in tree.
        """
        return self.__map.get(node.uri) is not None

    def unregister_node(self, node: InkNode):
        """
        Unregister a node.

        Parameters
        ----------
        node: `InkNode`
            Node to unregister

        Notes
        -----
        This function removes the triples for the node as well.
        """
        if node_registration_debug:
            logger.debug(f"Unregistering node {node.uri}")
            
        if node.tree is not None:
            triples = self.knowledge_graph.filter(node.uri)
            if node_registration_debug:
                logger.debug(f"Found {len(triples)} triples for {node.uri}")
            for t in triples:
                if node_registration_debug:
                    logger.debug(f"Removing semantic triple: {str(t)}")
                self.knowledge_graph.remove_semantic_triple(t)

            if node_registration_debug:
                triples = self.knowledge_graph.filter(node.uri)
                logger.debug(f"Sanity check => Found {len(triples)} triples for {node.uri}")

        del self.__map[node.uri]

    def get_sensor_channel(self, stroke: Stroke, ink_sensor_type: Union[InkSensorType, str]) -> Optional[SensorChannel]:
        """
        Get sensor channel.
        Parameters
        ----------
        stroke: Stroke
            Stroke
        ink_sensor_type: Union[InkSensorType, str]
            Sensor type

        Returns
        -------
        SensorChannel
            Sensor channel
        """
        if isinstance(ink_sensor_type, str):
            ink_sensor_type = InkSensorType(ink_sensor_type)
        sd: SensorData = self.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
        sc = None
        input_context = self.input_configuration.get_input_context(sd.input_context_id)
        if input_context is not None:
            sensor_context = self.input_configuration.get_sensor_context(input_context.sensor_context_id)
            if sensor_context is not None:
                if sensor_context.has_channel_type(ink_sensor_type):
                    sc = sensor_context.get_channel_by_type(ink_sensor_type)

        if sd is None or sc is None:
            return None
        return sc

    def reinit_sensor_channel(self, ink_sensor_type: InkSensorType,
                              ink_sensor_metric: Optional[InkSensorMetricType] = None,
                              resolution: Optional[float] = None,
                              channel_min: Optional[float] = None, channel_max: Optional[float] = None,
                              precision: Optional[int] = None, index: Optional[int] = None,
                              name: Optional[str] = None, data_type=None,
                              ink_input_provider_id: Optional[uuid.UUID] = None,
                              input_device_id: Optional[uuid.UUID] = None):
        """
        Reinitialize the sensor channel. This should be done when you want to modify the sensor data (because by
        default it is immutable), e.g. when you want to modify the timestamps or pressure values.

        Parameters
        ----------
        ink_sensor_type: `InkSensorType`
            Sensor type
        ink_sensor_metric: Optional[InkSensorMetricType] (optional) [default:=None]
            Sensor metric
        resolution: Optional[float] (optional) [default:=None]
            Resolution
        channel_min: Optional[float] (optional) [default:=None]
            Channel min
        channel_max: Optional[float] (optional) [default:=None]
            Channel max
        precision: Optional[int] (optional) [default:=None]
            Precision
        index: Optional[int] (optional) [default:=None]
            Index
        name: Optional[str] (optional) [default:=None]
            Name
        data_type:
            Data type
        ink_input_provider_id: Optional[UUID] (optional) [default:=None]
            Ink input provider ID
        input_device_id: Optional[UUID] (optional) [default:=None]
            Input device ID
        """
        for input_context in self.input_configuration.input_contexts:
            if input_context is not None:
                sensor_context = self.input_configuration.get_sensor_context(input_context.sensor_context_id)
                if sensor_context is not None:
                    if sensor_context.has_channel_type(ink_sensor_type):
                        for scc in sensor_context.sensor_channels_contexts:
                            for c in scc.channels:
                                if c.type == ink_sensor_type:
                                    new_channel = SensorChannel(channel_type=ink_sensor_type,
                                                                metric=ink_sensor_metric if ink_sensor_metric
                                                                                            is not None else c.metric,
                                                                resolution=resolution if resolution is not None
                                                                else c.resolution,
                                                                channel_min=channel_min if channel_min is not None
                                                                else c.min,
                                                                channel_max=channel_max if channel_max is not None
                                                                else c.max,
                                                                precision=precision if precision is not None
                                                                else c.precision,
                                                                index=index if index is not None else c.index,
                                                                name=name if name is not None else c.name,
                                                                data_type=data_type if data_type is not None
                                                                else c.data_type,
                                                                ink_input_provider_id=ink_input_provider_id
                                                                if ink_input_provider_id is not None
                                                                else c.ink_input_provider,
                                                                input_device_id=input_device_id
                                                                if input_device_id is not None else c.input_device_id)
                                    # Remove the old channel and replace it with the new one
                                    index = scc.channels.index(c)
                                    scc.channels.remove(c)
                                    scc.channels.insert(index, new_channel)
                                    # Since this changes the order §of channels in SCC its identifier needs
                                    # to be regenerated
                                    scc.regenerate_id()
                                    # Regenerate SC id just in case
                                    sensor_context.regenerate_id()

                                    old_ic_id = input_context.id

                                    # Swap the SC id in IC and regenerate its id
                                    input_context.sensor_context_id = sensor_context.id
                                    input_context.regenerate_id()

                                    # Go through all sensor data instances and fix ids and maintain the internal
                                    # storing mechanism
                                    try:
                                        for s in self.sensor_data.sensor_data:
                                            if c.id != new_channel.id:
                                                # This lookup is necessary because of the way the
                                                # SensorData class maintains its cache.
                                                # TODO: It's designed badly revise in future.
                                                s.get_data_by_id(c.id)

                                                index = list(s._SensorData__map_channels.keys()).index(c.id)

                                                s._SensorData__map_idx.pop(index, None)
                                                s._SensorData__map_channels.pop(c.id, None)

                                            if old_ic_id is not None and s.input_context_id == old_ic_id:
                                                s.input_context_id = input_context.id
                                    except Exception as e:
                                        logger.error(f"Error while reinitializing sensor channel: {e}")

    def remove_node(self, node: InkNode):
        """
        Remove a node.

        Parameters
        ----------
        node: `InkNode`
           Node to be remove

        Notes
        -----
        This function removes the triples and the node as well.

       """
        # First remove the triples
        self.unregister_node(node)
        if node.parent is not None:
            node.parent.remove(node)

    def __eq__(self, other: Any):
        if not isinstance(other, InkModel):
            logger.warning(f"Cannot compare InkModel with {type(other)}")
            return False
        other_model: InkModel = other
        if self.version != other_model.version:
            logger.debug(f"Version is different {self.version} != {other_model.version}")
            return False
        if not (self.transform == other_model.transform).all():
            logger.debug(f"Transform is different {self.transform} != {other_model.transform}")
            return False
        if self.has_properties() == other_model.has_properties():
            map_prop: dict = dict(other_model.properties)
            for key, value in self.properties:
                if key in map_prop:
                    if value != map_prop[key]:
                        logger.debug(f"Property {key} has different values {value} != {map_prop[key]}")
                        return False
                    del map_prop[key]
                else:
                    logger.debug(f"Property {key} is missing in other model")
                    return False
            if len(map_prop) > 0:
                logger.debug(f"Other model has additional properties {map_prop}")
                return False
        else:
            return False
        # Check if the input data is the same
        if self.has_input_data() == other_model.has_input_data():
            if self.has_input_data():
                if self.input_configuration != other_model.input_configuration:
                    logger.warning("Input configuration is different")
                    return False
                if self.sensor_data != other_model.sensor_data:
                    logger.warning("Sensor data is different")
                    return False
        else:
            return False
        # Check if the brushes are the same
        if self.has_brushes() == other_model.has_brushes():
            for v_brush_org, v_brush_diff in zip(self.brushes.vector_brushes, other_model.brushes.vector_brushes):
                if v_brush_org != v_brush_diff:
                    return False
            for r_brush_org, r_brush_diff in zip(self.brushes.raster_brushes, other_model.brushes.raster_brushes):
                if r_brush_org != r_brush_diff:
                    return False
        else:
            return False
        # Check if the strokes are the same
        if self.has_ink_data() == other_model.has_ink_data():
            for str_org, str_diff in zip(self.strokes,
                                         other_model.strokes):
                if str_org != str_diff:
                    return False
        else:
            return False
        if self.has_knowledge_graph() == other_model.has_knowledge_graph():
            for t_org, t_diff in zip(self.knowledge_graph.statements, other_model.knowledge_graph.statements):
                if t_org != t_diff:
                    return False
        else:
            return False

        for view_org, view_diff in zip(self.views, other_model.views):
            if view_org != view_diff:
                return False

        return True

    def __dict__(self):
        return {
            "version": self.version.__dict__() if self.version is not None else {},
            "transform": self.transform.tolist() if self.transform is not None else [],
            "properties": dict(self.properties) if self.properties is not None else {},
            "input_configuration": self.input_configuration.__dict__(),
            "sensor_data": self.sensor_data.__dict__(),
            "brushes": self.brushes.__dict__(),
            "strokes": [s.__dict__() for s in self.strokes],
            "ink_tree": self.ink_tree.__dict__() if self.ink_tree is not None else {},
            "views": [v.__dict__() for v in self.views],
            "knowledge_graph": self.knowledge_graph.__dict__(),
        }

    def __json__(self):
        return self.__dict__()

    def __repr__(self):
        parts: str = ''
        prefix: str = ''
        if self.has_properties():
            parts += f'Properties (properties:={len(self.properties)})'
            prefix = ', '
        if self.has_input_data():
            parts += prefix + f'Input Data (sensor data:={len(self.sensor_data.sensor_data)})'
            prefix = ', '
        if self.has_brushes():
            parts += prefix + f'Brushes (vector:={len(self.brushes.vector_brushes)}, '
            parts += f'raster:={len(self.brushes.raster_brushes)})'
            prefix = ', '
        if self.has_ink_data():
            parts += prefix + f'Ink Data (ink data:={len(self.strokes)})'
            prefix = ', '
        if self.has_knowledge_graph():
            parts += prefix + f'Knowledge graph (statements:={len(self.knowledge_graph.statements)})'
            prefix = ', '
        if self.has_ink_structure():
            parts += prefix + f'Ink Structure (main:={1 if self.ink_tree is not None else 0},views:={len(self.views)})'
        return f'<InkModel - [{parts}]>'

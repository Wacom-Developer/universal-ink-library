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
import logging
import sys
import uuid
from abc import ABC
from typing import List, Any, Dict, Tuple, Optional

import numpy

from uim.codec.context.version import Version
from uim.codec.parser.base import FormatException
from uim.model.base import InkModelException, UUIDIdentifier, node_registration_debug
from uim.model.helpers.policy import HandleMissingDataPolicy
from uim.model.inkdata.brush import Brushes, BlendMode
from uim.model.inkdata.strokes import Stroke
from uim.model.inkinput.inputdata import SensorChannel, \
    InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext, InputContextRepository
from uim.model.inkinput.sensordata import SensorData
from uim.model.semantics import syntax
from uim.model.semantics.node import InkNode, BoundingBox, StrokeNode, StrokeGroupNode, StrokeFragment
from uim.model.semantics.syntax import CommonViews, SemanticTriple
from uim.model.helpers.treeiterator import PreOrderEnumerator

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
            raise InkModelException('No sensor data with id:={}'.format(uimid))
        return self.__sensor_data[self.__map_id[uimid]]

    def __build_idx_map(self):
        """Building an index to map the UUID to index in a list."""
        self.__map_id = {}
        for idx, el in enumerate(self.sensor_data):
            self.__map_id[el.id] = idx

    def __eq__(self, other):
        if not isinstance(other, SensorDataRepository):
            return False
        map_sensor_data: dict = dict([(s.id, s) for s in other.sensor_data])
        for s in self.sensor_data:
            if s.id not in map_sensor_data:
                return False
            if s == map_sensor_data[s.id]:
                del map_sensor_data[s.id]
            else:
                return False
        return True

    def __repr__(self):
        return '<InputData : [sensor:={}]>'.format(self.__sensor_data)


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
        """The primary name associated with this ink tree. (`str`)"""
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def root(self) -> StrokeGroupNode:
        """Root node of the tree. (`StrokeGroupNode`)"""
        return self.__root

    @root.setter
    def root(self, root: StrokeGroupNode):
        root.__assert_not_owned__()
        if self.__root is not None:
            self.unregister_sub_tree(self.__root)
            self.__root = None
        self.register_sub_tree(root)
        self.__root = root

    def __iter__(self):
        return PreOrderEnumerator(self.__root)

    def __repr__(self):
        if self.__root:
            return f'<Ink Tree: [name:={self.name},  root id:={self.root}]>'
        return f'<Ink Tree: [name:={self.name}] - Empty tree'

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
    version: `Version`
            Version of the source (ink content file).

    Examples
    --------
    >>> from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
    >>> from uim.model.base import UUIDIdentifier
    >>> from uim.model.ink import InkModel, InkTree
    >>> from uim.model.inkdata.brush import VectorBrush, BrushPolygon, BrushPolygonUri, RasterBrush, RotationMode,\
    >>>  BlendMode
    >>> from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask
    >>> from uim.model.inkinput.inputdata import Environment, InkInputProvider, InkInputType, InputDevice,\
    >>>    SensorChannel, InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext
    >>> from uim.model.inkinput.sensordata import SensorData, InkState
    >>> from uim.model.semantics import syntax
    >>> from uim.model.semantics.node import StrokeGroupNode, StrokeNode, StrokeFragment, URIBuilder
    >>> from uim.model.semantics.syntax import SemanticTriple, CommonViews
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
    >>> sensor_channels_tablet: list = [
    >>>     SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
    >>>     SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
    >>>     SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0)
    >>> ]
    >>>
    >>> scc_tablet: SensorChannelsContext = SensorChannelsContext(channels=sensor_channels_tablet,
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
    >>> sensor_data_0.add_timestamp_data(sensor_channels_tablet[0], [0, 1, 2, 4, 5])
    >>> sensor_data_0.add_data(sensor_channels_tablet[1],  [100.4, 103.7, 110.1])
    >>> sensor_data_0.add_data(sensor_channels_tablet[2],  [200.1, 202.0, 207.0])
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
    >>> ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, syntax.CommonRDF.PRED_RDF_HAS_TYPE, syntax.WORD))
    >>> ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, syntax.Semantics.PRED_IS, "Wacom"))
    >>>
    >>> # We need an URI builder
    >>> uri_builder: URIBuilder = URIBuilder()
    >>>
    >>> # Create a named entity
    >>> named_entity_uri: str = uri_builder.build_named_entity_uri(UUIDIdentifier.id_generator())
    >>> ink_model.knowledge_graph.append(SemanticTriple(hwr_root.uri, syntax.Semantics.PRED_HAS_NAMED_ENTITY_DEFINITION,
    >>>                                                 named_entity_uri))
    >>>
    >>> # Add knowledge for the named entity
    >>> ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "entityType", "Organization"))
    >>> ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "basedIn", "Japan"))
    >>> ink_model.knowledge_graph.append(SemanticTriple(named_entity_uri, "hasConfidence", "0.85"))
    """

    def __init__(self, version: Version = None):
        self.__input_data: SensorDataRepository = SensorDataRepository()
        self.__version: Version = version
        self.__brushes: Brushes = Brushes()
        self.__ink_tree: Optional[InkTree] = None
        self.__views: List[InkTree] = []
        self.__knowledge_graph: syntax.TripleStore = syntax.TripleStore()
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
    def ink_tree(self) -> InkTree:
        """Main ink tree. (``InkTree)"""
        return self.__ink_tree

    @ink_tree.setter
    def ink_tree(self, ink_tree: InkTree):
        self.add_tree(ink_tree)

    @property
    def strokes(self) -> List[Stroke]:
        """List of all strokes. (`List[Stroke]`, read-only)"""
        strokes: List[Stroke] = []
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
        strokes: List[Stroke] = []
        for node in PreOrderEnumerator(tree.root):
            if isinstance(node, StrokeNode):
                strokes.append(node.stroke)
        return strokes

    @property
    def views(self) -> Tuple[InkTree]:
        """List of views."""
        return tuple(self.__views)

    def add_tree(self, tree: InkTree):
        """Adding an ink tree to the model.
        :param tree: InkTree -
            Instance of the ink tree
        :raises:
            InkModelException - If name is already assigned to an ink model or
        """
        if tree.model is not None:
            raise InkModelException(f"InkTree with name {tree.name} is already assigned to an ink model.")

        if self.has_tree(tree.name):
            raise InkModelException(f"InkTree with name {tree.name} is already assigned to the current ink model.")

        tree.model = self
        if tree.name == '' or tree.name == CommonViews.MAIN_INK_TREE.value:
            self.__ink_tree = tree
        else:
            self.__views.append(tree)

        if tree.root is not None:
            tree.register_sub_tree(tree.root)

    def remove_tree(self, name: str):
        """Removing view tree from model.
        :param name: str -
            Name of the tree that should be removed

        """
        tree: InkTree = self.tree(name)
        tree.unregister_sub_tree(tree.root)
        if tree.name == '' or tree.name == CommonViews.MAIN_INK_TREE.value:
            self.__ink_tree = None
        else:
            self.__views.remove(tree)

    def tree(self, name: str) -> InkTree:
        """Return named tree.
        :returns: tree for defined name
        """
        if name == CommonViews.MAIN_INK_TREE.value:
            return self.ink_tree
        else:
            for v in self.views:
                if v.name == name:
                    return v
        raise InkModelException(f"InkTree with name {name} is not found.")

    def has_tree(self, name: str) -> bool:
        """Check if the named tree exists.
        :param name: str -
            Name of the tree
        :returns: flag if the tree exists
        """
        if name == CommonViews.MAIN_INK_TREE.value:
            return self.ink_tree is not None
        else:
            for v in self.views:
                if v.name == name:
                    return True
        return False

    def clear_views(self):
        """Clears the views."""
        self.__views = []

    @property
    def knowledge_graph(self) -> syntax.TripleStore:
        """Knowledge graph encoding all knowledge about the ink strokes."""
        return self.__knowledge_graph

    @property
    def transform(self) -> numpy.array:
        """Transformation matrix."""
        return self.__transform

    @transform.setter
    def transform(self, transform: list):
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
        :param name: name of the property
        :param value: value of the property
        """
        self.__properties.append((name, value))

    def view_root(self, name: str) -> StrokeGroupNode:
        """Returns the root for a view.
        :param name: CommonViews -
            Name of the view
        :return : root of named view
        :raises:
            KeyError: View with name does not exist
        """
        return self.view(name).root

    def view(self, name: str) -> InkTree:
        """Returns the view.
        :param name: CommonViews -
            Name of the view
        :return : instance of the name
        :raises:
            KeyError: View with name does not exist
        """
        for v in self.__views:
            if v.name == name:
                return v
        raise KeyError('No view with name:={}'.format(name))

    def add_view(self, view: InkTree):
        """Adding a view to the InkObject.
        :param view: View object
        """
        self.add_tree(view)

    def add_semantic_triple(self, subject: str, predicate: str, obj: str):
        """Adding a semantic triple to the object.

        :param subject: subject of the statement
        :param predicate: predicate of the statement
        :param obj: object of the statement
        """
        self.__knowledge_graph.add_semantic_triple(subject, predicate, obj)

    def remove_semantic_triple(self, subject: str, predicate: str, obj: str):
        """Remove a semantic triple from the object.

        :param subject:
        :param predicate:
        :param obj:
        """
        self.__knowledge_graph.remove_semantic_triple(syntax.SemanticTriple(subject, predicate, obj))

    def get_semantic_statement(self, subject: str) -> syntax.SemanticTriple:
        """Returns the document property (or the optional default value).

        :param subject: str -
            key for property
        :return: value or None
        :raises:
            InkModelException: Raised if no semantic triple is existing for subject.
        """
        for sem in self.knowledge_graph.statements:
            if sem.subject == subject:
                return sem
        raise InkModelException('No semantic triple for subject:= {}.'.format(subject))

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
        stroke.set_timestamp_values(None)
        stroke.set_pressure_values(None)

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

    def get_strokes_as_strided_array(self, layout: str = "xytp",
                                     policy: HandleMissingDataPolicy = HandleMissingDataPolicy.FILL_WITH_ZEROS) \
            -> Tuple[List, str]:
        """
        Returns all the strokes in the document, where each stroke is an array with stride 4.

        Parameters
        ----------
        layout: str -
            Layout string - 'xytp' (x, y, timestamp, pressure).
        policy: HandleMissingDataPolicy -
            Policy to handle missing data.

        Returns
        -------
        array: `List`
            Strided array
        layout: `str`
            Layout string
        """

        if layout != "xytp":
            raise ValueError("Unsupported layout: %s" % layout)

        strokes: List[Stroke] = self.strokes
        result: List = []
        for stroke in strokes:
            # Remove the first and last element, which are added by the spline producer
            xs = stroke.splines_x[1:-1]
            ys = stroke.splines_y[1:-1]

            sd: SensorData = self.sensor_data.sensor_data_by_id(stroke.sensor_data_id)

            sc_ts: Optional[SensorChannel] = None
            sc_pressure: Optional[SensorChannel] = None

            input_context: InputContext = self.input_configuration.get_input_context(sd.input_context_id)
            if input_context is not None:
                sensor_context = self.input_configuration.get_sensor_context(input_context.sensor_context_id)
                if sensor_context is not None:
                    sc_ts = None
                    sc_pressure = None

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
                elif policy == HandleMissingDataPolicy.THROW_EXCEPTION:
                    raise ValueError("There is no timestamp data for this stroke.")

            # Handle missing pressure according to policy
            if len(ps) == 0:
                if policy == HandleMissingDataPolicy.SKIP_STROKE:
                    continue
                elif policy == HandleMissingDataPolicy.THROW_EXCEPTION:
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

    def sensor_data_lookup(self, stroke: Stroke, ink_sensor_type: InkSensorType,
                           return_channel_data_instance: bool = False):
        sd: SensorData = self.sensor_data.sensor_data_by_id(stroke.sensor_data_id)

        sc = None

        input_context = self.input_configuration.get_input_context(sd.input_context_id)
        if input_context is not None:
            sensor_context = self.input_configuration.get_sensor_context(input_context.sensor_context_id)
            if sensor_context is not None:

                if sensor_context.has_channel_type(ink_sensor_type):
                    sc = sensor_context.get_channel_by_type(ink_sensor_type)

        if sd is None or sc is None or sd.get_data_by_id(sc.id) is None:
            return None if return_channel_data_instance else []
        else:
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
        try:
            return self.ink_tree is not None
        except FormatException:
            return False

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
        try:
            if self.ink_tree is None:
                return False
            return self.ink_tree.root is not None
        except FormatException:
            return False

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
                child_clone: Optional[InkNode] = None

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
        else:
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

    def __eq__(self, other: Any):
        if not isinstance(other, InkModel):
            return False
        other_model: InkModel = other
        if self.has_properties() == other_model.has_properties():
            map_prop: dict = dict(other_model.properties)
            for key, value in self.properties:
                if key in map_prop:
                    if value != map_prop[key]:
                        return False
                    else:
                        del map_prop[key]
                else:
                    return False
            if len(map_prop) > 0:
                return False
        else:
            return False
        if self.has_input_data() == other_model.has_input_data():
            if self.has_input_data():
                if self.sensor_data != other_model.sensor_data:
                    return False
        else:
            return False
        if self.has_brushes() == other_model.has_input_data():
            pass
        else:
            return False
        if self.has_ink_data() == other_model.has_ink_data():
            pass
        else:
            return False
        if self.has_knowledge_graph() == other_model.has_knowledge_graph():
            pass
        else:
            return False
        if self.has_ink_structure() == other_model.has_ink_structure():
            pass
        else:
            return False
        return True

    def __repr__(self):
        parts: str = ''
        prefix: str = ''
        if self.has_properties():
            parts += 'Properties (properties:={})'.format(len(self.properties))
            prefix = ', '
        if self.has_input_data():
            parts += prefix + 'Input Data (sensor data:={})'.format(len(self.sensor_data.sensor_data))
            prefix = ', '
        if self.has_brushes():
            parts += prefix + 'Brushes (vector:={}, raster:={})'.format(len(self.brushes.vector_brushes),
                                                                        len(self.brushes.raster_brushes))
            prefix = ', '
        if self.has_ink_data():
            parts += prefix + 'Ink Data (ink data:={})'.format(len(self.strokes))
            prefix = ', '
        if self.has_knowledge_graph():
            parts += prefix + 'Knowledge graph (statements:={})'.format(len(self.knowledge_graph.statements))
            prefix = ', '
        if self.has_ink_structure():
            parts += prefix + f'Ink Structure (main:={1 if self.ink_tree is not None else 0},views:={len(self.views)})'
        return '<InkModel - [{}]>'.format(parts)

Module uim.model.ink
====================

Classes
-------

`InkModel(version: Optional[uim.codec.context.version.Version] = None)`
:   InkModel
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
    >>> from uim.model.inkdata.brush import VectorBrush, BrushPolygon, BrushPolygonUri, RasterBrush, RotationMode,     >>>      BlendMode
    >>> from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask, PathPointProperties
    >>> from uim.model.inkinput.inputdata import Environment, InkInputProvider, InkInputType, InputDevice,     >>>      SensorChannel,     >>>     InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext
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
    >>>     LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value | LayoutMask.RED.value |     >>>     LayoutMask.GREEN.value
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

    ### Ancestors (in MRO)

    * abc.ABC

    ### Static methods

    `clear_stroke_cache(stroke: uim.model.inkdata.strokes.Stroke)`
    :   Clear stroke cache.
        
        Parameters
        ----------
        stroke: `Stroke`
            Stroke to clear.

    `collect_strokes(tree: uim.model.ink.InkTree) ‑> List[uim.model.inkdata.strokes.Stroke]`
    :   Collecting strokes.
        
        Parameters
        ----------
        tree: `InkTree`
            Ink tree
        
        Returns
        -------
        strokes: `List[Stroke]`
            List of strokes

    ### Instance variables

    `brushes: <Brushes : [raster brush:=#0, vector brush:=#0]>`
    :   All brushes (vector and raster brushes). (`Brushes`)

    `default_transform: bool`
    :   Flag if the transform has been updated.

    `ink_tree: Optional[uim.model.ink.InkTree]`
    :   Main ink tree. (``InkTree)

    `input_configuration: uim.model.inkinput.inputdata.InputContextRepository`
    :   Input context data repository. (`InputContextRepository`)

    `knowledge_graph: uim.model.semantics.schema.TripleStore`
    :   Knowledge graph encoding all knowledge about the ink strokes.

    `properties: list`
    :   Returns the properties for ink object.

    `sensor_data: uim.model.ink.SensorDataRepository`
    :   Input data repository; sensor data. (`SensorDataRepository`)

    `strokes: List[uim.model.inkdata.strokes.Stroke]`
    :   List of all strokes. (`List[Stroke]`, read-only)

    `transform: <built-in function array>`
    :   Transformation matrix. (numpy.array)

    `unit_scale_factor: float`
    :   LocalUnit * UnitScaleFactor = DIP (DIP = 1/96 of a logical Inch). ('float')

    `version: uim.codec.context.version.Version`
    :   Version of ink content file used to create the model. (`Version`, read-only)

    `views: Tuple[uim.model.ink.InkTree]`
    :   List of views. (Tuple[InkTree])

    ### Methods

    `add_property(self, name: str, value: str)`
    :   Adds a property.
        
        Parameters
        ----------
        name: str
            Name of the property
        value: str
            Value of the property

    `add_semantic_triple(self, subject: str, predicate: str, obj: str)`
    :   Adding a semantic triple to the object.
        
        Parameters
        ----------
        subject: str
            Subject of the statement. This might be the uri of a stroke, a group, a view, etc.
        
        predicate: str
            Predicate of the statement. This might be a property of the subject, a relationship, etc. Here check out the
            schema module for some predefined predicates.
        
        obj: str
            Object of the statement. This might be a value, a uri, etc.

    `add_tree(self, tree: uim.model.ink.InkTree)`
    :   Adding an ink tree to the model.
        Parameters
        ----------
        tree: InkTree
            An instance of the ink tree
        
        Raises
        ------
        InkModelException
            If the tree is already assigned to an ink model.

    `add_view(self, view: uim.model.ink.ViewTree)`
    :   Adding a view to the InkObject.
        
        Parameters
        ----------
        view: ViewTree
            View to added to the ink model.

    `build_stroke_cache(self, stroke: uim.model.inkdata.strokes.Stroke)`
    :   Build stroke cache.
        
        Parameters
        ----------
        stroke: Stroke
            Stroke for cache

    `calculate_bounds_recursively(self, node: uim.model.semantics.node.InkNode)`
    :   Calculates the bounds recursively.
        
        Parameters
        ----------
        node: Node
            Node of the tree

    `clear_knowledge_graph(self)`
    :   Clears the knowledge graph.

    `clear_views(self)`
    :   Clears the views.

    `clone_stroke_group_node(self, stroke_group_node: uim.model.semantics.node.StrokeGroupNode, target_parent_node: uim.model.semantics.node.StrokeGroupNode = None, clone_semantics: bool = True, clone_child_stroke_nodes: bool = True, clone_child_group_nodes: bool = False, raise_exception: bool = False, store_source_node_reference_transient_key: str = None) ‑> uim.model.semantics.node.StrokeGroupNode`
    :   Clone stroke group node.
        
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

    `clone_stroke_node(self, stroke_node: uim.model.semantics.node.StrokeNode, target_parent_node: uim.model.semantics.node.StrokeGroupNode = None, clone_semantics: bool = True) ‑> uim.model.semantics.node.StrokeNode`
    :   Cloning a stroke node.
        
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

    `get_channel_data_instance(self, stroke: uim.model.inkdata.strokes.Stroke, ink_sensor_type: Union[uim.model.inkinput.inputdata.InkSensorType, str]) ‑> Optional[uim.model.inkinput.sensordata.ChannelData]`
    :   Get channel data instance.
        
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

    `get_channel_data_values(self, stroke: uim.model.inkdata.strokes.Stroke, ink_sensor_type: Union[uim.model.inkinput.inputdata.InkSensorType, str]) ‑> List[float]`
    :   Get channel data values.
        
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

    `get_sensor_channel(self, stroke: uim.model.inkdata.strokes.Stroke, ink_sensor_type: Union[uim.model.inkinput.inputdata.InkSensorType, str]) ‑> Optional[uim.model.inkinput.inputdata.SensorChannel]`
    :   Get sensor channel.
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

    `get_sensor_channel_types(self, stroke: uim.model.inkdata.strokes.Stroke)`
    :   Get sensor channel types.
        
        Parameters
        ----------
        stroke: `Stroke`
            Stroke object
        
        Returns
        -------
        sensor_channel_types: `List`
            List of sensor channel types

    `get_stroke_timestamp_and_pressure_values(self, stroke: uim.model.inkdata.strokes.Stroke, duplicate_first_and_last: bool = True) ‑> Tuple[List[float], List[float]]`
    :   Gets the timestamp and pressure values.
        
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

    `get_strokes_as_strided_array(self, layout: Optional[List[uim.model.inkdata.strokes.InkStrokeAttributeType]] = None, policy: uim.model.helpers.policy.HandleMissingDataPolicy = HandleMissingDataPolicy.FILL_WITH_ZEROS) ‑> Tuple[List, List[uim.model.inkdata.strokes.InkStrokeAttributeType]]`
    :   Returns all the strokes in the document, where each stroke is an array with stride 4.
        
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

    `get_strokes_as_strided_array_extended(self, layout: Optional[List[uim.model.inkdata.strokes.InkStrokeAttributeType]] = None, policy: uim.model.helpers.policy.HandleMissingDataPolicy = HandleMissingDataPolicy.FILL_WITH_ZEROS, include_stroke_idx: bool = False) ‑> Tuple[List[List[float]], List[uim.model.inkdata.strokes.InkStrokeAttributeType]]`
    :   Returns all the strokes in the document, where each stroke is an array with stride len(layout)
        
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

    `has_brushes(self) ‑> bool`
    :   Checks if the Ink Model has brushes configured.
        
        Returns
        -------
        flag: `bool`
            Flag if brushes have been configured for InkModel

    `has_ink_data(self) ‑> bool`
    :   Checks if the Ink Model has ink data configured.
        
        Returns
        -------
        flag: `bool`
            Flag if ink data have been configured for InkModel

    `has_ink_structure(self) ‑> bool`
    :   Checks if the Ink Model has ink structure configured.
        
        Returns
        -------
        flag: `bool`
            Flag if input data have been configured for InkModel

    `has_input_data(self) ‑> bool`
    :   Checks if the Ink Model has input data configured.
        
        Returns
        -------
        flag: `bool`
            Flag if input data have been configured for InkModel

    `has_knowledge_graph(self) ‑> bool`
    :   Checks if the Ink Model has knowledge graph configured.
        
        Returns
        -------
        flag: `bool`
            Flag if knowledge graph have been configured for InkModel

    `has_properties(self) ‑> bool`
    :   Checks if the Ink Model has properties configured.
        
        Returns
        --------
        flag: `bool`
            Flag if properties have been configured for InkModel

    `has_tree(self, name: str) ‑> bool`
    :   Check if the named tree exists.
        
        Parameters
        ----------
        name: str
            Name of the tree
        
        Returns
        -------
        bool
            Flag if the tree exists

    `is_node_registered(self, node: uim.model.semantics.node.InkNode)`
    :   Check if node is registered.
        
        Parameters
        ----------
        node: `InkNode`
            Node to check
        
        Returns
        -------
        flag: `bool`
            Flag if node is already registered in tree.

    `register_node(self, node: uim.model.semantics.node.InkNode)`
    :   Register ink node.
        
        Parameters
        ----------
        node: `InkNode`
            Reference to node.
        
        Raises
        ------
        InkModelException
            If Node with URI already exist in the tree

    `reinit_sensor_channel(self, ink_sensor_type: uim.model.inkinput.inputdata.InkSensorType, ink_sensor_metric: Optional[uim.model.inkinput.inputdata.InkSensorMetricType] = None, resolution: Optional[float] = None, channel_min: Optional[float] = None, channel_max: Optional[float] = None, precision: Optional[int] = None, index: Optional[int] = None, name: Optional[str] = None, data_type=None, ink_input_provider_id: Optional[uuid.UUID] = None, input_device_id: Optional[uuid.UUID] = None)`
    :   Reinitialize the sensor channel. This should be done when you want to modify the sensor data (because by
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

    `remove_node(self, node: uim.model.semantics.node.InkNode)`
    :   Remove a node.
        
        Parameters
        ----------
        node: `InkNode`
           Node to be remove
        
        Notes
        -----
        This function removes the triples and the node as well.

    `remove_semantic_triple(self, subject: str, predicate: str, obj: str)`
    :   Remove a semantic triple from the object.
        
        Parameters
        ----------
        subject: str
            Subject of the statement.
        
        predicate: str
            Predicate of the statement.
        
        obj: str
            Object of the statement.

    `remove_tree(self, name: str)`
    :   Removing view tree from model.
        
        Parameters
        ----------
        name: str
            Name of the tree that should be removed. If the tree does not exist, nothing happens.

    `sensor_data_lookup(self, stroke: uim.model.inkdata.strokes.Stroke, ink_sensor_type: uim.model.inkinput.inputdata.InkSensorType, return_channel_data_instance: bool = False) ‑> Union[List[float], uim.model.inkinput.sensordata.ChannelData]`
    :   Sensor data lookup.
        
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

    `stroke_by_id(self, stroke_uuid: uuid.UUID) ‑> uim.model.inkdata.strokes.Stroke`
    :   Returns the stroke for a specific UUID.
        
        Parameters
        ----------
        stroke_uuid: `UUID`
            ID of the stroke
        
        Returns
        -------
        stroke: `Stroke`
            Instance of the  stroke

    `tree(self, name: str) ‑> Optional[uim.model.ink.InkTree]`
    :   Return named tree.
        Returns
        -------
        Optional[InkTree]
            The main ink tree

    `unregister_node(self, node: uim.model.semantics.node.InkNode)`
    :   Unregister a node.
        
        Parameters
        ----------
        node: `InkNode`
            Node to unregister
        
        Notes
        -----
        This function removes the triples for the node as well.

    `view(self, name: str) ‑> uim.model.ink.ViewTree`
    :   Returns the view.
        
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

    `view_root(self, name: str) ‑> uim.model.semantics.node.StrokeGroupNode`
    :   Returns the root for a view.
        
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

`InkTree(name: str = 'main')`
:   InkTree
    =======
    The digital ink content, contained within a universal ink model, is organized in logical trees of ink nodes -
    they represent hierarchically organized ink-centric structures, and are also referred to as ink trees.
    
    Parameters
    ----------
    name: str -
        Name of the view

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * uim.model.ink.ViewTree

    ### Instance variables

    `model: uim.model.ink.InkModel`
    :   Reference to the model. (`InkModel`)

    `name: str`
    :   The primary name associated with this ink tree. (`str`, read-only)

    `root: uim.model.semantics.node.StrokeGroupNode`
    :   Root node of the tree. (`StrokeGroupNode`)

    ### Methods

    `register_node(self, node: uim.model.semantics.node.InkNode)`
    :   Register node.
        
        Parameters
        ----------
        node: `InkNode`
            Node that needs to be registered

    `register_sub_tree(self, node: uim.model.semantics.node.InkNode)`
    :   Register sub tree.
        
        Parameters
        ----------
        node: `InkNode`
            Sub tree that needs to be registered

    `unregister_node(self, node: uim.model.semantics.node.InkNode)`
    :   Unregister node.
        
        Parameters
        ----------
        node: `InkNode`
            Node that needs to be unregistered

    `unregister_sub_tree(self, node: uim.model.semantics.node.InkNode)`
    :   Unregister sub tree.
        
        Parameters
        ----------
        node: `InkNode`
            Sub tree that needs to be unregistered

`SensorDataRepository(sensor_data: List[uim.model.inkinput.sensordata.SensorData] = None)`
:   SensorDataRepository
    ====================
    A collection of data repositories, holding raw sensor input, input device/provider configurations, sensor channel
    configurations, etc. Each data repository keeps certain data-sets isolated and is responsible for
    specific type(s) of data.
    
    Parameters
    ----------
    sensor_data: List[SensorData]
            List of sensor data items. [optional]

    ### Ancestors (in MRO)

    * abc.ABC

    ### Instance variables

    `sensor_data: List[uim.model.inkinput.sensordata.SensorData]`
    :   List of SensorData objects. (`List[SensorData]`)

    ### Methods

    `add(self, sensor_data: uim.model.inkinput.sensordata.SensorData)`
    :   Adding a sensor sample.
        
        Parameters
        ----------
        sensor_data: `SensorData`
            Adding a sensor data sample

    `sensor_data_by_id(self, uimid: uuid.UUID) ‑> uim.model.inkinput.sensordata.SensorData`
    :   Returns the sensor data samples for a specific id.
        
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

`ViewTree(name: str)`
:   View tree
    ----------
    The view is a tree structure.

    ### Ancestors (in MRO)

    * uim.model.ink.InkTree
    * abc.ABC
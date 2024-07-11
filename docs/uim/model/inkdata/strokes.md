Module uim.model.inkdata.strokes
================================

Variables
---------

    
`DEFAULT_EXTENDED_LAYOUT: List[uim.model.inkdata.strokes.InkStrokeAttributeType]`
:   Default extended layout for strokes.

Classes
-------

`InkStrokeAttributeType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   InkStrokeAttributeType
    ======================
    This class supports combined all possible spline and sensor data.
    It is used by as_strided_array_extended() and stroke_resampling.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `SENSOR_ALTITUDE`
    :

    `SENSOR_AZIMUTH`
    :

    `SENSOR_PRESSURE`
    :

    `SENSOR_RADIUS_X`
    :

    `SENSOR_RADIUS_Y`
    :

    `SENSOR_ROTATION`
    :

    `SENSOR_TIMESTAMP`
    :

    `SPLINE_ALPHA`
    :

    `SPLINE_BLUE`
    :

    `SPLINE_GREEN`
    :

    `SPLINE_OFFSETS_X`
    :

    `SPLINE_OFFSETS_Y`
    :

    `SPLINE_RED`
    :

    `SPLINE_ROTATIONS`
    :

    `SPLINE_SCALES_X`
    :

    `SPLINE_SCALES_Y`
    :

    `SPLINE_SIZES`
    :

    `SPLINE_X`
    :

    `SPLINE_Y`
    :

    ### Static methods

    `get_attribute_type_by_sensor(sensor_type: uim.model.inkinput.inputdata.InkSensorType)`
    :   Get the attribute type by sensor type.
        Parameters
        ----------
        sensor_type: InkSensorType
            The sensor type.
        
        Returns
        -------
        Optional[InkStrokeAttributeType]
            The attribute type.

    `get_sensor_type_by_attribute(attribute_type: InkStrokeAttributeType) ‑> Optional[uim.model.inkinput.inputdata.InkSensorType]`
    :   Get the sensor type by attribute type.
        Parameters
        ----------
        attribute_type: InkStrokeAttributeType
            The attribute type.
        
        Returns
        -------
        Optional[InkSensorType]
            The sensor type.

    ### Methods

    `is_sensor_attribute(self) ‑> bool`
    :   Check if the attribute is a sensor attribute.
        Returns
        -------
        bool
            True if the attribute is a sensor attribute, False otherwise.

    `is_spline_attribute(self) ‑> bool`
    :   Check if the attribute is a spline attribute.
        Returns
        -------
        bool
            True if the attribute is a spline attribute, False otherwise.

    `resolve_path_point_property(self, path_point_properties: uim.model.inkdata.strokes.PathPointProperties) ‑> Any`
    :   Resolve the path point property.
        Parameters
        ----------
        path_point_properties: PathPointProperties
            The path point properties.
        
        Returns
        -------
        Any
            The resolved property.

`LayoutMask(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   LayoutMask
    ==========
    Specifies the various geometric and appearance attributes of a path point as bit flags.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ALPHA`
    :

    `BLUE`
    :

    `GREEN`
    :

    `OFFSET_X`
    :

    `OFFSET_Y`
    :

    `OFFSET_Z`
    :

    `RED`
    :

    `ROTATION`
    :

    `SCALE_X`
    :

    `SCALE_Y`
    :

    `SCALE_Z`
    :

    `SIZE`
    :

    `TANGENT_X`
    :

    `TANGENT_Y`
    :

    `X`
    :

    `Y`
    :

    `Z`
    :

`PathPointProperties(size: float = 0.0, red: float = 0.0, green: float = 0.0, blue: float = 0.0, alpha: float = 0.0, rotation: float = 0.0, scale_x: float = 0.0, scale_y: float = 0.0, scale_z: float = 0.0, offset_x: float = 0.0, offset_y: float = 0.0, offset_z: float = 0.0)`
:   PathPointProperties
    ===================
    A simple data model, which may hold size, color components and matrix transformational components.
    
    Parameters
    ----------
    size: float
        Size of the brush.
    red: float
        Color value [0, 1] for red channel.
    green: float
        Color value [0, 1] for green channel.
    blue: float
        Color value [0, 1] for blue channel.
    alpha: float
        Color value [0, 1] for alpha channel.
    rotation: float
        Brush rotation z value.
    scale_x: float
        Brush scale x value.
    scale_y: float
        Brush scale y value.
    scale_z: float
        Brush scale z [for 3D rendering].
    offset_x: float
        Brush offset x value.
    offset_y: float
        Brush offset y value.
    offset_z: float
        Brush offset z [for 3D rendering].
    
    References
    ----------
    [1] WILL SDK for ink - Rendering pipeline URL: https://developer-docs.wacom.com/sdk-for-ink/docs/pipeline
    [2] Ink Designer to configure rendering pipeline: http://ink-designer.trafficmanager.net/

    ### Ancestors (in MRO)

    * uim.model.base.HashIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Static methods

    `color(rgba: int) ‑> Tuple[float, float, float, float]`
    :   Decode integer encoded RBGA value into float.
        
        Parameters
        ----------
        rgba: int
            Color encoded in a single integer value
        
        Returns
        -------
        red - `float`
            Red value
        green - `float`
            Green value
        blue - `float`
            Blue value
        alpha - `float`
            Alpha value

    `rgba(red: float, green: float, blue: float, alpha: float) ‑> int`
    :   Encode RGBA values to a single integer value.
        
        Parameters
        ----------
        red: int -
            Red value
        green: int -
            Green value
        blue: int -
            Blue value
        alpha: int -
            Alpha value
        
        Returns
        -------
        rgba: int
            Color values encode as one single integer value

    ### Instance variables

    `alpha: float`
    :   Alpha value for channel; value between [0. - 1.]. (`float`)

    `blue: float`
    :   Color value for blue channel; value between [0. - 1.]. (`float`)

    `green: float`
    :   Color value for green channel; value between [0. - 1.]. (`float`)

    `offset_x: float`
    :   Offset x value. (`float`)

    `offset_y: float`
    :   Offset y value. (`float`)

    `offset_z: float`
    :   Offset z value. (`float`)

    `red: float`
    :   Color value for red channel; value between [0. - 1.]. (`float`)

    `rotation: float`
    :   Brush rotation. (`float`)

    `scale_x: float`
    :   Brush scale x value. (`float`)

    `scale_y: float`
    :   Brush scale y value. (`float`)

    `scale_z: float`
    :   Brush scale z value. (`float`)

    `size: float`
    :   Size of the brush; value between [0. - 1.]. (`float`)

`Spline(layout_mask: int, data: List[Union[float, int]], ts: float = 0.0, tf: float = 1.0)`
:   Spline
    ======
    The Catmull-Rom spline is defined in the scope of the Stroke using the following properties:
    
    - **ts, tf** - Spline start and end parameters
    - **spline** - a sequence of spline data points
    - **color** - a sequence of color values (per spline data point; if provided, the length of this sequence must be
                  equal to the spline points count)
    
    Parameters
    ----------
    layout_mask: int
        Configured layout mask
    data: List[float]
        List of spline values
    ts: float
        Start parameter
    tf: float
        Final parameter

    ### Ancestors (in MRO)

    * abc.ABC

    ### Instance variables

    `data: List[float]`
    :   Gets or sets a list of spline values. (`List[float]`, read-only)

    `layout_mask: int`
    :   Gets a bitmask representation of the spline's data layout. (`int`, read-only)

    `tf: float`
    :   Final parameter for the last Catmull-Rom segment. (`float`, read-only)

    `ts: float`
    :   Start parameter for the first Catmull-Rom segment. (`float`, read-only)

`Stroke(sid: uuid.UUID = None, sensor_data_offset: int = None, sensor_data_id: uuid.UUID = None, sensor_data_mapping: list = None, style: uim.model.inkdata.strokes.Style = None, random_seed: int = 0, property_index: int = 0, spline: uim.model.inkdata.strokes.Spline = None)`
:   Stroke Geometry
    ===============
    The geometry of an ink stroke is represented by its Stroke.
    A Stroke is defined as a combination of:
    
        - A Catmull-Rom spline in the form of a sequence of data points (mandatory), including per-point
          transformational data (optional)
        - Rendering configuration about how the spline should be visualized (optional)
        - Reference to raw input data (SensorData instance), which the path originates from (optional)
    
    Parameters
    ----------
     sid: `UUID`
        Stroke unique identifier
    sensor_data_offset: `int`
        Index of points mapping between raw and processed paths.
    sensor_data_id: `UUID`
        Reference UUID of sensor data.
    sensor_data_mapping: list
        Explicit mapping between indices of Path and SensorData, used when input rate is very high and
        provides unwanted points.
    style: `Style`
        The Style object associated with this stroke.
    random_seed: `int`
        A random seed used for randomly generated attributes of a stroke.
    spline: `Spline`
        The stroke's Catmull-Rom spline.
    
    Examples
    --------
    >>> from uim.model.inkdata.brush import BrushPolygon, BrushPolygonUri, RasterBrush, RotationMode, BlendMode
    >>> from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask
    >>>
    >>> raster_brush_0: RasterBrush = RasterBrush(
    >>> name="app://qa-test-app/raster-brush/MyRasterBrush",
    >>> spacing=10., scattering=5., rotation=RotationMode.TRAJECTORY, shape_textures=[bytes([10, 20]),
    >>>                                                                               bytes([30, 20])],
    >>> fill_width=2.0, fill_height=0.3,
    >>> fill_texture=bytes([10, 10, 20, 15, 17, 20, 25, 16, 34, 255, 23, 0, 34, 255, 23, 255]),
    >>> randomize_fill=False, blend_mode=BlendMode.SOURCE_OVER)
    >>> # Create a spline object - 9 data points, each consisting of X, Y, Size, Red, Green, Blue, Alpha
    >>> spline_1: Spline = Spline(
    >>>     LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value | LayoutMask.RED.value | LayoutMask.GREEN.value
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

    ### Ancestors (in MRO)

    * uim.model.base.UUIDIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `alpha: List[int]`
    :   Color values [0, 255] for alpha channel. (`List[int]`)

    `blue: List[int]`
    :   Color values [0, 255] for blue channel. (`List[int]`)

    `bounding_box: uim.model.semantics.structures.BoundingBox`
    :   Bounding box for path stroke. (`BoundingBox`)

    `end_parameter: float`
    :   End parameter of the stroke. (`float`)

    `green: List[int]`
    :   Color values [0, 255] for green channel. (`List[int]`)

    `layout_mask: int`
    :   Layout mask for the stroke. (`int`)

    `offsets_x: List[float]`
    :   List of x offsets.

    `offsets_y: List[float]`
    :   List of y offsets. (`List[float]`)

    `offsets_z: List[float]`
    :   List of z offsets. (`List[float]`)

    `points_count: int`
    :   Number of points of sample points. (`int`)

    `precision_scheme: uim.codec.context.scheme.PrecisionScheme`
    :   An object that defines the precisions used for storing the stroke data. If set to None, stroke data is stored
        using floating point values. (`PrecisionScheme`)

    `properties_index: int`
    :   Setting the properties index. (`int`)

    `random_seed: int`
    :   Random seed used for randomly generated attributes of a stroke. (`int`)

    `red: List[int]`
    :   List of color values [0, 255] for red channel. (`List[int]`)

    `rotations: List[float]`
    :   List of rotations. (`List[float]`)

    `scales_x: List[float]`
    :   List of x scales. (`List[float]`)

    `scales_y: List[float]`
    :   List of y scales. (`List[float]`)

    `scales_z: List[float]`
    :   List of z scales. (`List[float]`)

    `sensor_data_id: uuid.UUID`
    :   Reference id sensor data. (`UUID`)

    `sensor_data_mapping: List[int]`
    :   Explicit mapping between indices of Path and SensorData, used when input rate is very high and
        provides unwanted points. (`List[int]`)

    `sensor_data_offset: int`
    :   Index of points mapping between raw and processed paths. (`int`)

    `sizes: List[float]`
    :   List of size values. (`List[float]`)

    `spline_max_x: float`
    :   Maximum value of x spline. (`float`)

    `spline_max_y: float`
    :   Maximum value of y spline. (`float`)

    `spline_min_x: float`
    :   Minimum value of x spline. (`float`)

    `spline_min_y: float`
    :   Minimum value of y spline. (`float`)

    `splines_x: List[float]`
    :   List of splines x. (`List[float]`)

    `splines_y: List[float]`
    :   List of splines y. (`List[float]`)

    `splines_z: List[float]`
    :   List of splines z. (`List[float]`)

    `start_parameter: float`
    :   Start parameter of the stroke. (`float`)

    `style: uim.model.inkdata.strokes.Style`
    :   Style that is applied to the path of the stroke. (`Style`)

    `tangent_x: List[float]`
    :   List of tangent x values. (`List[float]`)

    `tangent_y: List[float]`
    :   List of tangent y values. (`List[float]`)

    `uri: str`
    :   The URI of the stroke. (`str`)

    ### Methods

    `as_strided_array_extended(self, ink_model: InkModel, layout: Optional[List[uim.model.inkdata.strokes.InkStrokeAttributeType]] = None, handle_missing_data: uim.model.helpers.policy.HandleMissingDataPolicy = HandleMissingDataPolicy.FILL_WITH_ZEROS, remove_duplicates_at_ends: bool = True) ‑> Optional[List[float]]`
    :   Create a strided array of the stroke data with the given layout.
        Parameters
        ----------
        ink_model: InkModel
            The ink model.
        layout: List[InkStrokeAttributeType]
            The layout of the strided array.
        handle_missing_data: HandleMissingDataPolicy
            The policy to handle missing data.
        remove_duplicates_at_ends: bool
            Remove duplicates at the ends.

    `get_pressure_values(self) ‑> Optional[List[float]]`
    :   Get the pressure values.
        
        Returns
        -------
        List[float]
            List of pressure values

    `get_sensor_point(self, index: int, sensor_channel_values: List[float] = None) ‑> float`
    :   Get the sensor point.
        
        Parameters
        ----------
        index: int
            The index.
        sensor_channel_values: List[float]
            The sensor channel values.
        
        Returns
        -------
        float
            The sensor point.
        
        Raises
        ------
        ValueError
            If the index is out of range.

    `get_spline_attribute_values(self, attribute_type: uim.model.inkdata.strokes.InkStrokeAttributeType) ‑> List[float]`
    :   Get the spline attribute values.
        
        Parameters
        ----------
        attribute_type: InkStrokeAttributeType
            The attribute type.
        
        Returns
        -------
        List[float]
            List of values.

    `get_timestamp_values(self) ‑> Optional[List[float]]`
    :   Get the timestamp values.
        
        Returns
        -------
        Optional[List[float]]
            List of timestamp values

    `set_pressure_values(self, pressure_values: List[float])`
    :   Set the pressure values.
        
        Parameters
        ----------
        pressure_values: List[float]
            List of pressure values

    `set_timestamp_values(self, timestamp_values: List[float])`
    :   Set the timestamp values.
        
        Parameters
        ----------
        timestamp_values: list
            List of timestamp values

`Style(properties: uim.model.inkdata.strokes.PathPointProperties = None, brush_uri: str = None, particles_random_seed: int = 0, render_mode_uri: str = 'will://rasterization/3.0/blend-mode/SourceOver')`
:   Style
    =====
    The `Style` is defined as a combination of a `PathPointProperties` configuration, reference to a Brush,
    a random number generator seed value and rendering method type. Setting the Style property allows overriding of
    specific path point properties, color components and/or matrix transformational components.
    A `Style` with `PathPointProperties` configuration should be normally used to define constant path components.
    
    Parameters
    ----------
    properties: `PathPointProperties`
        Static values of properties which do not exist per per path point
    brush_uri: str
        Reference to Brush used for stroke rasterization
    particles_random_seed: int
        Particles random seed, required for particle strokes
    render_mode_uri: str
        Render mode URI

    ### Ancestors (in MRO)

    * abc.ABC

    ### Instance variables

    `brush_uri: str`
    :   Reference to Brush used for stroke rasterization using the URI. (`str`, read-only)

    `particles_random_seed`
    :   Particles random seed, required for particle strokes.  (`int`, read-only)

    `path_point_properties: uim.model.inkdata.strokes.PathPointProperties`
    :   Static values of properties which do not exist per path point. (`PathPointProperties`, read-only)

    `render_mode_uri`
    :   Defines additional information about stroke visualisation, such as ERASER. (`str`)
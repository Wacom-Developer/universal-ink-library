Module uim.model.inkdata.brush
==============================

Classes
-------

`BlendMode(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   BlendMode
    =========
    The blend mode enum lists the different blend modes which can be applied to raster brushes.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `COPY`
    :   Only the new shape is shown. Also known as NONE.

    `DESTINATION_OUT`
    :   The existing content is kept where it doesn't overlap the new shape. Also known as ERASE.

    `DESTINATION_OVER`
    :   New shapes are drawn behind the existing canvas content. Also known as NORMAL_REVERSE.

    `LIGHTER`
    :   Where both shapes overlap the color is determined by adding color values. Also known as ADD.

    `MAX`
    :   The result is the maximum of both color. The result is a lighter color.

    `MIN`
    :   The result is the minimum of both color. The result is a darker color.

    `SOURCE_OVER`
    :   This is the default setting and draws new shapes on top of the existing canvas content. Also known as NORMAL.

`BlendModeURIs()`
:   BlendModeURIs
    =============
    URIs for the different blend modes.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Class variables

    `COPY: str`
    :   URI for BlendMode.Copy

    `DESTINATION_OUT: str`
    :   URI for BlendMode.DestinationOut

    `DESTINATION_OVER: str`
    :   URI for BlendMode.DestinationOver

    `LIGHTER: str`
    :   URI for BlendMode.Lighter

    `MAX: str`
    :   URI for BlendMode.Max

    `MIN: str`
    :   URI for BlendMode.Min

    `SOURCE_OVER: str`
    :   URI for BlendMode.SourceOver

`Brush()`
:   Brush
    -----
    Abstract class for brushes.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * uim.model.inkdata.brush.RasterBrush
    * uim.model.inkdata.brush.VectorBrush

`BrushPolygon(min_scale: float, points: Optional[List[Tuple[float, float]]] = None, indices: Optional[List[int]] = None)`
:   BrushPolygon
    ============
    Describes vector brush prototype.
    
    Parameters
    ----------
    points: Optional[List[Tuple[float, float]]] (optional) [default: None]
        List of points for polygon
    indices: Optional[List[int]] (optional) [default: None]
        List of indexes

    ### Ancestors (in MRO)

    * abc.ABC

    ### Instance variables

    `coord_x: List[float]`
    :   List of coordinates for x value. (`List[float]`, read-only)

    `coord_y: List[float]`
    :   List of coordinates for y value. (`List[float]`, read-only)

    `coord_z: List[float]`
    :   List of coordinates for z value. (`List[float]`, read-only)

    `indices: List[int]`
    :   List of indices of brush prototype [for 3D rendering]. (`List[int]`, read-only)

    `min_scale: float`
    :   Minimum scale of the brush sample, after which this shape is applied. (`float`, read-only)
        
        Notes
        -----
        This value is used by the brush applier in order to pick the proper shape according to the actual brush scale.

    `points: List[Tuple[float, float]]`
    :   List of coordinates for x value. (`List[Tuple[float, float]]`, read-only)

`BrushPolygonUri(uri: str, min_scale: float)`
:   BrushPolygonUri
    ===============
    Represents a vector brush shape that is specified with a URI.
    
    Parameters
    ----------
    uri: ´str´
        URI string that identifies the shape.
    min_scale: ´float´
        Minimum scale of the brush sample, after which this shape is applied.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Instance variables

    `min_scale: float`
    :   Minimum scale of the brush sample, after which this shape is applied. (´float´)
        
        Notes
        -----
        This value is used by the brush applier in order to pick the proper shape according to the actual brush scale.

    `shape_uri: str`
    :   URI string that identifies the shape. (´str´)

`Brushes(vector_brushes: Optional[List[uim.model.inkdata.brush.VectorBrush]] = None, raster_brushes: Optional[List[uim.model.inkdata.brush.RasterBrush]] = None)`
:   Brushes
    ========
    Brush descriptions, needed for uim rasterization.
    
    Parameters
    ----------
    vector_brushes: Optional[List[VectorBrush]] (optional) [default: None]
        List of vector brushes
    raster_brushes: Optional[List[RasterBrush] (optional) [default: None]
        List of raster brushes

    ### Instance variables

    `raster_brushes: List[uim.model.inkdata.brush.RasterBrush]`
    :   List of defined raster brushes. (`List[RasterBrush]`)

    `vector_brushes: List[uim.model.inkdata.brush.VectorBrush]`
    :   List of defined vector brushes. (`List[VectorBrush]`)

    ### Methods

    `add_raster_brush(self, brush: uim.model.inkdata.brush.RasterBrush)`
    :   Adding raster brush.
        
        Parameters
        ----------
        brush: `RasterBrush`
            Raster brush

    `add_vector_brush(self, brush: uim.model.inkdata.brush.VectorBrush)`
    :   Adding a vector brush.
        
        Parameters
        ----------
        brush: `VectorBrush`
            Vector brush

    `remove_raster_brush(self, name: str)`
    :   Remove raster brush from brushes. If the brush with the name does not exist, no operation is performed.
        
        Parameter
        ---------
        name: str
            Name of brush that should be remove

    `remove_vector_brush(self, name: str)`
    :   Remove vector brush from brushes.
        If the brush with the name does not exist, no operation is performed.
        
        Parameters
        ----------
        name: `str`
            Name of brush that should be remove.

`RasterBrush(name: str, spacing: float, scattering: float, rotation: uim.model.inkdata.brush.RotationMode, shape_textures: Optional[List[bytes]] = None, shape_texture_uris: Optional[List[str]] = None, fill_texture: Optional[bytes] = None, fill_texture_uri: Optional[str] = None, fill_width: float = 0.0, fill_height: float = 0.0, randomize_fill: bool = False, blend_mode: uim.model.inkdata.brush.BlendMode = BlendMode.SOURCE_OVER)`
:   RasterBrush
    ===========
    A configuration which allows rendering of an interpolated Catmull-Rom spline as a raster image by applying a
    specific sprite for each interpolated point, depending on its size.
    
    Parameters
    ----------
    name: `str`
        Brush descriptor
    spacing: `float`
        Distance between neighbour particles.
    scattering: `float`
        The scattering along the curve normal.
    rotation: `RotationMode`
        The particle rotation mode of the brush.
    shape_textures: Optional[List[bytes]] (optional) [default: None]
        List of png images that contains the shape texture.
    shape_texture_uris: Optional[List[str]] (optional) [default: None]
        List of URIs that contains the shape texture.
    fill_texture: Optional[bytes]
        List of png image that contains the fill texture.
    fill_texture_uri: Optional[str] (optional) [default: None]
        List of URIs that describes the fill textures.
    fill_width: `float` (optional) [default: 0.]
        Width of the fill tile.
    fill_height: `float` (optional) [default: 0.]
        Height of the fill tile.
    randomize_fill: `bool` (optional) [default: False]
        Specifies whether the fill texture is randomly displaced.
    blend_mode: `BlendMode` (optional) [default: BlendMode.SOURCE_OVER]
        The applied blend mode.

    ### Ancestors (in MRO)

    * uim.model.inkdata.brush.Brush
    * abc.ABC

    ### Instance variables

    `blend_mode: uim.model.inkdata.brush.BlendMode`
    :   The applied blend mode. (`BlendMode`, read-only)

    `fill_height: float`
    :   Height of the fill tile. (`float`, read-only)

    `fill_texture: bytes`
    :   List of png image that contains the fill texture. (`bytes`, read-only)

    `fill_texture_uri: str`
    :   The fill texture URI. (`str`, read-only)

    `fill_width: float`
    :   Width of the fill tile. (`float`, read-only)

    `name: str`
    :   Name of the raster brush. (`str`, read-only)

    `randomize_fill: bool`
    :   Specifies whether the fill texture is randomly displaced. (`bool`, read-only)

    `rotation: uim.model.inkdata.brush.RotationMode`
    :   The particle rotation mode of the brush. (`float`, read-only)

    `scattering: float`
    :   The scattering along the curve normal. (`float`, read-only)

    `shape_texture_uris: List[str]`
    :   URI identifying the fillTexture. (`List[str]`, read-only)

    `shape_textures: List[bytes]`
    :   List of png images that contains the shape texture; byte array with PNG content.
        (`List[bytes]`, read-only)

    `spacing: float`
    :   Distance between neighbour particles. (`float`, read-only)

`RotationMode(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   RotationMode
    ============
    Brush rotation modes.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `NONE`
    :   Indicates that the shape will not be rotated.

    `RANDOM`
    :   Indicates that the shape will be rotated randomly before it renders.

    `TRAJECTORY`
    :   Indicates that the shape will be rotated to match the path trajectory.

`VectorBrush(name: str, prototypes: List[Any] = None, spacing: float = 1.0)`
:   VectorBrush
    ===========
    A configuration which allows rendering of an interpolated Catmull-Rom spline as a vector spline by applying a
    specific polygon for each interpolated point, depending on its size and merging result afterwards.
    
    Parameters
    ----------
    name: str
        Name of the brush
    prototypes: list
        Prototypes for brush
    spacing: float (optional) [default: 1.]
        Spacing value

    ### Ancestors (in MRO)

    * uim.model.inkdata.brush.Brush
    * abc.ABC

    ### Instance variables

    `name: str`
    :   Name of the vector brush. (`str`, read-only)

    `prototypes: List[Union[uim.model.inkdata.brush.BrushPolygon, uim.model.inkdata.brush.BrushPolygonUri]]`
    :   Polygon prototype for the brush. (`List[Any]`,  read-only).
        
        Notes
        -----
        The prototype can be either URI-based for prototype with a defined polygon geometry.
        
        See also
        --------
        - `BrushPolygon` - List of polygon sample points
        - `BrushPolygonUri` - List of URI polygon prototype

    `spacing: float`
    :   Spacing value. (`float`, read-only)
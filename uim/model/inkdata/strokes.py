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
import ctypes
import uuid
from abc import ABC
from enum import Enum
from typing import Tuple, List, Optional

import numpy as np

from uim.codec.context.scheme import PrecisionScheme
from uim.model.base import UUIDIdentifier, HashIdentifier
from uim.model.inkdata.brush import BlendModeURIs
from uim.model.semantics.structures import BoundingBox


class LayoutMask(Enum):
    """
    Specifies the various geometric and appearance attributes of a path point as bit flags.
    """
    X = 0x1
    Y = 0x2
    Z = 0x4
    SIZE = 0x8
    ROTATION = 0x10
    RED = 0x20
    GREEN = 0x40
    BLUE = 0x80
    ALPHA = 0x100
    SCALE_X = 0x200
    SCALE_Y = 0x400
    SCALE_Z = 0x800
    OFFSET_X = 0x1000
    OFFSET_Y = 0x2000
    OFFSET_Z = 0x4000
    TANGENT_X = 0x8000
    TANGENT_Y = 0x10000


class PathPointProperties(HashIdentifier):
    """
    PathPointProperties
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
    """

    def __init__(self, size: float = 0., red: float = 0., green: float = 0., blue: float = 0., alpha: float = 0.,
                 rotation: float = 0.,
                 scale_x: float = 0., scale_y: float = 0., scale_z: float = 0.,
                 offset_x: float = 0., offset_y: float = 0., offset_z: float = 0.):
        super().__init__()
        self.__size = size
        self.__red = red
        self.__green = green
        self.__blue = blue
        self.__alpha = alpha
        self.__rotation = rotation
        self.__scale_x = scale_x
        self.__scale_y = scale_y
        self.__scale_z = scale_z
        self.__offset_x = offset_x
        self.__offset_y = offset_y
        self.__offset_z = offset_z

    @staticmethod
    def color(rgba: int) -> Tuple[float, float, float, float]:
        """
        Decode integer encoded RBGA value into float.

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
        """
        red: float = ((rgba >> 24) & 0xFF) / 255.0
        green: float = ((rgba >> 16) & 0xFF) / 255.0
        blue: float = ((rgba >> 8) & 0xFF) / 255.0
        alpha: float = (rgba & 0xFF) / 255.0
        return red, green, blue, alpha

    @staticmethod
    def rgba(red: float, green: float, blue: float, alpha: float) -> int:
        """
        Encode RGBA values to a single integer value.

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
        """
        r: int = int(red * 255)
        g: int = int(green * 255)
        b: int = int(blue * 255)
        a: int = int(alpha * 255)
        return ctypes.c_int32((r << 24) | (g << 16) | (b << 8) | a).value

    @property
    def size(self) -> float:
        """Size of the brush; value between [0. - 1.]. (`float`)"""
        return self.__size

    @property
    def red(self) -> float:
        """Color value for red channel; value between [0. - 1.]. (`float`)"""
        return self.__red

    @property
    def green(self) -> float:
        """Color value for green channel; value between [0. - 1.]. (`float`)"""
        return self.__green

    @property
    def blue(self) -> float:
        """Color value for blue channel; value between [0. - 1.]. (`float`)"""
        return self.__blue

    @property
    def alpha(self) -> float:
        """Alpha value for channel; value between [0. - 1.]. (`float`)"""
        return self.__alpha

    @property
    def rotation(self) -> float:
        """Brush rotation. (`float`)"""
        return self.__rotation

    @property
    def scale_x(self) -> float:
        """Brush scale x value. (`float`)"""
        return self.__scale_x

    @property
    def scale_y(self) -> float:
        """Brush scale y value. (`float`)"""
        return self.__scale_y

    @property
    def scale_z(self) -> float:
        """Brush scale z value. (`float`)"""
        return self.__scale_z

    @property
    def offset_x(self) -> float:
        """Offset x value. (`float`)"""
        return self.__offset_x

    @property
    def offset_y(self) -> float:
        """Offset y value. (`float`)"""
        return self.__offset_y

    @property
    def offset_z(self) -> float:
        """Offset z value. (`float`)"""
        return self.__offset_z

    @size.setter
    def size(self, size: float):
        self.__size = size

    @red.setter
    def red(self, red: float):
        self.__red = red

    @green.setter
    def green(self, green: float):
        self.__green = green

    @blue.setter
    def blue(self, blue: float):
        self.__blue = blue

    @alpha.setter
    def alpha(self, alpha: float):
        self.__alpha = alpha

    @rotation.setter
    def rotation(self, rotation: float):
        self.__rotation = rotation

    @scale_x.setter
    def scale_x(self, scale_x: float):
        self.__scale_x = scale_x

    @scale_y.setter
    def scale_y(self, scale_y: float):
        self.__scale_y = scale_y

    @scale_z.setter
    def scale_z(self, scale_z: float):
        self.__scale_z = scale_z

    @offset_x.setter
    def offset_x(self, offset_x: float):
        self.__offset_x = offset_x

    @offset_y.setter
    def offset_y(self, offset_y: float):
        self.__offset_y = offset_y

    @offset_z.setter
    def offset_z(self, offset_z: float):
        self.__offset_z = offset_z

    def __tokenize__(self) -> list:
        return [self.size, self.red, self.green, self.blue, self.alpha, self.rotation, self.scale_x, self.scale_y,
                self.scale_z, self.offset_x, self.offset_y, self.offset_z]

    def __repr__(self):
        return '<PathPointProperties: [size:={}, red:={}, green:={}, blue:={}, alpha:={}, rotation:={},' \
               'scale x:={}, scale y:={}, scale z:={}, offset x:={}, offset y:={}, offset z:={}]>' \
            .format(self.size,
                    self.red, self.green, self.blue, self.alpha,
                    self.rotation,
                    self.scale_x, self.scale_y, self.scale_z,
                    self.offset_x, self.offset_y, self.offset_z)


class Style(ABC):
    """
    Style
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
    """

    def __init__(self, properties: PathPointProperties = None, brush_uri: str = None, particles_random_seed: int = 0,
                 render_mode_uri: str = BlendModeURIs.SOURCE_OVER):
        self.__properties = properties if properties is not None else PathPointProperties()
        self.__brush_uri = brush_uri
        self.__particles_random_seed = particles_random_seed
        self.__render_mode_URI = render_mode_uri if render_mode_uri is not None and render_mode_uri != '' \
            else BlendModeURIs.SOURCE_OVER

    @property
    def path_point_properties(self) -> PathPointProperties:
        """Static values of properties which do not exist per per path point. (`PathPointProperties`, read-only)"""
        return self.__properties

    @property
    def brush_uri(self) -> str:
        """Reference to Brush used for stroke rasterization using the URI. (`str`, read-only)"""
        return self.__brush_uri

    @property
    def particles_random_seed(self):
        """Particles random seed, required for particle strokes.  (`int`, read-only) """
        return self.__particles_random_seed

    @property
    def render_mode_uri(self):
        """Defines additional information about stroke visualisation, such as ERASER. (`str`)"""
        return self.__render_mode_URI

    @render_mode_uri.setter
    def render_mode_uri(self, uri: str):
        self.__render_mode_URI = uri

    def __repr__(self):
        return '<Style : [id:={}, particles_random_seed:={}, render mode:={}>' \
            .format(self.__brush_uri,
                    self.__particles_random_seed,
                    self.__render_mode_URI)


class Spline(ABC):
    """
    Spline
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
    """

    def __init__(self, layout_mask: int, data: List[float], ts: float = 0., tf: float = 1.):
        self.__layout_mask: int = layout_mask
        self.__data: List[float] = data
        self.__ts: float = ts
        self.__tf: float = tf

    @property
    def data(self) -> List[float]:
        """Gets or sets a list of spline values. (`List[float]`, read-only)"""
        return self.__data

    @property
    def layout_mask(self) -> int:
        """Gets a bitmask representation of the spline's data layout. (`int`, read-only)"""
        return self.__layout_mask

    @property
    def ts(self) -> float:
        """Start parameter for the first Catmull-Rom segment. (`float`, read-only)"""
        return self.__ts

    @property
    def tf(self) -> float:
        """Final parameter for the last Catmull-Rom segment. (`float`, read-only)"""
        return self.__tf

    def __repr__(self):
        return f'<Spline : [mask:={self.layout_mask}]>'


class Stroke(UUIDIdentifier):
    """
    Stroke Geometry
    ---------------
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
    """

    def __init__(self, sid: uuid.UUID = None, sensor_data_offset: int = None, sensor_data_id: uuid.UUID = None,
                 sensor_data_mapping: list = None, style: Style = None, random_seed: int = 0, property_index: int = 0,
                 spline: Spline = None):
        super().__init__(sid)
        self.__start_parameter: float = 0.
        self.__end_parameter: float = 0.
        self.__spline_x: List[float] = []
        self.__spline_y: List[float] = []
        self.__spline_z: List[float] = []
        self.__size: List[float] = []
        self.__rotation: List[float] = []
        self.__scale_x: List[float] = []
        self.__scale_y: List[float] = []
        self.__scale_z: List[float] = []
        self.__offset_x: List[float] = []
        self.__offset_y: List[float] = []
        self.__offset_z: List[float] = []
        self.__red: List[int] = []
        self.__green: List[int] = []
        self.__blue: List[int] = []
        self.__alpha: List[int] = []
        self.__tangent_x: List[float] = []
        self.__tangent_y: List[float] = []
        self.__sensor_data_id: uuid.UUID = sensor_data_id
        self.__sensor_data_offset: int = sensor_data_offset or 0
        self._sensor_data_mapping: list = sensor_data_mapping or []
        self.__style: Style = style
        self.__random_seed: int = random_seed
        self.__properties_index: int = property_index
        self.__timestamp_cache = None
        self.__pressure_cache = None
        self.__precision_scheme: Optional[PrecisionScheme] = None
        if spline is not None:
            self.__import__(spline)

    def set_timestamp_values(self, timestamp_values):
        self.__timestamp_cache = timestamp_values

    def get_timestamp_values(self):
        return self.__timestamp_cache

    def set_pressure_values(self, pressure_values):
        self.__pressure_cache = pressure_values

    def get_pressure_values(self):
        return self.__pressure_cache

    @property
    def layout_mask(self) -> int:
        """Layout mask for the stroke. (`int`)"""
        mask: int = 0
        if len(self.__spline_x) > 0:
            mask |= LayoutMask.X.value
        if len(self.__spline_y) > 0:
            mask |= LayoutMask.Y.value
        if len(self.__spline_z) > 0:
            mask |= LayoutMask.Z.value
        if len(self.__size) > 0:
            mask |= LayoutMask.SIZE.value
        if len(self.__rotation) > 0:
            mask |= LayoutMask.ROTATION.value
        if len(self.__red) > 0:
            mask |= LayoutMask.RED.value
        if len(self.__green) > 0:
            mask |= LayoutMask.GREEN.value
        if len(self.__blue) > 0:
            mask |= LayoutMask.BLUE.value
        if len(self.__alpha) > 0:
            mask |= LayoutMask.ALPHA.value
        if len(self.__scale_x) > 0:
            mask |= LayoutMask.SCALE_X.value
        if len(self.__scale_y) > 0:
            mask |= LayoutMask.SCALE_Y.value
        if len(self.__scale_z) > 0:
            mask |= LayoutMask.SCALE_Z.value
        if len(self.__offset_x) > 0:
            mask |= LayoutMask.OFFSET_X.value
        if len(self.__offset_y) > 0:
            mask |= LayoutMask.OFFSET_Y.value
        if len(self.__offset_z) > 0:
            mask |= LayoutMask.OFFSET_Z.value
        if len(self.__tangent_x) > 0:
            mask |= LayoutMask.TANGENT_X.value
        if len(self.__tangent_y) > 0:
            mask |= LayoutMask.TANGENT_Y.value
        return mask

    @property
    def properties_index(self) -> int:
        """Setting the properties index. (`int`)"""
        return self.__properties_index

    @properties_index.setter
    def properties_index(self, properties_index: int):
        self.__properties_index = properties_index

    @property
    def start_parameter(self) -> float:
        """Start parameter of the stroke. (`float`)"""
        return self.__start_parameter

    @start_parameter.setter
    def start_parameter(self, s: float):
        self.__start_parameter = s

    @property
    def end_parameter(self) -> float:
        """End parameter of the stroke. (`float`)"""
        return self.__end_parameter

    @end_parameter.setter
    def end_parameter(self, e: float):
        self.__end_parameter = e

    @property
    def precision_scheme(self) -> PrecisionScheme:
        """An object that defines the precisions used for storing the stroke data. If set to None, stroke data is stored
        using floating point values. (`PrecisionScheme`)"""
        return self.__precision_scheme

    @precision_scheme.setter
    def precision_scheme(self, precision_scheme: PrecisionScheme):
        self.__precision_scheme = precision_scheme

    @property
    def sizes(self) -> List[float]:
        """List of size values. (`List[float]`)"""
        return self.__size

    @sizes.setter
    def sizes(self, size: list):
        self.__size = size

    @property
    def red(self) -> List[int]:
        """List of color values [0, 255] for red channel. (`List[int]`)"""
        return self.__red

    @red.setter
    def red(self, values: List[int]):
        self.__red = values

    @property
    def green(self) -> List[int]:
        """Color values [0, 255] for green channel. (`List[int]`)"""
        return self.__green

    @green.setter
    def green(self, values: List[int]):
        self.__green = values

    @property
    def blue(self) -> List[int]:
        """Color values [0, 255] for blue channel. (`List[int]`)"""
        return self.__blue

    @blue.setter
    def blue(self, values: List[int]):
        self.__blue = values

    @property
    def alpha(self) -> List[int]:
        """Color values [0, 255] for alpha channel. (`List[int]`)"""
        return self.__alpha

    @alpha.setter
    def alpha(self, values: List[int]):
        self.__alpha = values

    @property
    def rotations(self) -> List[float]:
        """List of rotations. (`List[float]`)"""
        return self.__rotation

    @rotations.setter
    def rotations(self, values: List[float]):
        self.__rotation = values

    @property
    def splines_x(self) -> List[float]:
        """List of splines x. (`List[float]`)"""
        return self.__spline_x

    @splines_x.setter
    def splines_x(self, spline_x: List[float]):
        self.__spline_x = spline_x

    @property
    def splines_y(self) -> List[float]:
        """List of splines y. (`List[float]`)"""
        return self.__spline_y

    @splines_y.setter
    def splines_y(self, spline_y: List[float]):
        self.__spline_y = spline_y

    @property
    def splines_z(self) -> List[float]:
        """List of splines z. (`List[float]`)"""
        return self.__spline_z

    @splines_z.setter
    def splines_z(self, spline_z: List[float]):
        self.__spline_z = spline_z

    @property
    def scales_x(self) -> List[float]:
        """List of x scales. (`List[float]`)"""
        return self.__scale_x

    @scales_x.setter
    def scales_x(self, scale: List[float]):
        self.__scale_x = scale

    @property
    def scales_y(self) -> List[float]:
        """List of y scales. (`List[float]`)"""
        return self.__scale_y

    @scales_y.setter
    def scales_y(self, scale: List[float]):
        self.__scale_y = scale

    @property
    def scales_z(self) -> List[float]:
        """List of z scales. (`List[float]`)"""
        return self.__scale_z

    @scales_z.setter
    def scales_z(self, scale: list):
        self.__scale_z = scale

    @property
    def offsets_x(self) -> List[float]:
        """List of x offsets."""
        return self.__offset_x

    @offsets_x.setter
    def offsets_x(self, offset: List[float]):
        self.__offset_x = offset

    @property
    def offsets_y(self) -> List[float]:
        """List of y offsets. (`List[float]`)"""
        return self.__offset_y

    @offsets_y.setter
    def offsets_y(self, offset: List[float]):
        self.__offset_y = offset

    @property
    def offsets_z(self) -> List[float]:
        """List of z offsets. (`List[float]`)"""
        return self.__offset_z

    @offsets_z.setter
    def offsets_z(self, offset: List[float]):
        self.__offset_z = offset

    @property
    def sensor_data_offset(self) -> int:
        """Index of points mapping between raw and processed paths. (`int`)"""
        return self.__sensor_data_offset

    @property
    def sensor_data_id(self) -> uuid.UUID:
        """Reference id sensor data. (`UUID`)"""
        return self.__sensor_data_id

    @property
    def sensor_data_mapping(self) -> List[int]:
        """Explicit mapping between indices of Path and SensorData, used when input rate is very high and
        provides unwanted points. (`List[int]`)"""
        return self._sensor_data_mapping

    @property
    def style(self) -> Style:
        """Style that is applied to the path of the stroke. (`Style`)"""
        return self.__style

    @style.setter
    def style(self, style: Style):
        self.__style = style

    @property
    def spline_min_x(self) -> float:
        """Minimum value of x spline. (`float`)"""
        return np.min(self.__spline_x)

    @property
    def spline_min_y(self) -> float:
        """Minimum value of y spline. (`float`)"""
        return np.min(self.__spline_y)

    @property
    def spline_max_x(self) -> float:
        """Maximum value of x spline. (`float`)"""
        return np.max(self.__spline_x)

    @property
    def spline_max_y(self) -> float:
        """Maximum value of y spline. (`float`)"""
        return np.max(self.__spline_y)

    @property
    def points_count(self) -> int:
        """Number of points of sample points. (`int`)"""
        return len(self.__spline_x)

    @property
    def bounding_box(self) -> BoundingBox:
        """Bounding box for path stroke. (`BoundingBox`)"""
        x_min = self.spline_min_x
        x_max = self.spline_max_x
        y_min = self.spline_min_y
        y_max = self.spline_max_y
        return BoundingBox(x=x_min, y=y_min, width=x_max - x_min, height=y_max - y_min)

    def __import__(self, spline: Spline):
        # The content from spline is imported with the appropriate Layout mask being set.
        self.__start_parameter = spline.ts
        self.__end_parameter = spline.tf
        idx: int = 0
        while idx < len(spline.data):
            if spline.layout_mask & LayoutMask.X.value:
                self.__spline_x.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.Y.value:
                self.__spline_y.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.Z.value:
                self.__spline_z.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.SIZE.value:
                self.__size.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.ROTATION.value:
                self.__rotation.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.RED.value:
                self.__red.append(int(spline.data[idx] * 255))
                idx += 1
            if spline.layout_mask & LayoutMask.GREEN.value:
                self.__green.append(int(spline.data[idx] * 255))
                idx += 1
            if spline.layout_mask & LayoutMask.BLUE.value:
                self.__blue.append(int(spline.data[idx] * 255))
                idx += 1
            if spline.layout_mask & LayoutMask.ALPHA.value:
                self.__alpha.append(int(spline.data[idx] * 255))
                idx += 1
            if spline.layout_mask & LayoutMask.SCALE_X.value:
                self.__scale_x.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.SCALE_Y.value:
                self.__scale_y.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.SCALE_Z.value:
                self.__scale_z.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.OFFSET_X.value:
                self.__offset_x.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.OFFSET_Y.value:
                self.__offset_y.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.OFFSET_Z.value:
                self.__offset_z.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.TANGENT_X.value:
                self.__tangent_x.append(spline.data[idx])
                idx += 1
            if spline.layout_mask & LayoutMask.TANGENT_Y.value:
                self.__tangent_y.append(spline.data[idx])
                idx += 1

    def __repr__(self):
        return f'<Stroke : [id:={self.id_h_form}], [num points:={self.points_count}, layout mask:={self.layout_mask}]>'

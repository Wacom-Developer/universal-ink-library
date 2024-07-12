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
import ctypes
import logging
import uuid
from abc import ABC
from enum import Enum
from logging import Logger
from math import isclose
from typing import Tuple, List, Optional, Dict, Any, Union

import numpy as np

from uim.codec.context.scheme import PrecisionScheme
from uim.model.base import UUIDIdentifier, HashIdentifier
from uim.model.helpers.policy import HandleMissingDataPolicy
from uim.model.inkdata.brush import BlendModeURIs
from uim.model.inkinput.inputdata import InkSensorType
from uim.model.semantics.node import URIBuilder
from uim.model.semantics.structures import BoundingBox

logger: Logger = logging.getLogger(__name__)
TOLERANCE_VALUE_COMPARISON: float = 1e-2
HIGH_TOLERANCE_VALUE_COMPARISON: float = 1e-1


class LayoutMask(Enum):
    """
    LayoutMask
    ==========
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
                 rotation: float = 0., scale_x: float = 0., scale_y: float = 0., scale_z: float = 0.,
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

    def __tokenize__(self) -> List[float]:
        return [self.size, self.red, self.green, self.blue, self.alpha, self.rotation, self.scale_x, self.scale_y,
                self.scale_z, self.offset_x, self.offset_y, self.offset_z]

    def __dict__(self):
        return {
            "size": self.size,
            "red": self.red,
            "green": self.green,
            "blue": self.blue,
            "alpha": self.alpha,
            "rotation": self.rotation,
            "scale_x": self.scale_x,
            "scale_y": self.scale_y,
            "scale_z": self.scale_z,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "offset_z": self.offset_z
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, PathPointProperties):
            logger.warning(f"Cannot compare PathPointProperties with {type(other)}")
            return False
        if not isclose(self.size, other.size, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Size mismatch: {self.size} != {other.size}")
            return False
        if not isclose(self.red, other.red, abs_tol=HIGH_TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Red mismatch: {self.red} != {other.red}")
            return False
        if not isclose(self.green, other.green, abs_tol=HIGH_TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Green mismatch: {self.green} != {other.green}")
            return False
        if not isclose(self.blue, other.blue, abs_tol=HIGH_TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Blue mismatch: {self.blue} != {other.blue}")
            return False
        if not isclose(self.alpha, other.alpha, abs_tol=HIGH_TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Alpha mismatch: {self.alpha} != {other.alpha}")
            return False
        if not isclose(self.rotation, other.rotation, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Rotation mismatch: {self.rotation} != {other.rotation}")
            return False
        if not isclose(self.scale_x, other.scale_x, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Scale x mismatch: {self.scale_x} != {other.scale_x}")
            return False
        if not isclose(self.scale_y, other.scale_y, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Scale y mismatch: {self.scale_y} != {other.scale_y}")
            return False
        if not isclose(self.scale_z, other.scale_z, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Scale z mismatch: {self.scale_z} != {other.scale_z}")
            return False
        if not isclose(self.offset_x, other.offset_x, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Offset x mismatch: {self.offset_x} != {other.offset_x}")
            return False
        if not isclose(self.offset_y, other.offset_y, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Offset y mismatch: {self.offset_y} != {other.offset_y}")
            return False
        if not isclose(self.offset_z, other.offset_z, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Offset z mismatch: {self.offset_z} != {other.offset_z}")
            return False
        return True

    def __repr__(self):
        return (f'<PathPointProperties: [size:={self.size}, red:={self.red}, green:={self.green}, blue:={self.blue}, '
                f'alpha:={self.alpha}, rotation:={self.rotation}, scale x:={self.scale_x}, scale y:={self.scale_y}, '
                f'scale z:={self.scale_z}, offset x:={self.offset_x}, offset y:={self.offset_y}, '
                f'offset z:={self.offset_z}]>')


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
        """Static values of properties which do not exist per path point. (`PathPointProperties`, read-only)"""
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

    def __dict__(self):
        return {
            "path_point_properties": self.path_point_properties.__json__(),
            "brush_uri": self.__brush_uri,
            "particles_random_seed": self.__particles_random_seed,
            "render_mode_uri": self.__render_mode_URI
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, Style):
            logger.warning(f"Cannot compare Style with {type(other)}")
            return False
        if not isclose(self.particles_random_seed, other.particles_random_seed):
            logger.warning(f"Particles random seed mismatch: {self.particles_random_seed} != "
                           f"{other.particles_random_seed}")
            return False
        if self.brush_uri != other.brush_uri:
            logger.warning(f"Brush URI mismatch: {self.brush_uri} != {other.brush_uri}")
            return False
        if self.render_mode_uri != other.render_mode_uri:
            logger.warning(f"Render mode URI mismatch: {self.render_mode_uri} != {other.render_mode_uri}")
            return False
        if self.path_point_properties != other.path_point_properties:
            logger.warning(f"Path point properties mismatch: {self.path_point_properties} != "
                           f"{other.path_point_properties}")
            return False
        return True

    def __repr__(self):
        return (f'<Style : [id:={self.__brush_uri}, particles_random_seed:={self.__particles_random_seed}, '
                f'render mode:={self.__render_mode_URI}>')


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

    def __init__(self, layout_mask: int, data: List[Union[float, int]], ts: float = 0., tf: float = 1.):
        self.__layout_mask: int = layout_mask
        self.__data: List[Union[float, int]] = data
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


class InkStrokeAttributeType(Enum):
    """
    InkStrokeAttributeType
    ======================
    This class supports combined all possible spline and sensor data.
    It is used by as_strided_array_extended() and stroke_resampling.
    """
    SPLINE_X = 1
    SPLINE_Y = 2
    SPLINE_SIZES = 3
    SPLINE_ALPHA = 4
    SPLINE_RED = 5
    SPLINE_GREEN = 6
    SPLINE_BLUE = 7
    SPLINE_OFFSETS_X = 8
    SPLINE_OFFSETS_Y = 9
    SPLINE_SCALES_X = 10
    SPLINE_SCALES_Y = 11
    SPLINE_ROTATIONS = 12

    SENSOR_TIMESTAMP = 101  # Time (of the sample point)
    SENSOR_PRESSURE = 102  # Input pressure.
    SENSOR_RADIUS_X = 103  # Touch radius by X
    SENSOR_RADIUS_Y = 104  # Touch radius by Y
    SENSOR_AZIMUTH = 105  # Azimuth angle of the pen (yaw)
    SENSOR_ALTITUDE = 106  # Elevation angle of the pen (pitch)
    SENSOR_ROTATION = 107  # Rotation (counter-clockwise rotation about pen axis)

    def is_spline_attribute(self) -> bool:
        """
        Check if the attribute is a spline attribute.
        Returns
        -------
        bool
            True if the attribute is a spline attribute, False otherwise.
        """
        return 0 < self.value < 100

    def is_sensor_attribute(self) -> bool:
        """
        Check if the attribute is a sensor attribute.
        Returns
        -------
        bool
            True if the attribute is a sensor attribute, False otherwise.
        """
        return 100 < self.value < 200

    @staticmethod
    def get_sensor_type_by_attribute(attribute_type: 'InkStrokeAttributeType') -> Optional[InkSensorType]:
        """
        Get the sensor type by attribute type.
        Parameters
        ----------
        attribute_type: InkStrokeAttributeType
            The attribute type.

        Returns
        -------
        Optional[InkSensorType]
            The sensor type.
        """
        if attribute_type == InkStrokeAttributeType.SPLINE_X:
            return InkSensorType.X
        if attribute_type == InkStrokeAttributeType.SPLINE_Y:
            return InkSensorType.Y
        if attribute_type == InkStrokeAttributeType.SENSOR_TIMESTAMP:
            return InkSensorType.TIMESTAMP
        if attribute_type == InkStrokeAttributeType.SENSOR_PRESSURE:
            return InkSensorType.PRESSURE
        if attribute_type == InkStrokeAttributeType.SENSOR_RADIUS_X:
            return InkSensorType.RADIUS_X
        if attribute_type == InkStrokeAttributeType.SENSOR_RADIUS_Y:
            return InkSensorType.RADIUS_Y
        if attribute_type == InkStrokeAttributeType.SENSOR_AZIMUTH:
            return InkSensorType.AZIMUTH
        if attribute_type == InkStrokeAttributeType.SENSOR_ALTITUDE:
            return InkSensorType.ALTITUDE
        if attribute_type == InkStrokeAttributeType.SENSOR_ROTATION:
            return InkSensorType.ROTATION
        logger.warning(f"{attribute_type} is not a valid InkSensorType. Returning None")
        return None

    @staticmethod
    def get_attribute_type_by_sensor(sensor_type: InkSensorType):
        """
        Get the attribute type by sensor type.
        Parameters
        ----------
        sensor_type: InkSensorType
            The sensor type.

        Returns
        -------
        Optional[InkStrokeAttributeType]
            The attribute type.
        """
        if sensor_type == InkSensorType.X:
            return InkStrokeAttributeType.SPLINE_X
        if sensor_type == InkSensorType.Y:
            return InkStrokeAttributeType.SPLINE_Y
        if sensor_type == InkSensorType.TIMESTAMP:
            return InkStrokeAttributeType.SENSOR_TIMESTAMP
        if sensor_type == InkSensorType.PRESSURE:
            return InkStrokeAttributeType.SENSOR_PRESSURE
        if sensor_type == InkSensorType.RADIUS_X:
            return InkStrokeAttributeType.SENSOR_RADIUS_X
        if sensor_type == InkSensorType.RADIUS_Y:
            return InkStrokeAttributeType.SENSOR_RADIUS_Y
        if sensor_type == InkSensorType.AZIMUTH:
            return InkStrokeAttributeType.SENSOR_AZIMUTH
        if sensor_type == InkSensorType.ALTITUDE:
            return InkStrokeAttributeType.SENSOR_ALTITUDE
        if sensor_type == InkSensorType.ROTATION:
            return InkStrokeAttributeType.SENSOR_ROTATION
        logger.warning(f"{sensor_type} is not a valid InkSensorType. Returning None")
        return None

    def resolve_path_point_property(self, path_point_properties: PathPointProperties) -> Any:
        """
        Resolve the path point property.
        Parameters
        ----------
        path_point_properties: PathPointProperties
            The path point properties.

        Returns
        -------
        Any
            The resolved property.
        """
        if self == InkStrokeAttributeType.SPLINE_SIZES:
            return path_point_properties.size
        if self == InkStrokeAttributeType.SPLINE_ALPHA:
            return path_point_properties.alpha
        if self == InkStrokeAttributeType.SPLINE_RED:
            return path_point_properties.red
        if self == InkStrokeAttributeType.SPLINE_GREEN:
            return path_point_properties.green
        if self == InkStrokeAttributeType.SPLINE_BLUE:
            return path_point_properties.blue
        if self == InkStrokeAttributeType.SPLINE_OFFSETS_X:
            return path_point_properties.offset_x
        if self == InkStrokeAttributeType.SPLINE_OFFSETS_Y:
            return path_point_properties.offset_y
        if self == InkStrokeAttributeType.SPLINE_SCALES_X:
            return path_point_properties.scale_x
        if self == InkStrokeAttributeType.SPLINE_SCALES_Y:
            return path_point_properties.scale_y
        if self == InkStrokeAttributeType.SPLINE_ROTATIONS:
            return path_point_properties.rotation
        return None


DEFAULT_EXTENDED_LAYOUT: List[InkStrokeAttributeType] = [
    InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y, InkStrokeAttributeType.SENSOR_TIMESTAMP,
    InkStrokeAttributeType.SENSOR_PRESSURE
]
"""
Default extended layout for strokes.
"""


class Stroke(UUIDIdentifier):
    """
    Stroke Geometry
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
        self.__sensor_data_mapping: list = sensor_data_mapping or []
        self.__style: Style = style
        self.__random_seed: int = random_seed
        self.__properties_index: int = property_index
        self.__timestamp_cache: Optional[List[float]] = None
        self.__pressure_cache: Optional[List[float]] = None
        self.__precision_scheme: Optional[PrecisionScheme] = None
        if spline is not None:
            self.__import__(spline)

    @property
    def uri(self) -> str:
        """
        The URI of the stroke. (`str`)
        """
        return URIBuilder().build_stroke_uri(self.id)

    def set_timestamp_values(self, timestamp_values: List[float]):
        """
        Set the timestamp values.

        Parameters
        ----------
        timestamp_values: list
            List of timestamp values
        """
        self.__timestamp_cache = timestamp_values

    def get_timestamp_values(self) -> Optional[List[float]]:
        """
        Get the timestamp values.

        Returns
        -------
        Optional[List[float]]
            List of timestamp values
        """
        return self.__timestamp_cache

    def set_pressure_values(self, pressure_values: List[float]):
        """
        Set the pressure values.

        Parameters
        ----------
        pressure_values: List[float]
            List of pressure values
        """
        self.__pressure_cache = pressure_values

    def get_pressure_values(self) -> Optional[List[float]]:
        """
        Get the pressure values.

        Returns
        -------
        List[float]
            List of pressure values
        """
        return self.__pressure_cache

    @property
    def random_seed(self) -> int:
        """Random seed used for randomly generated attributes of a stroke. (`int`)"""
        return self.__random_seed

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
    def tangent_x(self) -> List[float]:
        """
        List of tangent x values. (`List[float]`)
        """
        return self.__tangent_x

    @tangent_x.setter
    def tangent_x(self, tangent_x: List[float]):
        self.__tangent_x = tangent_x

    @property
    def tangent_y(self) -> List[float]:
        """
        List of tangent y values. (`List[float]`)
        """
        return self.__tangent_y

    @tangent_y.setter
    def tangent_y(self, tangent_y: List[float]):
        self.__tangent_y = tangent_y

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
        return self.__sensor_data_mapping

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

    def get_spline_attribute_values(self, attribute_type: InkStrokeAttributeType) -> List[float]:
        """
        Get the spline attribute values.

        Parameters
        ----------
        attribute_type: InkStrokeAttributeType
            The attribute type.

        Returns
        -------
        List[float]
            List of values.
        """
        if attribute_type == InkStrokeAttributeType.SPLINE_X:
            return self.splines_x
        if attribute_type == InkStrokeAttributeType.SPLINE_Y:
            return self.splines_y
        if attribute_type == InkStrokeAttributeType.SPLINE_SIZES:
            return self.sizes
        if attribute_type == InkStrokeAttributeType.SPLINE_ALPHA:
            return self.alpha
        if attribute_type == InkStrokeAttributeType.SPLINE_RED:
            return self.red
        if attribute_type == InkStrokeAttributeType.SPLINE_BLUE:
            return self.blue
        if attribute_type == InkStrokeAttributeType.SPLINE_GREEN:
            return self.green
        if attribute_type == InkStrokeAttributeType.SPLINE_OFFSETS_X:
            return self.offsets_x
        if attribute_type == InkStrokeAttributeType.SPLINE_OFFSETS_Y:
            return self.offsets_y
        if attribute_type == InkStrokeAttributeType.SPLINE_ROTATIONS:
            return self.rotations
        if attribute_type == InkStrokeAttributeType.SPLINE_SCALES_X:
            return self.scales_x
        if attribute_type == InkStrokeAttributeType.SPLINE_SCALES_Y:
            return self.scales_y
        return []

    def get_sensor_point(self, index: int, sensor_channel_values: List[float] = None) -> float:
        """
        Get the sensor point.

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
        """
        if index >= len(self.splines_x) or index < 0:
            raise ValueError(f"Index {index} out of range - [0, ${len(self.splines_x) - 1}]")

        if self.sensor_data_offset == 0 and index > 0:
            index -= 1

        if len(self.sensor_data_mapping) > 0:
            if index >= len(self.sensor_data_mapping):
                sensor_point_index = self.sensor_data_mapping[-1]
            else:
                sensor_point_index = self.sensor_data_mapping[index]
        else:
            sensor_point_index = self.sensor_data_offset + index

            if sensor_channel_values is not None and sensor_point_index >= len(sensor_channel_values):
                sensor_point_index = len(sensor_channel_values) - 1
        return sensor_channel_values[sensor_point_index]

    @staticmethod
    def __handle_missing_data__(spline_len: int, handle_missing_data_policy: HandleMissingDataPolicy) -> Any:
        """
        Handle missing data.

        Parameters
        ----------
        spline_len: int
            The spline length.
        handle_missing_data_policy: HandleMissingDataPolicy
            The policy to handle missing data.

        Returns
        -------
        Any
            The output handler.

        Raises
        ------
        ValueError
            If the handle_missing_data_policy is unknown.
        """
        if handle_missing_data_policy == HandleMissingDataPolicy.FILL_WITH_ZEROS:
            return [0] * spline_len
        if handle_missing_data_policy == HandleMissingDataPolicy.FILL_WITH_NAN:
            nan = float("nan")
            return [nan] * spline_len
        if handle_missing_data_policy == HandleMissingDataPolicy.SKIP_STROKE:
            return None
        if handle_missing_data_policy == HandleMissingDataPolicy.THROW_EXCEPTION:
            raise ValueError("There is no timestamp data for this stroke.")
        raise ValueError(f"Unknown handle_missing_data_policy {handle_missing_data_policy}")

    def as_strided_array_extended(self, ink_model: 'InkModel',
                                  layout: Optional[List[InkStrokeAttributeType]] = None,
                                  handle_missing_data: HandleMissingDataPolicy =
                                  HandleMissingDataPolicy.FILL_WITH_ZEROS,
                                  remove_duplicates_at_ends: bool = True) \
            -> Optional[List[float]]:
        """
        Create a strided array of the stroke data with the given layout.
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
        """
        if layout is None:
            layout = DEFAULT_EXTENDED_LAYOUT
        attribute_type_values_map: Dict = {}
        target_channel_len: int = len(self.splines_x)

        start_index: int = 0
        end_index = target_channel_len

        if remove_duplicates_at_ends:
            if self.splines_x[0] == self.splines_x[1] and self.splines_y[0] == self.splines_y[1]:
                start_index = 1

            if self.splines_x[-1] == self.splines_x[-2] and self.splines_y[-1] == self.splines_y[-2]:
                end_index -= 1

        for attribute_type in layout:
            if attribute_type.is_spline_attribute():
                attribute_values = self.get_spline_attribute_values(attribute_type)
                if len(attribute_values) == 0:
                    # Check if there is information for this attribute in the path_point_properties
                    attr = attribute_type.resolve_path_point_property(self.style.path_point_properties)
                    if attr is not None and attr != 0:
                        attribute_values = [attr] * target_channel_len
                    else:
                        attribute_values = Stroke.__handle_missing_data__(target_channel_len, handle_missing_data)

                attribute_type_values_map[attribute_type] = attribute_values
                continue

            if attribute_type.is_sensor_attribute():
                attribute_values = None
                if self.sensor_data_id is not None:
                    channel_data = ink_model.get_channel_data_values(
                        self, InkStrokeAttributeType.get_sensor_type_by_attribute(attribute_type))

                    if channel_data is not None and len(channel_data) > 0:
                        # This will also use offset and mapping to properly align the data
                        attribute_values = [self.get_sensor_point(i, channel_data) for i in
                                            range(0, target_channel_len)]

                if attribute_values is None:
                    output_handler = Stroke.__handle_missing_data__(target_channel_len, handle_missing_data)
                    if output_handler is None:
                        return None
                    attribute_values = output_handler

                attribute_type_values_map[attribute_type] = attribute_values

            else:
                raise ValueError(f"Don't know how to process attribute type {attribute_type}")

            if len(attribute_values) > 0 and len(attribute_values) != target_channel_len:
                raise ValueError(f"Mismatch in channel size for {attribute_type}.")

            attribute_type_values_map[attribute_type] = attribute_values

        result_strided_array = []
        for i in range(start_index, end_index):
            for attribute_type in layout:
                result_strided_array.append(attribute_type_values_map[attribute_type][i])

        return result_strided_array

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

    def __dict__(self):
        return {
            "id": str(self.id),
            "sensor_data_id": str(self.sensor_data_id),
            "sensor_data_offset": self.sensor_data_offset,
            "sensor_data_mapping": self.sensor_data_mapping,
            "style": self.style.__dict__(),
            "random_seed": self.random_seed,
            "start_parameter": self.start_parameter,
            "end_parameter": self.end_parameter,
            "splines_x": self.splines_x,
            "splines_y": self.splines_y,
            "splines_z": self.splines_z,
            "sizes": self.sizes,
            "rotations": self.rotations,
            "red": self.red,
            "green": self.green,
            "blue": self.blue,
            "alpha": self.alpha,
            "scales_x": self.scales_x,
            "scales_y": self.scales_y,
            "scales_z": self.scales_z,
            "offsets_x": self.offsets_x,
            "offsets_y": self.offsets_y,
            "offsets_z": self.offsets_z,
            "tangent_x": self.tangent_x,
            "tangent_y": self.tangent_y
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, Stroke):
            logger.warning(f"Cannot compare Stroke with {type(other)}")
            return False
        if self.id != other.id:
            logger.warning(f"Stroke id mismatch: {self.id} != {other.id}")
            return False
        if self.sensor_data_id != other.sensor_data_id:
            logger.warning(f"Stroke sensor data id mismatch: {self.sensor_data_id} != {other.sensor_data_id}")
            return False
        if self.start_parameter != other.start_parameter:
            logger.warning(f"Stroke start parameter mismatch: {self.start_parameter} != {other.start_parameter}")
            return False
        if self.end_parameter != other.end_parameter:
            logger.warning(f"Stroke end parameter mismatch: {self.end_parameter} != {other.end_parameter}")
            return False
        if len(self.splines_x) != len(other.splines_x) or len(self.splines_x) != len(other.splines_x) or\
            len(self.splines_z) != len(other.splines_z) or len(self.scales_x) != len(other.scales_x) or\
            len(self.scales_y) != len(other.scales_y) or len(self.scales_z) != len(other.scales_z) or\
            len(self.offsets_x) != len(other.offsets_x) or len(self.offsets_y) != len(other.offsets_y) or\
            len(self.offsets_z) != len(other.offsets_z) or len(self.tangent_x) != len(other.tangent_x) or\
            len(self.tangent_y) != len(other.tangent_y) or len(self.sizes) != len(other.sizes):
            logger.warning("Missmatch of length of internal arrays.")
            return False
        # Due to floating point precision, we need to use isclose
        for v1, v2 in zip(self.splines_x, other.splines_x):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke spline x mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.splines_y, other.splines_y):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke spline y mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.splines_z, other.splines_z):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke spline z mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.sizes, other.sizes):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke size mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.rotations, other.rotations):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke rotation mismatch: {v1} != {v2}")
                return False
        if self.red != other.red:
            logger.warning(f"Stroke red mismatch: {self.red} != {other.red}")
            return False
        if self.green != other.green:
            logger.warning(f"Stroke green mismatch: {self.green} != {other.green}")
            return False
        if self.blue != other.blue:
            logger.warning(f"Stroke blue mismatch: {self.blue} != {other.blue}")
            return False
        if self.alpha != other.alpha:
            logger.warning(f"Stroke alpha mismatch: {self.alpha} != {other.alpha}")
            return False
        for v1, v2 in zip(self.scales_x, other.scales_x):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke scale x mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.scales_y, other.scales_y):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke scale y mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.scales_z, other.scales_z):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke scale z mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.offsets_x, other.offsets_x):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke offset x mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.offsets_y, other.offsets_y):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke offset y mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.offsets_z, other.offsets_z):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke offset z mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.tangent_x, other.tangent_x):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke tangent x mismatch: {v1} != {v2}")
                return False
        for v1, v2 in zip(self.tangent_y, other.tangent_y):
            if not isclose(v1, v2, abs_tol=TOLERANCE_VALUE_COMPARISON):
                logger.warning(f"Stroke tangent y mismatch: {v1} != {v2}")
                return False
        if self.sensor_data_offset != other.sensor_data_offset:
            logger.warning(f"Stroke sensor data offset mismatch: {self.sensor_data_offset} != {other.sensor_data_offset}")
            return False
        if self.sensor_data_mapping != other.sensor_data_mapping:
            logger.warning(f"Stroke sensor data mapping mismatch: {self.sensor_data_mapping} != "
                           f"{other.sensor_data_mapping}")
            return False
        if self.style != other.style:
            logger.warning(f"Stroke style mismatch: {self.style} != {other.style}")
            return False
        if self.random_seed != other.random_seed:
            logger.warning(f"Stroke random seed mismatch: {self.random_seed} != {other.random_seed}")
            return False
        return True

    def __repr__(self):
        return f'<Stroke : [id:={self.id_h_form}], [num points:={self.points_count}, layout mask:={self.layout_mask}]>'

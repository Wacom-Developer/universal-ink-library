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
from abc import ABC
from enum import Enum
from math import isclose
from typing import List, Tuple, Any, Optional, Union

import uim.codec.format.UIM_3_0_0_pb2 as uim
from uim.model.base import InkModelException

logger: logging.Logger = logging.getLogger(__name__)
TOLERANCE_VALUE_COMPARISON: float = 1e-2


class RotationMode(Enum):
    """
    RotationMode
    ============
    Brush rotation modes.
    """
    NONE = 0
    """Indicates that the shape will not be rotated."""
    RANDOM = 1
    """Indicates that the shape will be rotated randomly before it renders."""
    TRAJECTORY = 2
    """Indicates that the shape will be rotated to match the path trajectory."""


class BlendMode(Enum):
    """
    BlendMode
    =========
    The blend mode enum lists the different blend modes which can be applied to raster brushes.
    """

    SOURCE_OVER = uim.SOURCE_OVER
    """This is the default setting and draws new shapes on top of the existing canvas content. Also known as NORMAL."""
    DESTINATION_OVER = uim.DESTINATION_OVER
    """New shapes are drawn behind the existing canvas content. Also known as NORMAL_REVERSE."""
    DESTINATION_OUT = uim.DESTINATION_OUT
    """The existing content is kept where it doesn't overlap the new shape. Also known as ERASE."""
    LIGHTER = uim.LIGHTER
    """Where both shapes overlap the color is determined by adding color values. Also known as ADD."""
    COPY = uim.COPY
    """Only the new shape is shown. Also known as NONE."""
    MIN = uim.MIN
    """The result is the minimum of both color. The result is a darker color."""
    MAX = uim.MAX
    """The result is the maximum of both color. The result is a lighter color."""


class BlendModeURIs(ABC):
    """
    BlendModeURIs
    =============
    URIs for the different blend modes.
    """
    SOURCE_OVER: str = "will://rasterization/3.0/blend-mode/SourceOver"
    """URI for BlendMode.SourceOver"""
    DESTINATION_OVER: str = "will://rasterization/3.0/blend-mode/DestinationOver"
    """URI for BlendMode.DestinationOver"""
    DESTINATION_OUT: str = "will://rasterization/3.0/blend-mode/DestinationOut"
    """URI for BlendMode.DestinationOut"""
    LIGHTER: str = "will://rasterization/3.0/blend-mode/Lighter"
    """URI for BlendMode.Lighter"""
    COPY: str = "will://rasterization/3.0/blend-mode/Copy"
    """URI for BlendMode.Copy"""
    MIN: str = "will://rasterization/3.0/blend-mode/Min"
    """URI for BlendMode.Min"""
    MAX: str = "will://rasterization/3.0/blend-mode/Max"
    """URI for BlendMode.Max"""


class BrushPolygonUri(ABC):
    """
    BrushPolygonUri
    ===============
    Represents a vector brush shape that is specified with a URI.

    Parameters
    ----------
    uri: ´str´
        URI string that identifies the shape.
    min_scale: ´float´
        Minimum scale of the brush sample, after which this shape is applied.
    """

    def __init__(self, uri: str, min_scale: float):
        self.__uri: str = uri
        self.__min_scale: float = min_scale

    @property
    def shape_uri(self) -> str:
        """
        URI string that identifies the shape. (´str´)
        """
        return self.__uri

    @property
    def min_scale(self) -> float:
        """
        Minimum scale of the brush sample, after which this shape is applied. (´float´)

        Notes
        -----
        This value is used by the brush applier in order to pick the proper shape according to the actual brush scale.
        """
        return self.__min_scale

    def __dict__(self):
        return {
            "uri": self.shape_uri,
            "min_scale": self.min_scale
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, BrushPolygonUri):
            logger.warning(f'Cannot compare BrushPolygonUri with {type(other)}')
            return False
        return self.shape_uri == other.shape_uri and isclose(self.min_scale, other.min_scale,
                                                             abs_tol=TOLERANCE_VALUE_COMPARISON)

    def __repr__(self):
        return f'<VectorBrushPrototypeUri : [uri:={self.__uri}, min scale:={self.min_scale}]>'


class BrushPolygon(ABC):
    """
    BrushPolygon
    ============
    Describes vector brush prototype.

    Parameters
    ----------
    points: Optional[List[Tuple[float, float]]] (optional) [default: None]
        List of points for polygon
    indices: Optional[List[int]] (optional) [default: None]
        List of indexes
    """

    def __init__(self, min_scale: float, points: Optional[List[Tuple[float, float]]] = None,
                 indices: Optional[List[int]] = None):
        self.__min_scale: float = min_scale
        self.__points: List[Tuple[float, float]] = points or []
        self.__indices: List[int] = indices or []

    @property
    def points(self) -> List[Tuple[float, float]]:
        """List of coordinates for x value. (`List[Tuple[float, float]]`, read-only)"""
        return self.__points

    @property
    def coord_x(self) -> List[float]:
        """List of coordinates for x value. (`List[float]`, read-only)"""
        if len(self.__points) == 0:
            return []
        if isinstance(self.__points[0], tuple) and len(self.__points[0]) > 0:
            return [p[0] for p in self.points]
        raise InkModelException("The points do not have x value.")

    @property
    def coord_y(self) -> List[float]:
        """List of coordinates for y value. (`List[float]`, read-only)"""
        if len(self.__points) == 0:
            return []
        if isinstance(self.__points[0], tuple) and len(self.__points[0]) > 1:
            return [p[1] for p in self.points]
        raise InkModelException("The points do not have y value.")

    @property
    def coord_z(self) -> List[float]:
        """List of coordinates for z value. (`List[float]`, read-only)"""
        if len(self.__points) == 0:
            return []
        if isinstance(self.__points[0], tuple) and len(self.__points[0]) > 2:
            return [p[2] for p in self.points]
        return []

    @property
    def indices(self) -> List[int]:
        """List of indices of brush prototype [for 3D rendering]. (`List[int]`, read-only)"""
        return self.__indices

    @property
    def min_scale(self) -> float:
        """
        Minimum scale of the brush sample, after which this shape is applied. (`float`, read-only)

        Notes
        -----
        This value is used by the brush applier in order to pick the proper shape according to the actual brush scale.
        """
        return self.__min_scale

    def __dict__(self):
        return {
            "indices": self.indices,
            "min_scale": self.min_scale,
            "coord_x": self.coord_x,
            "coord_y": self.coord_y,
            "coord_z": self.coord_z
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, BrushPolygon):
            logger.warning(f'Cannot compare BrushPolygon with {type(other)}')
            return False
        if self.__min_scale != other.min_scale:
            logger.warning(f'BrushPolygon min scale mismatch: {self.min_scale} != {other.min_scale}')
            return False
        if self.__indices != other.indices:
            logger.warning(f'BrushPolygon indices mismatch: {self.indices} != {other.indices}')
            return False
        for p1, p2 in zip(self.points, other.points):
            if not (isclose(p1[0], p2[0], abs_tol=TOLERANCE_VALUE_COMPARISON) and
                    isclose(p1[1], p2[1], abs_tol=TOLERANCE_VALUE_COMPARISON)):
                logger.warning(f'BrushPolygon point mismatch: {p1} != {p2}')
                return False
        return True

    def __repr__(self):
        return f'<VectorBrushPrototype : [#points:={len(self.__points)}]>'


class Brush(ABC):
    """
    Brush
    -----
    Abstract class for brushes.
    """


class VectorBrush(Brush):
    """
    VectorBrush
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
    """

    def __init__(self, name: str, prototypes: List[Any] = None, spacing: float = 1.):
        self.__name: str = name
        self.__prototypes: List[Any] = prototypes or []
        self.__spacing: float = spacing

    @property
    def name(self) -> str:
        """Name of the vector brush. (`str`, read-only)"""
        return self.__name

    @property
    def prototypes(self) -> List[Union[BrushPolygon, BrushPolygonUri]]:
        """ Polygon prototype for the brush. (`List[Any]`,  read-only).

        Notes
        -----
        The prototype can be either URI-based for prototype with a defined polygon geometry.

        See also
        --------
        - `BrushPolygon` - List of polygon sample points
        - `BrushPolygonUri` - List of URI polygon prototype
        """
        return self.__prototypes

    @property
    def spacing(self) -> float:
        """Spacing value. (`float`, read-only)"""
        return self.__spacing

    def __dict__(self):
        return {
            'name': self.name,
            'prototypes': [p.__dict__() for p in self.prototypes],
            'spacing': self.spacing
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, VectorBrush):
            logger.warning(f'Cannot compare VectorBrush with {type(other)}')
            return False
        return self.name == other.name and self.prototypes == other.prototypes and self.spacing == other.spacing

    def __repr__(self):
        return f'<VectorBrush : [name:={self.__name}]>'


class RasterBrush(Brush):
    """
    RasterBrush
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
    """

    def __init__(self, name: str, spacing: float, scattering: float, rotation: RotationMode,
                 shape_textures: Optional[List[bytes]] = None, shape_texture_uris: Optional[List[str]] = None,
                 fill_texture: Optional[bytes] = None, fill_texture_uri: Optional[str] = None,
                 fill_width: float = 0., fill_height: float = 0.,
                 randomize_fill: bool = False, blend_mode: BlendMode = BlendMode.SOURCE_OVER):
        self.__name: str = name
        self.__spacing: float = spacing
        self.__scattering: float = scattering
        self.__rotation: RotationMode = rotation
        self.__shape_textures: List[bytes] = shape_textures if shape_textures is not None else []
        self.__shape_texture_uri: List[str] = shape_texture_uris if shape_texture_uris is not None else []
        self.__fill_texture: bytes = fill_texture if fill_texture is not None else b''
        self.__fill_texture_uri: str = fill_texture_uri if fill_texture_uri is not None else ''
        self.__fill_width: float = fill_width
        self.__fill_height: float = fill_height
        self.__randomize_fill: bool = randomize_fill
        self.__blend_mode: BlendMode = blend_mode

    @property
    def name(self) -> str:
        """ Name of the raster brush. (`str`, read-only)"""
        return self.__name

    @property
    def spacing(self) -> float:
        """Distance between neighbour particles. (`float`, read-only)"""
        return self.__spacing

    @property
    def scattering(self) -> float:
        """The scattering along the curve normal. (`float`, read-only)"""
        return self.__scattering

    @property
    def rotation(self) -> RotationMode:
        """The particle rotation mode of the brush. (`float`, read-only)"""
        return self.__rotation

    @property
    def shape_textures(self) -> List[bytes]:
        """List of png images that contains the shape texture; byte array with PNG content.
        (`List[bytes]`, read-only)"""
        return self.__shape_textures

    @property
    def shape_texture_uris(self) -> List[str]:
        """URI identifying the fillTexture. (`List[str]`, read-only)"""
        return self.__shape_texture_uri

    @property
    def fill_texture(self) -> bytes:
        """List of png image that contains the fill texture. (`bytes`, read-only)"""
        return self.__fill_texture

    @property
    def fill_texture_uri(self) -> str:
        """The fill texture URI. (`str`, read-only)"""
        return self.__fill_texture_uri

    @property
    def fill_width(self) -> float:
        """Width of the fill tile. (`float`, read-only)"""
        return self.__fill_width

    @property
    def fill_height(self) -> float:
        """Height of the fill tile. (`float`, read-only)"""
        return self.__fill_height

    @property
    def randomize_fill(self) -> bool:
        """Specifies whether the fill texture is randomly displaced. (`bool`, read-only)"""
        return self.__randomize_fill

    @property
    def blend_mode(self) -> BlendMode:
        """The applied blend mode. (`BlendMode`, read-only)"""
        return self.__blend_mode

    def __dict__(self):
        return {
            'name': self.name,
            'spacing': self.spacing,
            'scattering': self.scattering,
            'rotation': self.rotation,
            'shape_texture_uris': self.shape_texture_uris,
            'fill_texture_uri': self.fill_texture_uri,
            'fill_width': self.fill_width,
            'fill_height': self.fill_height,
            'randomize_fill': self.randomize_fill,
            'blend_mode': self.blend_mode
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, RasterBrush):
            logger.warning(f'Cannot compare RasterBrush with {type(other)}')
            return False
        if self.name != other.name:
            logger.warning(f'RasterBrush name mismatch: {self.__name} != {other.name}')
            return False
        if not isclose(self.spacing, other.spacing, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f'RasterBrush spacing mismatch: {self.spacing} != {other.spacing}')
            return False
        if not isclose(self.scattering, other.scattering, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f'RasterBrush scattering mismatch: {self.scattering} != {other.scattering}')
            return False
        if self.rotation != other.rotation:
            logger.warning(f'RasterBrush rotation mismatch: {self.rotation} != {other.rotation}')
            return False
        if self.shape_textures != other.shape_textures:
            logger.warning(f'RasterBrush shape textures mismatch: {self.shape_textures} != {other.shape_textures}')
            return False
        if self.shape_texture_uris != other.shape_texture_uris:
            logger.warning(f'RasterBrush shape texture URIs mismatch: {self.shape_texture_uris} != '
                           f'{other.shape_texture_uris}')
            return False
        if self.fill_texture != other.fill_texture:
            logger.warning(f'RasterBrush fill texture mismatch: {self.fill_texture} != {other.fill_texture}')
            return False
        if self.fill_texture_uri != other.fill_texture_uri:
            logger.warning(f'RasterBrush fill texture URI mismatch: {self.fill_texture_uri} != '
                           f'{other.fill_texture_uri}')
            return False
        if not isclose(self.fill_width, other.fill_width, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f'RasterBrush fill width mismatch: {self.fill_width} != {other.fill_width}')
            return False
        if not isclose(self.fill_height, other.fill_height, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f'RasterBrush fill height mismatch: {self.fill_height} != {other.fill_height}')
            return False
        if self.randomize_fill != other.randomize_fill:
            logger.warning(f'RasterBrush randomize fill mismatch: {self.randomize_fill} != {other.randomize_fill}')
            return False
        if self.blend_mode != other.blend_mode:
            logger.warning(f'RasterBrush blend mode mismatch: {self.blend_mode} != {other.blend_mode}')
            return False
        return True

    def __repr__(self):
        return f'<RasterBrush : [name:={self.name}]>'


class Brushes:
    """
    Brushes
    ========
    Brush descriptions, needed for uim rasterization.

    Parameters
    ----------
    vector_brushes: Optional[List[VectorBrush]] (optional) [default: None]
        List of vector brushes
    raster_brushes: Optional[List[RasterBrush] (optional) [default: None]
        List of raster brushes
    """

    def __init__(self, vector_brushes: Optional[List[VectorBrush]] = None,
                 raster_brushes: Optional[List[RasterBrush]] = None):
        self.__vector_brushes: List[VectorBrush] = vector_brushes or []
        self.__raster_brushes: List[RasterBrush] = raster_brushes or []

    @property
    def vector_brushes(self) -> List[VectorBrush]:
        """
        List of defined vector brushes. (`List[VectorBrush]`)"""
        return self.__vector_brushes

    @property
    def raster_brushes(self) -> List[RasterBrush]:
        """
        List of defined raster brushes. (`List[RasterBrush]`)
        """
        return self.__raster_brushes

    def add_vector_brush(self, brush: VectorBrush):
        """
        Adding a vector brush.

        Parameters
        ----------
        brush: `VectorBrush`
            Vector brush
        """
        self.vector_brushes.append(brush)

    def add_raster_brush(self, brush: RasterBrush):
        """
        Adding raster brush.

        Parameters
        ----------
        brush: `RasterBrush`
            Raster brush
        """
        self.raster_brushes.append(brush)

    def remove_vector_brush(self, name: str):
        """
        Remove vector brush from brushes.
        If the brush with the name does not exist, no operation is performed.

        Parameters
        ----------
        name: `str`
            Name of brush that should be remove.
        """
        for v_i, _ in enumerate(self.__vector_brushes):
            if self.__vector_brushes[v_i].name == name:
                del self.__vector_brushes[v_i]
                break

    def remove_raster_brush(self, name: str):
        """
        Remove raster brush from brushes. If the brush with the name does not exist, no operation is performed.

        Parameter
        ---------
        name: str
            Name of brush that should be remove
        """
        for v_i, _ in enumerate(self.__raster_brushes):
            if self.__raster_brushes[v_i].name == name:
                del self.__raster_brushes[v_i]
                break

    def __dict__(self):
        return {
            'vector_brushes': [b.__dict__() for b in self.vector_brushes],
            'raster_brushes': [b.__dict__() for b in self.raster_brushes]
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, Brushes):
            logger.warning(f'Cannot compare Brushes with {type(other)}')
            return False
        if len(self.vector_brushes) != len(other.vector_brushes):
            logger.warning(f'VectorBrushes length mismatch: {len(self.vector_brushes)} != {len(other.vector_brushes)}')
            return False
        for v1, v2 in zip(self.vector_brushes, other.vector_brushes):
            if v1 != v2:
                logger.warning(f'VectorBrush mismatch: {v1} != {v2}')
                return False
        if len(self.raster_brushes) != len(other.raster_brushes):
            logger.warning(f'RasterBrushes length mismatch: {len(self.raster_brushes)} != {len(other.raster_brushes)}')
            return False
        for r1, r2 in zip(self.raster_brushes, other.raster_brushes):
            if r1 != r2:
                logger.warning(f'RasterBrush mismatch: {r1} != {r2}')
                return False
        return True

    def __repr__(self):
        return f'<Brushes : [raster brush:=#{len(self.__raster_brushes)}, vector brush:=#{len(self.__vector_brushes)}]>'

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
from abc import ABC
from enum import Enum
from typing import List, Tuple, Any

import uim.codec.format.UIM_3_0_0_pb2 as uim


class RotationMode(Enum):
    """Brush rotation modes."""
    NONE = 0
    """Indicates that the shape will not be rotated."""
    RANDOM = 1
    """Indicates that the shape will be rotated randomly before it renders."""
    TRAJECTORY = 2
    """Indicates that the shape will be rotated to match the path trajectory."""


class BlendMode(Enum):
    """The blend mode enum lists the different blend modes which can be applied to raster brushes."""

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


class BrushPolygon(ABC):
    """
    Describes vector brush prototype.

    Parameters
    ----------
    points: list
        List of points for polygon
    indices: list
        List of indexes
    """

    def __init__(self, min_scale: float, points: list = None, indices: list = None):
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
        if len(self.__points[0]) > 0:
            return [p[0] for p in self.points]

    @property
    def coord_y(self) -> List[float]:
        """List of coordinates for y value. (`List[float]`, read-only)"""
        if len(self.__points) == 0:
            return []
        if len(self.__points[0]) > 1:
            return [p[1] for p in self.points]

    @property
    def coord_z(self) -> List[float]:
        """List of coordinates for z value. (`List[float]`, read-only)"""
        if len(self.__points) == 0:
            return []
        if len(self.__points[0]) > 2:
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

    def __repr__(self):
        return '<VectorBrushPrototype : [#points:={}]>'.format(len(self.__points))


class Brush(ABC):
    """Abstract class for brushes."""
    pass


class VectorBrush(Brush):
    """
    VectorBrush
    -----------
    A configuration which allows rendering of an interpolated Catmull-Rom spline as a vector spline by applying a
    specific polygon for each interpolated point, depending on its size and merging result afterwards.

    Parameters
    ----------
    name: str
        Name of the brush
    prototypes: list
        Prototypes for brush
    spacing: float
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
    def prototypes(self) -> List[Any]:
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

    def __repr__(self):
        return '<VectorBrush : [name:={}]>'.format(self.__name)


class RasterBrush(Brush):
    """
    RasterBrush
    -----------
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
    shape_textures: list
        List of png images that contains the shape texture.
    shape_texture_uris: list
        List of URIs that contains the shape texture.
    fill_texture: `bytes`
        List of png image that contains the fill texture.
    fill_texture_uri: `list`
        List of URIs that describes the fill textures.
    fill_width: `float`
        Width of the fill tile.
    fill_height: `float`
        Height of the fill tile.
    randomize_fill: `bool`
        Specifies whether the fill texture is randomly displaced.
    blend_mode: `BlendMode`
        The applied blend mode.
    """

    def __init__(self, name: str, spacing: float, scattering: float, rotation: RotationMode,
                 shape_textures: List[bytes] = None, shape_texture_uris: List[str] = None,
                 fill_texture: bytes = None, fill_texture_uri: str = None,
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
        """ Brush descriptor
        :return : name of brush
        """
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
        """URIs identifying the fillTexture.
        :return : list of URIs
        """
        return self.__fill_texture_uri

    @property
    def fill_width(self) -> float:
        """Width of the fill tile.
        :return : width
        """
        return self.__fill_width

    @property
    def fill_height(self) -> float:
        """Height of the fill tile.
        :return : height
        """
        return self.__fill_height

    @property
    def randomize_fill(self) -> bool:
        """Specifies whether the fill texture is randomly displaced.
        :return : bool - flag
        """
        return self.__randomize_fill

    def __repr__(self):
        return '<RasterBrush : [name:={}]>'.format(self.name)


class Brushes(object):
    """
        Brush descriptions, needed for uim rasterization.
    """

    def __init__(self, vector_brushes: List[VectorBrush] = None, raster_brushes: List[RasterBrush] = None):
        """
        Constructor.
        :param vector_brushes: List of defined vector brushes.
        :param raster_brushes: List of defined raster brushes.
        """
        self.__vector_brushes: List[VectorBrush] = vector_brushes or []
        self.__raster_brushes: List[RasterBrush] = raster_brushes or []

    @property
    def vector_brushes(self) -> List[VectorBrush]:
        """
        List of defined vector brushes.
        :return: list
        """
        return self.__vector_brushes

    @property
    def raster_brushes(self) -> List[RasterBrush]:
        """
        List of defined raster brushes.
        :return: list
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
        for v_i in range(len(self.__vector_brushes)):
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
        for v_i in range(len(self.__raster_brushes)):
            if self.__raster_brushes[v_i].name == name:
                del self.__raster_brushes[v_i]
                break

    def __repr__(self):
        return '<Brushes : [raster brush:=#{}, vector brush:=#{}]>'.format(len(self.__raster_brushes),
                                                                           len(self.__vector_brushes))

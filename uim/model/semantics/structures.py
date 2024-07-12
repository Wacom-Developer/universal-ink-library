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
from abc import ABC
from typing import Any


class BoundingBox(ABC):
    """
    BoundingBox
    ===========
    Bounding boxes are represented as rectangle.
    Each rectangle is composed of a x, y coordinate representing the lower left point and the height and width.

    Parameters
    ----------
    x: float
        x-coordinate
    y: float
        y-coordinate
    width: float
        Width of the bounding box
    height: float
        Height of the bounding box
    """

    def __init__(self, x: float, y: float, width: float, height: float):
        self.__x: float = x
        self.__y: float = y
        self.__width: float = width
        self.__height: float = height

    @property
    def x(self) -> float:
        """X coordinate of the lower left x coordinate of the bounding box. ('float', read-only)"""
        return self.__x

    @property
    def y(self) -> float:
        """y coordinate of the lower left y coordinate of the bounding box. ('float', read-only)"""
        return self.__y

    @property
    def width(self) -> float:
        """Width of the bounding box. ('float', read-only)"""
        return self.__width

    @property
    def height(self) -> float:
        """Height of the bounding box. ('float', read-only)"""
        return self.__height

    def enclosing_bounding_box(self, bb: 'BoundingBox') -> 'BoundingBox':
        """
        Enclosing bounding box.

        Parameters
        ----------
        bb: `BoundingBox`
            Other bounding box

        Returns
        -------
        bb: `BoundingBox`
            Enclosing bounding box
        """
        new_x: float = min(self.x, bb.x)
        new_y: float = min(self.y, bb.y)
        new_width: float = max(self.width, self.width + self.x - bb.x)
        new_height: float = max(self.height, self.height + self.y - bb.y)
        return BoundingBox(new_x, new_y, new_width, new_height)

    def __dict__(self):
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, BoundingBox):
            return False
        return self.x == other.x and self.y == other.y and self.width == other.width and self.height == other.height

    def __repr__(self):
        return f'<Bounding box : [x:={self.x}, y:={self.y}, width:={self.width}, height:={self.height}]>'

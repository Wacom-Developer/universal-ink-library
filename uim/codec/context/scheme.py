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


class PrecisionScheme(object):
    """
    Contains information for the decimal precision of data in different channels.

    Parameters
    ----------
    mask_value: int
        Mask value which encodes the path precision.

    """

    POSITION_SHIFT_BITS: int = 0
    SIZE_SHIFT_BITS: int = 4
    ROTATION_SHIFT_BITS: int = 8
    SCALE_SHIFT_BITS: int = 12
    OFFSET_SHIFT_BITS: int = 16

    def __init__(self, mask_value: int = 0):
        self.__value = mask_value

    @property
    def value(self) -> int:
        """Value that encodes the bits. (`int`)"""
        return self.__value

    @value.setter
    def value(self, value: int):
        self.__value = value

    @property
    def position_precision(self) -> int:
        """Gets or sets the data precision for position (X, Y, Z) channels. (`int`)"""
        return (self.value >> PrecisionScheme.POSITION_SHIFT_BITS) & 0xF

    @property
    def size_precision(self) -> int:
        """Gets or sets the data precision for the Size channel. (`int`, read-only)"""
        return (self.value >> PrecisionScheme.SIZE_SHIFT_BITS) & 0xF

    @property
    def rotation_precision(self) -> int:
        """Gets or sets the data precision for the Rotation channel. (`int`, read-only)"""
        return (self.value >> PrecisionScheme.ROTATION_SHIFT_BITS) & 0xF

    @property
    def scale_precision(self) -> int:
        """Gets or sets the data precision for the Scale (ScaleX, ScaleY, ScaleZ) channels. (`int`, read-only)"""
        return (self.value >> PrecisionScheme.SCALE_SHIFT_BITS) & 0xF

    @property
    def offset_precision(self) -> int:
        """Gets or sets the data precision for the Offset (OffsetX, OffsetY, OffsetZ) channels. (`int`, read-only)"""
        return (self.value >> PrecisionScheme.OFFSET_SHIFT_BITS) & 0xF

    def __repr__(self):
        return f'Precision scheme. [position:={self.position_precision}, size:={self.size_precision}, ' \
               f'rotation:={self.rotation_precision}, scale:={self.scale_precision}, ' \
               f'offset:={self.offset_precision}]'

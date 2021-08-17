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


class Matrix4x4(ABC):
    """
    Collection of helpers for matrices.

    Representation of a 4x4 affine matrix

        | m00  m01  m02  m03 |
        | m10  m11  m12  m13 |
        | m20  m21  m22  m23 |
        | m30  m31  m32  m33 |

    """

    @staticmethod
    def create_scale(scale: float) -> list:
        return [[scale, 0, 0., 0.],
                [0., scale, 0., 0.],
                [0., 0, scale, 0.],
                [0., 0, 0., 1.]]

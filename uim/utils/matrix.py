# -*- coding: utf-8 -*-
# Copyright © 2023-present Wacom Authors. All Rights Reserved.
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
from typing import List


class Matrix4x4(ABC):
    """
    Matrix4x4
    ==========
    Collection of helpers for matrices.

    Representation of a 4x4 affine matrix

        | m00  m01  m02  m03 |
        | m10  m11  m12  m13 |
        | m20  m21  m22  m23 |
        | m30  m31  m32  m33 |

    """

    @staticmethod
    def create_scale(scale: float) -> List[List[float]]:
        """
        Create a scale matrix.
        Parameters
        ----------
        scale: float
            Scale factor

        Returns
        -------
        List[List[float]]
            4x4 scale matrix
        """
        return [[scale, 0, 0., 0.],
                [0., scale, 0., 0.],
                [0., 0, scale, 0.],
                [0., 0, 0., 1.]]

    @staticmethod
    def create_translation(translation: List[float]) -> List[List[float]]:
        """
        Create a translation matrix.
        Parameters
        ----------
        translation: List[float]
            Translation vector

        Returns
        -------
        List[List[float]]
            4x4 translation matrix

        Raises
        ------
        ValueError
            Translation must be a 3D vector
        """
        if len(translation) != 3:
            raise ValueError("Translation must be a 3D vector")
        return [[1., 0., 0., translation[0]],
                [0., 1., 0., translation[1]],
                [0., 0., 1., translation[2]],
                [0., 0., 0., 1.]]

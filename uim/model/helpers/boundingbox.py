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
from typing import List

from uim.model.semantics.structures import BoundingBox


def union(b0: BoundingBox, b1: BoundingBox):
    """
    Union of two bounding boxes.

    Parameters
    ----------
    b0: BoundingBox
        Bounding box 1
    b1: BoundingBox
        Bounding box 1

    Returns
    -------
    union_box: BoundingBox
        Union bounding box
    """
    top: float = min(b0.y, b1.y)
    left: float = min(b0.x, b1.x)
    bottom: float = max(b0.y + b0.height, b1.y + b1.height)
    right: float = max(b0.x + b0.width, b1.x + b1.width)
    return BoundingBox(left, top, right - left, bottom - top)


def union_all(bounds: List[BoundingBox]) -> BoundingBox:
    """
    Create union of all bounding boxes.

    Parameters
    ----------
    bounds: List[BoundingBox]
        List of bounding boxes

    Returns
    -------
    union: BoundingBox
        Union of all bounding boxes.
    """
    result: BoundingBox = bounds[0]
    for i in range(1, len(bounds)):
        result = union(result, bounds[i])
    return result

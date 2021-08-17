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
"""
Spline helpers
==============
Helper functions to interpolate list of coordinates.
"""
from typing import Tuple, List

import numpy as np


def catmull_rom_one_point(x: float, v0: float, v1: float, v2: float, v3: float) -> float:
    """
    Computes interpolated x-coord for given x-coord using Catmull-Rom.
    Computes an interpolated y-coordinate for the given x-coordinate between
    the support points v1 and v2. The neighboring support points v0 and v3 are
    used by Catmull-Rom to ensure a smooth transition between the spline
    segments.

    Parameters
    ----------
    x: ´float´
        The x-coord, for which the y-coord is needed
    v0: ´float´
        1st support point
    v1: ´float´
        2nd support point
    v2: ´float´
        3rd support point
    v3: ´float´
        4th support point

    Returns
    -------
    coord - ´float´
        Point
    """
    c1: float = 1. * v1
    c2: float = -.5 * v0 + .5 * v2
    c3: float = 1. * v0 + -2.5 * v1 + 2. * v2 - .5 * v3
    c4: float = -.5 * v0 + 1.5 * v1 + -1.5 * v2 + .5 * v3
    return ((c4 * x + c3) * x + c2) * x + c1


def catmull_rom(p_x: List[float], p_y: List[float], res: int = 2) -> Tuple[List[float], List[float]]:
    """
    Computes Catmull-Rom Spline for given support points and resolution.

    Parameters
    ----------
    p_x: list
        Array of x-coords
    p_y: list
        Array of y-coords
    res: int
        Resolution of a segment (including the start point, but not the endpoint of the segment)

    Returns
    -------
    interp_x: list
        List of interpolated x values
    interp_y: list
        List of interpolated y values

    References
    ----------
    - [1] Wikipedia article on Catmull-Rom spline
            URL: https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline
    """
    # create arrays for spline points
    x_intpol: np.ndarray = np.empty(res * (len(p_x) - 1) + 1)
    y_intpol: np.ndarray = np.empty(res * (len(p_x) - 1) + 1)

    # set the last x- and y-coord, the others will be set in the loop
    x_intpol[-1] = p_x[-1]
    y_intpol[-1] = p_y[-1]

    # loop over segments (we have n-1 segments for n points)
    for i in range(len(p_x) - 1):
        # set x-coords
        x_intpol[i * res:(i + 1) * res] = np.linspace(
            p_x[i], p_x[i + 1], res, endpoint=False)
        if i == 0:
            # need to estimate an additional support point before the first
            y_intpol[:res] = np.array([
                catmull_rom_one_point(
                    x,
                    p_y[0] - (p_y[1] - p_y[0]),  # estimated start point,
                    p_y[0],
                    p_y[1],
                    p_y[2])
                for x in np.linspace(0., 1., res, endpoint=False)])
        elif i == len(p_x) - 2:
            # need to estimate an additional support point after the last
            y_intpol[i * res:-1] = np.array([
                catmull_rom_one_point(
                    x,
                    p_y[i - 1],
                    p_y[i],
                    p_y[i + 1],
                    p_y[i + 1] + (p_y[i + 1] - p_y[i])  # estimated end point
                ) for x in np.linspace(0., 1., res, endpoint=False)])
        else:
            y_intpol[i * res:(i + 1) * res] = np.array([
                catmull_rom_one_point(
                    x,
                    p_y[i - 1],
                    p_y[i],
                    p_y[i + 1],
                    p_y[i + 2]) for x in np.linspace(0., 1., res, endpoint=False)])
    return x_intpol.tolist(), y_intpol.tolist()


def linear_interpol(p_x: list, p_y: list) -> Tuple[List[float], List[float]]:
    """
    Linear interpolation of the first and the last point in array.

    Parameters
    ----------
    p_x: list -
        array of x-coordinates
    p_y: list -
        array of y-coordinates

    Returns
    --------
    interp_x: list
        List of linear interpolated x coordinates
    interp_y: list
        List of linear interpolated x coordinates
    """
    x_intpol = np.linspace(p_x[0], p_x[-1], 4)
    return x_intpol.tolist(), np.interp(x_intpol, p_x, p_y).tolist()

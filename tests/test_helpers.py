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
import math
import uuid
from typing import List

import numpy as np
import pytest

from uim.model import UUIDIdentifier
from uim.model.base import Identifier
from uim.model.helpers.boundingbox import union, union_all
from uim.model.helpers.spline import catmull_rom_one_point, catmull_rom, linear_interpol
from uim.model.inkdata.strokes import PathPointProperties
from uim.model.inkinput.inputdata import unit2unit, Unit, unit2unit_matrix
from uim.model.semantics.structures import BoundingBox
from uim.utils.matrix import Matrix4x4


def test_matrix_helper():
    """
    Test the matrix helper functions.
    """
    matrix: List[List[float]] = Matrix4x4.create_scale(1.5)
    assert matrix[0] == [1.5, 0, 0., 0.]
    assert matrix[1] == [0., 1.5, 0., 0.]
    assert matrix[2] == [0., 0, 1.5, 0.]
    assert matrix[3] == [0., 0, 0., 1.]
    matrix = Matrix4x4.create_translation([1.0, 2.0, 3.0])
    assert matrix[0] == [1., 0., 0., 1.]
    assert matrix[1] == [0., 1., 0., 2.]
    assert matrix[2] == [0., 0., 1., 3.]
    assert matrix[3] == [0., 0., 0., 1.]
    try:
        Matrix4x4.create_translation([1.0, 2.0, 3.0, 4.0])
        pytest.fail("Translation must be a 3D vector. Exception should have been thrown.")
    except ValueError:
        pass


def test_spline_helper():
    """
    Test the spline helper functions.
    """
    value = catmull_rom_one_point(0.5, 0.0, 1.0, 2.0, 3.0)
    assert value == 1.5


def test_spline_array():
    """
    Test the spline helper functions.
    """
    spline_x, spline_y = catmull_rom([0.0, 1.0, 2.0, 3.0], [0.0, 1.0, 2.0, 3.0], 2)
    assert spline_x == [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    assert spline_y == [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    spline_x, spline_y = catmull_rom([0.0, 1.0, 2.0], [0.0, 1.0, 2.0], 2)
    assert spline_x == [0.0, 0.5, 1.0, 1.5, 2.0]
    assert spline_y == [0.0, 0.5, 1.0, 1.5, 2.0]
    spline_x, spline_y = catmull_rom([0.0], [0.0], 2)
    assert spline_x == [0.0]
    assert spline_y == [0.0]
    try:
        catmull_rom([], [], 2)
        pytest.fail("Empty arrays should throw an exception.")
    except ValueError:
        print("Empty arrays throw an exception.")


def test_linear_interpolation():
    """
    Test the linear interpolation function.
    """
    lin_x, lin_y = linear_interpol([0.0, 1.0, 2.0], [0.0, 1.0, 2.0])
    assert lin_x == pytest.approx([0.0, 0.6666666, 1.3333333, 2.0])
    assert lin_y == pytest.approx([0.0, 0.6666666, 1.3333333, 2.0])
    lin_x, lin_y = linear_interpol([0.0, 1.0], [0.0, 1.0])
    assert lin_x == pytest.approx([0.0, 0.3333333, 0.6666666, 1.0])
    assert lin_y == pytest.approx([0.0, 0.3333333, 0.6666666, 1.0])
    lin_x, lin_y = linear_interpol([0.0, 20., 1.0], [0.0, 20., 1.0])
    assert lin_x == pytest.approx([0.0, 0.3333333, 0.6666666, 1.0])
    assert lin_y == pytest.approx([0.0, 0.3333333, 0.6666666, 1.0])
    try:
        linear_interpol([0.], [0.])
        pytest.fail("Empty arrays should throw an exception.")
    except ValueError:
        print("Empty arrays throw an exception.")


def test_bounding_box():
    """
    Test the bounding box function.
    """
    bb1 = BoundingBox(x=0.0, y=0.0, width=100., height=100.)
    bb2 = BoundingBox(x=10.0, y=10.0, width=100., height=100.)
    bb3 = union(bb1, bb2)
    assert bb3.x == 0.0
    assert bb3.y == 0.0
    assert bb3.width == 110.0
    assert bb3.height == 110.0
    bb4 = union_all([bb1, bb2, bb3])
    assert bb4.x == 0.0
    assert bb4.y == 0.0
    assert bb4.width == 110.0
    assert bb4.height == 110.0
    assert str(bb4) == "<Bounding box : [x:=0.0, y:=0.0, width:=110.0, height:=110.0]>"


def test_unit_conversion():
    """
    Test the unit conversion function.
    """
    assert unit2unit(Unit.M, Unit.CM, 2.0) == 200.0
    assert unit2unit(Unit.CM, Unit.M, 200.0) == 2.0
    assert unit2unit(Unit.MM, Unit.CM, 20.0) == 2.0
    assert unit2unit(Unit.CM, Unit.MM, 2.0) == 20.0
    assert unit2unit(Unit.MM, Unit.M, 200.0) == 0.2
    assert unit2unit(Unit.M, Unit.DIP, 1) == 3779.5296
    with pytest.raises(ValueError):
        unit2unit("Not", Unit.MM, 200.0)
    with pytest.raises(ValueError):
        unit2unit(Unit.MM, "Not", 200.0)
    with pytest.raises(ValueError):
        unit2unit(Unit.MM, Unit.S, 1)
    assert unit2unit(Unit.S, Unit.MS, 1) == 1000
    assert unit2unit(Unit.MS, Unit.S, 1000) == 1
    assert unit2unit(Unit.MS, Unit.MS, 1000) == 1000
    assert unit2unit(Unit.S, Unit.S, 1) == 1


def test_conversion_matrix_unit():
    """
    Test the conversion matrix unit function.
    """
    matrix = unit2unit_matrix(Unit.M, Unit.CM)
    assert matrix[0][0] == 100.0
    assert matrix[1][1] == 100.0
    assert matrix[2][2] == 1.0
    assert (unit2unit_matrix(Unit.UNDEFINED, Unit.MM) == np.identity(3)).all()
    with pytest.raises(ValueError):
        unit2unit_matrix("Not", Unit.M)
    with pytest.raises(ValueError):
        unit2unit_matrix(Unit.M, "Not")


def test_color_conversation():
    """Validate that the UimID can be converted from s-form to byte array."""
    color: int = -1  # white color
    r, g, b, a = PathPointProperties.color(color)
    c2: int = PathPointProperties.rgba(r, g, b, a)
    assert math.isclose(color, c2, rel_tol=0.1, abs_tol=0.0)
    red: float = 0.3
    green: float = 0.3
    blue: float = 0.3
    alpha: float = 1.
    color: int = PathPointProperties.rgba(red, green, blue, alpha)
    r2, g2, b2, a2 = PathPointProperties.color(color)
    assert math.isclose(red, r2, rel_tol=0.1, abs_tol=0.0)
    assert math.isclose(green, g2, rel_tol=0.1, abs_tol=0.0)
    assert math.isclose(blue, b2, rel_tol=0.1, abs_tol=0.0)
    assert math.isclose(alpha, a2, rel_tol=0.1, abs_tol=0.0)


def test_uimid_s_form_conversation():
    """Validate that the UimID can be converted from s-form to byte array."""
    uimid: uuid.UUID = UUIDIdentifier.id_generator()
    uimid_object: UUIDIdentifier = UUIDIdentifier(uimid)
    uimid_conv: uuid.UUID = UUIDIdentifier.str_to_uimid(uimid_object.id_s_form)
    assert uimid == uimid_conv


def test_uimid_h_form_conversation():
    """Validate that the UimID can be converted from s-form to byte array."""
    uimid: uuid.UUID = UUIDIdentifier.id_generator()
    uimid_object: UUIDIdentifier = UUIDIdentifier(uimid)
    assert uimid_object.id_s_form == uimid_object.id_h_form.replace('-', '')
    uimid_conv: uuid.UUID = UUIDIdentifier.str_to_uimid(uimid_object.id_h_form)
    assert uimid == uimid_conv


def test_uuid():
    uuid_str: str = 'd40ca4a8b8987d79895e62020fbc219c'
    uuid_obj: uuid.UUID = UUIDIdentifier.str_to_uimid(uuid_str)
    id_s_form: str = Identifier.uimid_to_s_form(uuid_obj)
    assert uuid_str == id_s_form
    uuid_2_str: str = '6d586b07-87b0-4a29-b9a0-7de8d0219bae'
    uuid_2_obj: uuid.UUID = UUIDIdentifier.str_to_uimid(uuid_2_str)
    id_h_form: str = str(uuid_2_obj)
    assert uuid_2_str == id_h_form

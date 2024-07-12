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
import csv
import json
from json import JSONEncoder
from pathlib import Path
from typing import Union, Any, Optional, List

from uim.model.base import Identifier
from uim.model.helpers.policy import HandleMissingDataPolicy
from uim.model.ink import InkModel, SensorDataRepository
from uim.model.inkdata.brush import Brushes
from uim.model.inkdata.strokes import Style, InkStrokeAttributeType
from uim.model.inkinput.inputdata import InputContextRepository
from uim.model.semantics.node import StrokeFragment


# subclass JSONEncoder
class UniversalInkModelEncoder(JSONEncoder):
    """
    UniversalInkModelEncoder
    ========================
    Universal Ink Model Encoder is a JSONEncoder that can be used to serialize
    """

    def default(self, obj: Any):
        if hasattr(obj, '__json__'):
            return obj.__json__()
        return super().default(obj)


def json_encode(obj: Union[Identifier, InkModel, InputContextRepository, SensorDataRepository, Brushes, Style,
                StrokeFragment], indent: int = 4) -> str:
    """
    Encodes the given object to a JSON string.

    Parameters
    ----------
    obj: `Identifier`
        Object to encode
    indent: int
        Indentation

    Returns
    -------
    str
        JSON string
    """
    return json.dumps(obj, cls=UniversalInkModelEncoder, indent=indent)


def serialize_json(ink_model: InkModel, path: Path):
    """
    Serialize the ink model to a JSON file.

    Parameters
    ----------
    ink_model: InkModel
        Ink model
    path: Path
        Path to save the JSON file
    """
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    with open(path, 'w') as fp:
        json.dump(ink_model, fp, cls=UniversalInkModelEncoder, indent=4)


def serialize_sensor_data_csv(ink_model: InkModel, path: Path, layout: Optional[List[InkStrokeAttributeType]] = None,
                              policy: HandleMissingDataPolicy = HandleMissingDataPolicy.FILL_WITH_ZEROS,
                              delimiter: str = ','):
    """
    Serialize the sensor data to a CSV file.

    Parameters
    ----------
    ink_model: InkModel
        Ink model
    path: Path
        Path to save the CSV file
    layout: List[InkStrokeAttributeType]
        Layout of the CSV file
    policy: HandleMissingDataPolicy
        Policy to handle missing data
    delimiter: str
        Delimiter
    """
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    sensor_strided_array, layout_export = ink_model.get_strokes_as_strided_array_extended(layout=layout, policy=policy,
                                                                                          include_stroke_idx=True)
    header = ["idx"] + [attr.name for attr in layout_export]
    with path.open('w') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=delimiter, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(header)
        for row in sensor_strided_array:
            idx: int = int(row[0])
            for i in range(1, len(row), len(layout_export)):
                csv_writer.writerow([idx] + row[i: i + len(layout_export)])

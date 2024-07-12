# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom Authors. All Rights Reserved.
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
from pathlib import Path
from typing import List

from uim.codec.parser.uim import UIMParser
from uim.model.helpers.serialize import serialize_sensor_data_csv
from uim.model.ink import InkModel
from uim.model.inkdata.strokes import InkStrokeAttributeType

if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    # This file contains ink from different providers: PEN, TOUCH, MOUSE
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'special' / 'ink.uim')
    # Decide which attributes to serialize
    layout: List[InkStrokeAttributeType] = [
        InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y, InkStrokeAttributeType.SENSOR_TIMESTAMP,
        InkStrokeAttributeType.SENSOR_PRESSURE, InkStrokeAttributeType.SENSOR_ALTITUDE,
        InkStrokeAttributeType.SENSOR_AZIMUTH
    ]
    # Serialize the model to CSV
    serialize_sensor_data_csv(ink_model, Path('sensor_data.csv'), layout=layout)

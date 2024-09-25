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

from uim.codec.parser.iotpaper import IOTPaperParser
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.helpers.serialize import json_encode, serialize_raw_sensor_data_csv
from uim.model.ink import InkModel
from uim.model.inkinput.inputdata import InkSensorType, Unit

if __name__ == '__main__':
    paper_file: Path = Path(__file__).parent / '..' / '..' / 'ink' / 'iot' / 'HelloInk.paper'
    parser: IOTPaperParser = IOTPaperParser()

    parser.cropping_ink = False
    parser.cropping_offset = 10
    ink_model: InkModel = parser.parse(paper_file)
    img: bytes = parser.parse_template(paper_file)
    with Path("iot.uim").open("wb") as file:
        file.write(UIMEncoder310().encode(ink_model))
    with Path("template.bmp").open("wb") as file:
        file.write(img)
    layout: List[InkSensorType] = [
        InkSensorType.TIMESTAMP, InkSensorType.X, InkSensorType.Y, InkSensorType.Z,
        InkSensorType.PRESSURE, InkSensorType.ALTITUDE,
        InkSensorType.AZIMUTH
    ]
    # In the Universal Ink Model, the sensor data is in SI units:
    # - timestamp: seconds
    # - x, y, z: meters
    # - pressure: N
    serialize_raw_sensor_data_csv(ink_model, Path('sensor_data.csv'), layout)
    # If you want to convert the data to different units, you can use the following code:
    serialize_raw_sensor_data_csv(ink_model, Path('sensor_data_unit.csv'), layout,
                                    {
                                        InkSensorType.X: Unit.MM,  # Convert meters to millimeters
                                        InkSensorType.Y: Unit.MM,  # Convert meters to millimeters
                                        InkSensorType.Z: Unit.MM,  # Convert meters to millimeters
                                        InkSensorType.TIMESTAMP: Unit.MS  # Convert seconds to milliseconds
                                     })
    # Convert the model to JSON
    with open('ink.json', 'w') as f:
        # json_encode is a helper function to convert the model to JSON
        f.write(json_encode(ink_model))

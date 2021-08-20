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
from typing import Dict
from uuid import UUID

from uim.codec.parser.uim import UIMParser
from uim.model.ink import InkModel
from uim.model.inkinput.inputdata import InkInputType, InputContext, SensorContext, InputDevice
from uim.model.inkinput.sensordata import SensorData

if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    # This file contains ink from different providers: PEN, TOUCH, MOUSE
    ink_model: InkModel = parser.parse('../ink/uim_3.1.0/6) Different Input Providers.uim')
    mapping_type: Dict[UUID, InkInputType] = {}
    if ink_model.has_ink_structure():
        print('InkInputProviders:')
        print('-------------------')
        # Iterate Ink input providers
        for ink_input_provider in ink_model.input_configuration.ink_input_providers:
            print(f' InkInputProvider. ID: {ink_input_provider.id} | type: {ink_input_provider.type}')
            mapping_type[ink_input_provider.id] = ink_input_provider.type
        print()
        print('Strokes:')
        print('--------')
        # Iterate over strokes
        for stroke in ink_model.strokes:
            print(f'|- Stroke (id:={stroke.id} | points count: {stroke.points_count})')
            if stroke.style and stroke.style.path_point_properties:
                print(f'|   |- Style (render mode:={stroke.style.render_mode_uri} | color:=('
                      f'red: {stroke.style.path_point_properties.red}, '
                      f'green: {stroke.style.path_point_properties.green}, '
                      f'blue: {stroke.style.path_point_properties.green}, '
                      f'alpha: {stroke.style.path_point_properties.alpha}))')
            # Stroke is produced by sensor data being processed by the ink geometry pipeline
            sd: SensorData = ink_model.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
            # Get InputContext for the sensor data
            input_context: InputContext = ink_model.input_configuration.get_input_context(sd.input_context_id)
            # Retrieve SensorContext
            sensor_context: SensorContext = ink_model.input_configuration\
                .get_sensor_context(input_context.sensor_context_id)
            for scc in sensor_context.sensor_channels_contexts:
                # Sensor channel context is referencing input device
                input_device: InputDevice = ink_model.input_configuration.get_input_device(scc.input_device_id)
                print(f'|   |- Input device (id:={input_device.id} | type:=({mapping_type[scc.input_provider_id]})')
                # Iterate over sensor channels
                for c in scc.channels:
                    print(f'|   |     |- Sensor channel (id:={c.id} | name: {c.type.name} '
                          f'| values: {sd.get_data_by_id(c.id).values}')
            print('|')



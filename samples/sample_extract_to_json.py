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

from uim.codec.parser.uim import UIMParser
from uim.model.helpers.serialize import json_encode
from uim.model.ink import InkModel

if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'special' / 'ink.uim')
    # Convert the model to JSON
    with open('ink.json', 'w') as f:
        # json_encode is a helper function to convert the model to JSON
        f.write(json_encode(ink_model))


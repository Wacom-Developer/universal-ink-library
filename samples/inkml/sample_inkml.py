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
import uuid
from pathlib import Path

from uim.codec.parser.inkml import InkMLParser
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.ink import InkModel


if __name__ == '__main__':
    parser: InkMLParser = InkMLParser()
    device_id: str = uuid.uuid4().hex
    parser.cropping_ink = True
    # Kondate database is not using namespace
    parser.default_namespace = ''
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'inkml' / 'reference.inkml')
    with Path("inkml.uim").open("wb") as file:
        file.write(UIMEncoder310().encode(ink_model))

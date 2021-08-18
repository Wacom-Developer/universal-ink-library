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
import io

from uim.codec.parser.uim import UIMParser
from uim.codec.parser.will import WILL2Parser
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.ink import InkModel

if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    # Parse UIM v3.0.0
    ink_model: InkModel = parser.parse('../ink/uim_3.0.0/1) Value of Ink 1.uim')
    # Save the model, this will overwrite an existing file
    with io.open('1) Value of Ink 1_3_0_0_to_3_1_0.uim', 'wb') as uim:
        # Encode as UIM v3.1.0
        uim.write(UIMEncoder310().encode(ink_model))
    # ------------------------------------------------------------------------------------------------------------------
    #  Parse UIM v3.1.0
    # ------------------------------------------------------------------------------------------------------------------
    ink_model: InkModel = parser.parse('../ink/uim_3.1.0/1) Value of Ink 1 (3.1 delta).uim')
    # Save the model, this will overwrite an existing file
    with io.open('1) Value of Ink 1_3_1_0.uim', 'wb') as uim:
        # Encode as UIM v3.1.0
        uim.write(UIMEncoder310().encode(ink_model))
    # ------------------------------------------------------------------------------------------------------------------
    #  Parse WILL 2 file from Inkspace (https://inkspace.wacom.com/)
    # ------------------------------------------------------------------------------------------------------------------
    parser: WILL2Parser = WILL2Parser()
    ink_model_2: InkModel = parser.parse('../ink/will/elephant.will')
    # Save the model, this will overwrite an existing file
    with io.open('elephant.uim', 'wb') as uim:
        # Encode as UIM v3.1.0
        uim.write(UIMEncoder310().encode(ink_model_2))

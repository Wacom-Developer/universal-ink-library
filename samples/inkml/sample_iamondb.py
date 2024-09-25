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
from typing import Dict, Any, List

from uim.utils.print import print_tree
from uim.codec.parser.inkml import InkMLParser
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.helpers.schema_content_extractor import uim_schema_semantics_from
from uim.model.ink import InkModel
from uim.model.semantics.schema import SegmentationSchema, IS


if __name__ == '__main__':
    parser: InkMLParser = InkMLParser()
    parser.set_typedef_pred(IS)
    parser.content_view = 'hwr'
    parser.register_type('type', 'Document', SegmentationSchema.ROOT)
    parser.register_type('type', 'Formula', SegmentationSchema.MATH_BLOCK)
    parser.register_type('type', 'Arrow', SegmentationSchema.CONNECTOR)
    parser.register_type('type', 'Table', SegmentationSchema.TABLE)
    parser.register_type('type', 'Structure', SegmentationSchema.BORDER)
    parser.register_type('type', 'Diagram', SegmentationSchema.DIAGRAM)
    parser.register_type('type', 'Drawing', SegmentationSchema.DRAWING)
    parser.register_type('type', 'Correction', SegmentationSchema.CORRECTION)
    parser.register_type('type', 'Symbol', '<T>')
    parser.register_type('type', 'Marking', SegmentationSchema.MARKING)
    parser.register_type('type', 'Marking_Bracket', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE, 'other')])
    parser.register_type('type', 'Marking_Encircling', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE, 'encircling')])
    parser.register_type('type', 'Marking_Angle', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE, 'other')])
    parser.register_type('type', 'Marking_Underline', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE,
                                    "underlining")])
    parser.register_type('type', 'Marking_Sideline', SegmentationSchema.MARKING,
                         subtypes=[(SegmentationSchema.HAS_MARKING_TYPE, 'other')])
    parser.register_type('type', 'Marking_Connection', SegmentationSchema.CONNECTOR)

    parser.register_type('type', 'Textblock', SegmentationSchema.TEXT_REGION)
    parser.register_type('type', 'Textline', SegmentationSchema.TEXT_LINE)
    parser.register_type('type', 'Word', SegmentationSchema.WORD)

    parser.register_type('type', 'Garbage', SegmentationSchema.GARBAGE)
    parser.register_type('type', 'List', SegmentationSchema.LIST)
    parser.register_value('transcription', SegmentationSchema.HAS_CONTENT)

    parser.cropping_ink = False
    parser.cropping_offset = 10
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'inkml' / 'iamondb.inkml')

    structures: List[Dict[str, Any]] = uim_schema_semantics_from(ink_model, "hwr")
    print_tree(structures)
    with Path("iamondb.uim").open("wb") as file:
        file.write(UIMEncoder310().encode(ink_model))

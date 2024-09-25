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
from typing import List, Dict, Any

from uim.codec.parser.uim import UIMParser
from uim.utils.print import print_tree
from uim.model.helpers.schema_content_extractor import uim_schema_semantics_from
from uim.model.ink import InkModel
from uim.model.semantics.schema import CommonViews

if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    # Parse UIM v3.0.0
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'schemas' / 'math-structures.uim')
    math_structures: List[Dict[str, Any]] = uim_schema_semantics_from(ink_model,
                                                                      semantic_view=CommonViews.HWR_VIEW.value)
    # Print the tree structure
    print_tree(math_structures)

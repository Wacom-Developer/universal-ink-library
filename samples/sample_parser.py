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
from uim.codec.parser.uim import UIMParser
from uim.model.helpers.text_extractor import uim_extract_text_and_semantics_from
from uim.model.ink import InkModel
from uim.model.semantics.syntax import CommonViews, SEMANTIC_HAS_URI, SEMANTIC_HAS_LABEL, \
    SEMANTIC_HAS_TYPE

if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse('../ink/uim_3.1.0/2) Digital Ink is processable 1 (3.1 delta).uim')
    if ink_model.has_knowledge_graph() and ink_model.has_tree(CommonViews.HWR_VIEW.value) \
            and ink_model.has_tree(CommonViews.NER_VIEW.value):
        # The sample
        text_lines, entities = uim_extract_text_and_semantics_from(ink_model, hwr_view=CommonViews.HWR_VIEW.value,
                                                                   ner_view=CommonViews.NER_VIEW.value)
        line_number: int = 1
        print('-------------------------------------------------------------------------------------------------------')
        print(' Text lines:')
        print('-------------------------------------------------------------------------------------------------------')
        for line in text_lines:
            print(f'{line_number}. Text line: {line["line"]} | {line["box"]}')
            word_num: int = 1
            for word in line['words']:
                print(f' {word_num}. Word: {word["word"]} | {word["box"]}')
                print(f'  -> Stroke UUIDs: {[str(w) for w in word["strokes"]]}')
                word_num += 1
            line_number += 1
        print()
        entity_number: int = 1
        print('-------------------------------------------------------------------------------------------------------')
        print(' Entities:')
        print('-------------------------------------------------------------------------------------------------------')
        for entity in entities:
            print(f'{entity_number}. URI: {entity["statements"][SEMANTIC_HAS_URI]} - '
                  f'{entity["statements"][SEMANTIC_HAS_LABEL]} '
                  f'({entity["statements"][SEMANTIC_HAS_TYPE]})')
            entity_number += 1

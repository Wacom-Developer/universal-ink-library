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
from pathlib import Path

from uim.codec.parser.uim import UIMParser
from uim.model.helpers.text_extractor import uim_extract_text_and_semantics_from
from uim.model.ink import InkModel
from uim.model.semantics.schema import CommonViews

if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'uim_3.1.0' /
                                       '2) Digital Ink is processable 1 (3.1 delta).uim')
    if ink_model.has_knowledge_graph() and ink_model.has_tree(CommonViews.HWR_VIEW.value):
        # The sample
        words, entities, text = uim_extract_text_and_semantics_from(ink_model, hwr_view=CommonViews.HWR_VIEW.value)
        print('=' * 100)
        print(' Recognised text: ')
        print(text)
        print('=' * 100)
        print(' Words:')
        print('=' * 100)
        for word_idx, word in enumerate(words):
            print(f' Word #{word_idx + 1}:')
            print(f'  Text: {word["text"]}')
            print(f'  Alternatives: {word["alternatives"]}')
            print(f'  Bounding box: x:={word["bounding_box"]["x"]}, y:={word["bounding_box"]["y"]}, '
                  f'width:={word["bounding_box"]["width"]}, height:={word["bounding_box"]["height"]}')
            print('')
        print('=' * 100)
        print(' Entities:')
        print('=' * 100)
        entity_idx: int = 1
        for entity_uri, entity_mappings in entities.items():
            print(f' Entity #{entity_idx}: URI: {entity_uri}')
            print("-" * 100)
            print(f" Label: {entity_mappings[0]['label']}")
            print(' Ink Stroke IDs:')
            for word_idx, entity in enumerate(entity_mappings):
                print(f"  #{word_idx + 1}: Word match: {entity['path_id']}")
            print('=' * 100)
            entity_idx += 1

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
from typing import List, Dict, Any, Tuple

from uim.codec.parser.uim import UIMParser
from uim.model.helpers.schema_content_extractor import uim_schema_semantics_from
from uim.model.ink import InkModel
from uim.model.semantics.schema import CommonViews


def build_tree(node_list: List[Dict[str, Any]]):
    """
    Build a tree structure from the node list.
    Parameters
    ----------
    node_list: `List[Dict[str, Any]]`
        List of nodes
    """
    # Step 1: Create dictionaries for nodes and parent-child relationships
    children_dict: Dict[str, Any] = {}

    for node in node_list:
        parent_uri: str = node['parent_uri']
        if parent_uri is not None:
            if parent_uri not in children_dict:
                children_dict[parent_uri] = []
            children_dict[parent_uri].append(node)

    # Step 2: Define a recursive function to print the tree
    def print_tree(node_display: Dict[str, Any], indent: int = 0):
        info: str = ""
        attributes: List[Tuple[str, Any]] = node_display.get('attributes', [])
        if "path_id" in node_display:
            info = f"(#strokes:={len(node_display['path_id'])})"
        elif "bounding_box" in node_display:
            info = (f"(x:={node_display['bounding_box']['x']}, y:={node_display['bounding_box']['y']}, "
                    f"width:={node_display['bounding_box']['width']}, "
                    f"height:={node_display['bounding_box']['height']})")
        print('|' + '-' * indent + f" [type:={node_display['type']}] - {info}")
        if len(attributes) > 0:
            print('|' + ' ' * (indent + 4) + "| -[Attributes:]")
            for key, value in attributes:
                print('|' + ' ' * (indent + 8) + f"\t|-- {key}:={value}")
        if node_display['node_uri'] in children_dict:
            for child in children_dict[node_display['node_uri']]:
                print_tree(child, indent + 4)

    # Step 3: Find the root node (where parent_uri is None) and start printing the tree
    for node in node_list:
        if node['parent_uri'] is None:
            print_tree(node)


if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    # Parse UIM v3.0.0
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'schemas' / 'math-structures.uim')
    math_structures: List[Dict[str, Any]] = uim_schema_semantics_from(ink_model,
                                                                      semantic_view=CommonViews.HWR_VIEW.value)
    # Print the tree structure
    build_tree(math_structures)

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
from typing import List, Dict, Any

from uim.model.helpers.treeiterator import PreOrderEnumerator
from uim.model.ink import InkModel
from uim.model.semantics import schema
from uim.model.semantics.node import InkNode, StrokeGroupNode, StrokeNode


def __collected_stroke_ids__(node: StrokeGroupNode) -> List[uuid.UUID]:
    """
    Collecting all stroke ids from the node.
    Parameters
    ----------
    node: `StrokeGroupNode`
        Stroke group node

    Returns
    -------
    strokes: `List[uuid.UUID]`
        List of stroke ids
    """
    strokes: List[uuid.UUID] = []
    for child in node.children:
        if isinstance(child, StrokeNode):
            strokes.append(child.stroke.id)
        elif isinstance(child, StrokeGroupNode):
            strokes.extend(__collected_stroke_ids__(child))
    return strokes


def uim_schema_semantics_from(ink_model: InkModel, semantic_view: str = schema.CommonViews.HWR_VIEW.value)\
        -> List[Dict[str, Any]]:
    """
    Extract schema semantics from the ink model.
    Parameters
    ----------
    ink_model: `InkModel`
        Ink model
    semantic_view: `str`
        Semantic view

    Returns
    -------
    elements: `List[Dict[str, Any]]`
        List of schema semantics elements. The structure of the element is as follows:
        {
            'node_uri': `uuid.UUID`
                URI of the node
            'parent_uri': `Optional[uuid.UUID]`
                URI of the parent node
            'path_id': `List[uuid.UUID]`
                List of stroke ids
            'bounding_box': `Dict[str, float]`
                Bounding box
            'type': `str`
                Type
            'attributes': `List[Tuple[str, Any]]`
                List of attributes
        }

    Example
    -------
    >>> from uim.model.ink import InkModel
    >>> from uim.codec.parser.uim import UIMParser
    >>> from uim.model.helpers.schema_content_extractor import uim_schema_semantics_from
    >>> parser = UIMParser()
    >>> ink_model = parser.parse("path/to/ink.uim")
    >>> schema_semantics = uim_schema_semantics_from(ink_model)
    >>> print(schema_semantics)
    >>> [
    >>>   {
    >>>     'node_uri': UUID('16918b3f-b192-466e-83a3-54835ddfff11'),
    >>>     'parent_uri': UUID('16918b3f-b192-466e-83a3-54835ddfff11'),
    >>>     'path_id': [UUID('16918b3f-b192-466e-83a3-54835ddfff11')],
    >>>     'bounding_box': {'x': 175.71, 'y': 150.65, 'width': 15.91, 'height': 27.018},
    >>>     'type': 'will:math-structures/0.1/Symbol',
    >>>      'attributes': [('symbolType', 'Numerical'), ('representation', 'e')]
    >>>   }, ... ]
    """

    elements: List[Dict[str, Any]] = []
    entity_map: Dict[str, Dict[str, Any]] = {}
    root: InkNode = ink_model.view_root(str(semantic_view))

    # Iterate for triples with triple list and look for words
    for s in ink_model.knowledge_graph.statements:
        if s.predicate == schema.IS:
            if s.subject not in entity_map:
                entity_map[s.subject] = {
                    'type': s.object,
                    'attributes': [(st.predicate, st.object)
                                   for st in ink_model.knowledge_graph.all_statements_for(s.subject)
                                   if st.predicate != schema.IS]
                }
    ink_model.calculate_bounds_recursively(root)
    # Iterate
    for node in PreOrderEnumerator(root):
        if node.uri in entity_map:
            path_ids: List[uuid.UUID] = __collected_stroke_ids__(node)
            entry: Dict[str, Any] = {
                'path_id': path_ids, 'node_uri': node.uri, 'parent_uri': node.parent.uri if node.parent else None,
                'bounding_box': {
                    'x': node.group_bounding_box.x,
                    'y': node.group_bounding_box.y,
                    'width': node.group_bounding_box.width,
                    'height': node.group_bounding_box.height
                },
                'type': entity_map[node.uri]['type'],
                'attributes': entity_map[node.uri]['attributes']
            }
            elements.append(entry)
    return elements

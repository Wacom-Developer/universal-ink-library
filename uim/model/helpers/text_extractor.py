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
import string
import uuid
from typing import List, Tuple, Optional, Dict, Any

from uim.codec.parser.uim import UIMParser
from uim.model.helpers.treeiterator import PreOrderEnumerator
from uim.model.ink import InkModel
from uim.model.semantics.node import InkNode, StrokeGroupNode, StrokeNode
from uim.model.semantics.schema import WORD, TEXT_LINE, CommonViews, HAS_ALTERNATIVE, HAS_CONTENT, HAS_NAMED_ENTITY, \
    HAS_URI, HAS_LABEL


def uim_extract_text_and_semantics(uim_bytes: bytes, hwr_view: str = CommonViews.HWR_VIEW.value,
                                   ner_view: Optional[str] = None) \
        -> Tuple[List[dict], List[dict]]:
    """
    Extracting the text from Universal Ink Model.

    Parameters
    ----------
    uim_bytes: `bytes`
        Byte array with RIFF file from Universal Ink Model
    hwr_view: `str`
       HWR view.
    ner_view: `str`
        NER view if needed.

    Returns
    -------
    text: `List[dict]`
        List of text lines. Each line has its own dict containing the  bounding box, and all words
    entities.

    Raises
    ------
        `InkModelException`
            If the Universal Ink Model does not contain the view with the requested view name.
    """
    uim_parser: UIMParser = UIMParser()
    ink_object: InkModel = uim_parser.parse(uim_bytes)
    return uim_extract_text_and_semantics_from(ink_object, hwr_view, ner_view)


def __collected_stroke_ids__(node: StrokeGroupNode) -> List[uuid.UUID]:
    strokes: List[uuid.UUID] = []
    for child in node.children:
        if isinstance(child, StrokeNode):
            strokes.append(child.stroke.id)
        elif isinstance(child, StrokeGroupNode):
            strokes.extend(__collected_stroke_ids__(child))
    return strokes


def uim_extract_text_and_semantics_from(ink_model: InkModel, hwr_view: str = CommonViews.HWR_VIEW.value)\
        -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]], str]:
    """
    Extracting the text from Universal Ink Model.

    Parameters
    ----------
    ink_model: InkModel -
        Universal Ink Model
    hwr_view: str -
       Name of the HWR view.

    Returns
    -------
    words: `List[dict]`
        List of words. Each word has its own dict containing the text, bounding box, and all alternatives.
    entities: `Dict[str, List[dict]]`
        Dictionary of entities. Each entity has its own dict containing the label, instance, and path ids.
    text: `str`
        Text extracted from the Universal Ink Model.
    Raises
    ------
        `InkModelException`
            If the Universal Ink Model does not contain the view with the requested view name.

     Examples
    --------

    """
    text: str = ''
    words: List[Dict[str, Any]] = []
    entity_map: Dict[str, Dict[str, Any]] = {}
    root: InkNode = ink_model.view_root(str(hwr_view))
    text_nodes: Dict[str, str] = {}
    text_alternatives: Dict[str, List[str]] = {}
    text_lines: List[str] = []
    entities: Dict[str, List[Dict[str, Any]]] = {}

    # Iterate for triples with triple list and look for words
    for s in ink_model.knowledge_graph.statements:
        if s.predicate.startswith(HAS_ALTERNATIVE):
            if s.subject not in text_alternatives:
                text_alternatives[s.subject] = []
            text_alternatives[s.subject].append(s.object)
        # Collect all words
        if s.object == WORD:
            all_statements = ink_model.knowledge_graph.all_statements_for(s.subject, predicate=HAS_CONTENT)
            if len(all_statements) == 1:
                text_nodes[s.subject] = all_statements[0].object
        # Collect all entities
        if s.predicate == HAS_NAMED_ENTITY:
            all_statements = ink_model.knowledge_graph.all_statements_for(s.object)
            entity: Dict[str, Any] = {'instance': s.object}
            for st in all_statements:
                if st.predicate.startswith('hasPart'):
                    entity_map[st.object] = entity
                elif st.predicate == HAS_URI:
                    entity['uri'] = st.object
                elif st.predicate == HAS_LABEL:
                    entity['label'] = st.object
                    # Check for text lines
        elif s.object == TEXT_LINE:
            text_lines.append(s.subject)
    # Position
    pos: int = 0
    # Iterate
    for node in PreOrderEnumerator(root):
        if node.uri in text_lines:
            for word_node in node.children:
                path_ids: List[str] = [str(p.stroke.id) for p in word_node.children if isinstance(p, StrokeNode)]
                if word_node.uri in text_nodes:
                    alternatives: List[str] = text_alternatives.get(word_node.uri, [])
                    t = text_nodes[word_node.uri]
                    if t in string.punctuation or pos == 0:
                        text += t
                    else:
                        text += f' {t}'
                    words.append({
                        'alternatives': alternatives, 'text': t, 'path_id': path_ids, "word-uri": word_node.uri,
                        "bounding_box": {
                            'x': word_node.group_bounding_box.x,
                            'y': word_node.group_bounding_box.y,
                            'width': word_node.group_bounding_box.width,
                            'height': word_node.group_bounding_box.height
                        }
                    })
                    # Position
                    pos += 1
                if word_node.uri in entity_map:
                    uri: str = entity_map[word_node.uri]['uri']
                    if uri not in entities:
                        entities[uri] = []
                    entities[uri].append(
                        {
                            'path_id': path_ids,
                            'label': entity_map[word_node.uri]['label'],
                            'instance': entity_map[word_node.uri]['instance']
                        }
                    )
            text += '\n'
    if text.endswith('\n'):
        text = text[:-1]
    return words, entities, text

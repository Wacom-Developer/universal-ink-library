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
from typing import List, Tuple, Optional

from uim.codec.parser.uim import UIMParser
from uim.model.base import InkModelException
from uim.model.helpers.treeiterator import PreOrderEnumerator
from uim.model.ink import InkModel
from uim.model.semantics.node import InkNode, StrokeGroupNode, StrokeNode
from uim.model.semantics.syntax import WORD, SEMANTIC_IS, TEXT_LINE, SEMANTIC_HAS_URI, \
    SEMANTIC_HAS_RELEVANT_CONCEPT, SEMANTIC_HAS_NAMED_ENTITY, CommonViews, SEMANTIC_HAS_TYPE


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


def uim_extract_text_and_semantics_from(ink_model: InkModel, hwr_view: str = CommonViews.HWR_VIEW.value,
                                        ner_view: Optional[str] = None) -> Tuple[List[dict], List[dict]]:
    """
    Extracting the text from Universal Ink Model.

    Parameters
    ----------
    ink_model: InkModel -
        Universal Ink Model
    hwr_view: str -
       Name of the HWR view.
    ner_view: str -
        Name of the NER view if needed.

    Returns
    -------
    tuple(list of text lines (including bounding box), list knowledge uris)

    Raises
    ------
        `InkModelException`
            If the Universal Ink Model does not contain the view with the requested view name.

     Examples
    --------
    >>> from uim.codec.parser.uim import UIMParser
    >>> from uim.model.helpers.text_extractor import uim_extract_text_and_semantics_from
    >>> from uim.model.ink import InkModel
    >>> from uim.model.semantics.syntax import CommonViews, SEMANTIC_HAS_URI, SEMANTIC_HAS_LABEL, SEMANTIC_HAS_TYPE
    >>>
    >>> parser: UIMParser = UIMParser()
    >>> ink_model: InkModel = parser.parse('../ink/uim_3.1.0/2) Digital Ink is processable 1 (3.1 delta).uim')
    >>> if ink_model.has_knowledge_graph():
    >>>     #  Extract text lines and entities from model
    >>>     text_lines, entities = uim_extract_text_and_semantics_from(ink_model, hwr_view=CommonViews.HWR_VIEW.value,
    >>>                                                                ner_view=CommonViews.NER_VIEW.value)
    >>>     line_number: int = 1
    >>>     print('---------------------------------------------------------------------------------------------------')
    >>>     print(' Text lines:')
    >>>     print('---------------------------------------------------------------------------------------------------')
    >>>     for line in text_lines:
    >>>        print(f'{line_number}. Text line: {line["line"]} | {line["box"]}')
    >>>        word_num: int = 1
    >>>        for word in line['words']:
    >>>            print(f' {word_num}. Word: {word["word"]} | {word["box"]}')
    >>>            print(f'  -> Stroke UUIDs: {[str(w) for w in word["strokes"]]}')
    >>>            word_num += 1
    >>>        line_number += 1
    >>>     print()
    >>>     entity_number: int = 1
    >>>     print('---------------------------------------------------------------------------------------------------')
    >>>     print(' Entities:')
    >>>     print('---------------------------------------------------------------------------------------------------')
    >>>     for entity in entities:
    >>>         print(f'{entity_number}. URI: {entity["statements"][SEMANTIC_HAS_URI]} - '
    >>>               f'{entity["statements"][SEMANTIC_HAS_LABEL]} '
    >>>               f'({entity["statements"][SEMANTIC_HAS_TYPE]})')
    >>>         entity_number += 1
    """
    lines: List[dict] = []
    text_nodes: dict = {}
    text_line_nodes: list = []
    ne_node_mapping: dict = {}
    uris_mapping: dict = {}
    types: List[dict] = []
    type_mapping: dict = {}
    for s in ink_model.knowledge_graph.statements:
        if s.object == WORD:
            all_statements = ink_model.knowledge_graph.all_statements_for(s.subject, predicate=SEMANTIC_IS)
            if len(all_statements) == 1:
                text_nodes[s.subject] = all_statements[0].object
        elif s.object == TEXT_LINE:
            text_line_nodes.append(s.subject)
        elif s.predicate == SEMANTIC_HAS_NAMED_ENTITY:
            if s.subject not in ne_node_mapping:
                ne_node_mapping[s.subject] = []
            ne_node_mapping[s.subject].append(s.object)
        elif s.predicate == SEMANTIC_HAS_URI:
            uris_mapping[s.subject] = s.object
        elif s.predicate == SEMANTIC_HAS_RELEVANT_CONCEPT:
            type_mapping[s.subject] = s.object
    try:
        root: InkNode = ink_model.view_root(hwr_view)
        for node in PreOrderEnumerator(root):
            # First find text lines
            if node.uri in text_line_nodes:
                line: dict = {'line': '', 'box': node.group_bounding_box, 'words': []}
                # Add each word to line
                for word_node in node.children:
                    if word_node.uri in text_nodes:
                        t: str = text_nodes[word_node.uri]
                        line['words'].append({'word': t, 'box': word_node.group_bounding_box,
                                              'strokes': __collected_stroke_ids__(word_node)})
                        line['line'] += '{}'.format(t if t in string.punctuation else ' {}'.format(t))
                lines.append(line)
    except KeyError as e:
        raise InkModelException(f'The  requested handwriting recognition view does not exist. {e}')
    if ner_view is not None:
        try:
            ner_root: InkNode = ink_model.view_root(ner_view)
            for group in PreOrderEnumerator(ner_root):
                if isinstance(group, StrokeGroupNode):
                    for node in group.children:
                        if node.uri in ne_node_mapping:
                            for ne_uri in ne_node_mapping[node.uri]:
                                entity: dict = {'uri': ne_uri, 'statements': {}, 'strokes': []}
                                # Add statements
                                statements: list = ink_model.knowledge_graph.all_statements_for(ne_uri)
                                for st in statements:
                                    if st.predicate in [SEMANTIC_HAS_TYPE]:
                                        if st.predicate not in entity['statements']:  # List not yet created
                                            entity['statements'][st.predicate] = [st.object]
                                        else:
                                            entity['statements'][st.predicate].append(st.object)
                                    elif st.predicate in entity['statements']:
                                        if isinstance(entity['statements'][st.predicate], list):
                                            entity['statements'][st.predicate].append(st.object)
                                        else:
                                            first_entry: str = entity['statements'][st.predicate]
                                            # override as list
                                            entity['statements'][st.predicate] = [first_entry, st.object]
                                    else:
                                        entity['statements'][st.predicate] = st.object
                                if isinstance(node, StrokeGroupNode):
                                    entity['strokes'] = __collected_stroke_ids__(node)
                                types.append(dict(entity))
        except KeyError as e:
            raise InkModelException(f'The  requested named entity recognition view does not exist. {e}')
    return lines, types

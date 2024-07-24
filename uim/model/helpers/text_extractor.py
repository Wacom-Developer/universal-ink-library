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
import string
import uuid
from typing import List, Tuple, Dict, Any, Optional

from uim.codec.parser.uim import UIMParser
from uim.model.helpers.schema_content_extractor import __collected_stroke_ids__
from uim.model.helpers.treeiterator import PreOrderEnumerator
from uim.model.ink import InkModel
from uim.model.semantics.node import InkNode, StrokeGroupNode, StrokeNode
from uim.model.semantics.schema import CommonViews, SegmentationSchema, NamedEntityRecognitionSchema

SEMANTIC_PREFIX: str = 'will://semantic/3.0/'
LEGACY_WORD: str = 'will://segmentation/3.0/Word'
LEGACY_TEXT_LINE: str = 'will://segmentation/3.0/TextLine'
LEGACY_HAS_CONTENT: str = f'{SEMANTIC_PREFIX}is'
LEGACY_HAS_ALT_CONTENT: str = f'{SEMANTIC_PREFIX}hasAlt'
LEGACY_HAS_NAMED_ENTITY: str = f'{SEMANTIC_PREFIX}hasNamedEntityDefinition'

LEGACY_NE_MAPPING: Dict[str, str] = {
    f'{SEMANTIC_PREFIX}nerBackend': 'provider',
    f'{SEMANTIC_PREFIX}hasUri': 'uri',
    f'{SEMANTIC_PREFIX}hasLabel': 'label',
    f'{SEMANTIC_PREFIX}hasThumb': 'image',
    f'{SEMANTIC_PREFIX}hasAbstract': 'description',
    f'{SEMANTIC_PREFIX}hasConfidence': 'confidence'
}

NE_MAPPING: Dict[str, str] = {
    NamedEntityRecognitionSchema.HAS_LANGUAGE.lower(): 'language',
    NamedEntityRecognitionSchema.HAS_PROVIDER.lower(): 'provider',
    NamedEntityRecognitionSchema.HAS_CREATION_DATE.lower(): 'creationDate',
    NamedEntityRecognitionSchema.HAS_ABSTRACT_TEXT.lower(): 'description',
    NamedEntityRecognitionSchema.HAS_THUMBNAIL_URL.lower(): 'image',
    NamedEntityRecognitionSchema.HAS_URI.lower(): 'uri',
    NamedEntityRecognitionSchema.HAS_LABEL.lower(): 'label',
    NamedEntityRecognitionSchema.HAS_ENTITY_TYPE.lower(): 'ontologyType'
}


def uim_extract_text_and_semantics(uim_bytes: bytes, hwr_view: str = CommonViews.HWR_VIEW.value) \
        -> tuple[list[dict], Any, str]:
    """
    Extracting the text from Universal Ink Model.

    Parameters
    ----------
    uim_bytes: `bytes`
        Byte array with RIFF file from Universal Ink Model
    hwr_view: `str`
       HWR view.

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
    """
    uim_parser: UIMParser = UIMParser()
    ink_object: InkModel = uim_parser.parse(uim_bytes)
    return uim_extract_text_and_semantics_from(ink_object, hwr_view)


def uim_extract_text_and_semantics_from(ink_model: InkModel, hwr_view: str = CommonViews.HWR_VIEW.value)\
        -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]], str]:
    """
    Extracting the text from Universal Ink Model.

    Parameters
    ----------
    ink_model: InkModel
        Universal Ink Model
    hwr_view: str
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
    >>> from pathlib import Path
    >>> from typing import Dict, Any
    >>> from uim.codec.parser.uim import UIMParser
    >>> from uim.model.helpers.text_extractor import uim_extract_text_and_semantics_from
    >>> path: Path = Path('ink_3_1_0.uim')
    >>> parser: UIMParser = UIMParser()
    >>> ink_model: InkModel = parser.parse(path)
    >>> words, entities, text = uim_extract_text_and_semantics_from(ink_model, CommonViews.HWR_VIEW.value)
    >>> for word in words:
    >>>     print(f"[text]: {word['text']}")
    >>>     print(f"[alternatives]: {'|'.join(word['alternatives'])}")
    >>>     print(f"[path ids]: {word['path_id']}")
    >>>     print(f"[word URI]: {word['word-uri']}")
    >>>     print(f"[bounding box]: x: {word['bounding_box']['x']}, y: {word['bounding_box']['y']}, "
    >>>           f"width: {word['bounding_box']['width']}, height: {word['bounding_box']['height']}")
    >>> for entity_uri, entity_hits in entities.items():
    >>>     print(f"[entity URI]: {entity_uri}")
    >>>     for entity in entity_hits:
    >>>         print(f"[entity]: {entity}")
    >>>         print(f"[path ids]: {entity['path_id']}")
    >>>         print(f"[instance]: {entity['instance']}")
    >>>         print(f"[provider]: {entity['provider']}")
    >>>         print(f"[uri]: {entity['uri']}")
    >>>         print(f"[image]: {entity['image']}")
    >>>         print(f"[description]: {entity['description']}")
    >>>         print(f"[label]: {entity['label']}")
    >>>         print(f"[bounding box]: x: {entity['bounding_box']['x']}, y: {entity['bounding_box']['y']}, "
    >>>               f"width: {entity['bounding_box']['width']}, height: {entity['bounding_box']['height']}")
    >>> print(f"[text]: {text}")
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
        if s.predicate.startswith(SegmentationSchema.HAS_ALT_CONTENT):
            if s.subject not in text_alternatives:
                text_alternatives[s.subject] = []
            text_alternatives[s.subject].append(s.object)
        if s.predicate == LEGACY_HAS_ALT_CONTENT:
            if s.subject not in text_alternatives:
                text_alternatives[s.subject] = []
            text_alternatives[s.subject].append(s.object)
        # Collect all words
        if s.object in [SegmentationSchema.WORD_OF_STROKES, SegmentationSchema.WORD]:
            all_statements = ink_model.knowledge_graph.all_statements_for(s.subject,
                                                                          predicate=SegmentationSchema.HAS_CONTENT)
            if len(all_statements) == 1:
                text_nodes[s.subject] = all_statements[0].object
        if s.object == LEGACY_WORD:
            all_statements = ink_model.knowledge_graph.all_statements_for(s.subject, predicate=LEGACY_HAS_CONTENT)
            if len(all_statements) == 1:
                text_nodes[s.subject] = all_statements[0].object
        # Collect all entities
        if s.predicate == NamedEntityRecognitionSchema.HAS_NAMED_ENTITY:
            all_statements = ink_model.knowledge_graph.all_statements_for(s.object)
            entity: Dict[str, Any] = {'instance': s.object}
            entity_map[s.subject] = entity
            for st in all_statements:
                if st.predicate.lower().startswith('haspart'):
                    entity_map[st.object] = entity
                elif st.predicate.lower() in NE_MAPPING:
                    entity[NE_MAPPING[st.predicate.lower()]] = st.object
        # Collect all entities for the legacy view
        if s.predicate == LEGACY_HAS_NAMED_ENTITY:
            all_statements = ink_model.knowledge_graph.all_statements_for(s.object)
            entity: Dict[str, Any] = {'instance': s.object}
            entity_map[s.subject] = entity
            for st in all_statements:
                if st.predicate in LEGACY_NE_MAPPING:
                    entity[LEGACY_NE_MAPPING[st.predicate]] = st.object
        # Collect all text lines
        if s.object == SegmentationSchema.TEXT_LINE:
            text_lines.append(s.subject)
        if s.object == LEGACY_TEXT_LINE:
            text_lines.append(s.subject)
    # Position
    pos: int = 0
    # Iterate
    for node in PreOrderEnumerator(root):
        if node.uri in text_lines:
            for word_node in node.children:
                path_ids: List[uuid.UUID] = __collected_stroke_ids__(node)
                if word_node.uri in text_nodes:
                    alternatives: List[str] = text_alternatives.get(word_node.uri, [])
                    t = text_nodes[word_node.uri]
                    if t in string.punctuation or pos == 0:
                        text += t
                    else:
                        text += f' {t}'
                    words.append({
                        'alternatives': alternatives, 'text': t, 'path_id': path_ids, 'word-uri': word_node.uri,
                        'bounding_box': {
                            'x': word_node.group_bounding_box.x,
                            'y': word_node.group_bounding_box.y,
                            'width': word_node.group_bounding_box.width,
                            'height': word_node.group_bounding_box.height
                        }
                    })
                    # Position
                    pos += 1
                if word_node.uri in entity_map:
                    uri: str = entity_map[word_node.uri].get('uri', '')
                    if uri not in entities:
                        entities[uri] = []
                    entry: Dict[str, Any] = {
                        'path_id': path_ids,
                        'instance': entity_map[word_node.uri]['instance'],
                        'bounding_box': {
                            'x': word_node.group_bounding_box.x,
                            'y': word_node.group_bounding_box.y,
                            'width': word_node.group_bounding_box.width,
                            'height': word_node.group_bounding_box.height
                        }
                    }
                    for key in entity_map[word_node.uri]:
                        entry[key] = entity_map[word_node.uri][key]
                    entities[uri].append(entry)
            text += '\n'
    ne_view: Optional[InkNode] = None
    if ink_model.has_tree(CommonViews.LEGACY_NER_VIEW.value):
        # In the legacy view, the named entities are in a separate view
        ne_view = ink_model.view_root(CommonViews.LEGACY_NER_VIEW.value)
    if ink_model.has_tree(CommonViews.NER_VIEW.value):
        # In the new view, the named entities are in a separate view
        ne_view = ink_model.view_root(CommonViews.NER_VIEW.value)
    if ne_view is not None:
        for node in PreOrderEnumerator(ne_view):
            if node.uri in entity_map:
                path_ids: List[uuid.UUID] = __collected_stroke_ids__(node)
                uri: str = entity_map[node.uri]['uri'] if 'uri' in entity_map[node.uri] else ''
                if uri not in entities:
                    entities[uri] = []
                entry: Dict[str, Any] = {
                    'path_id': path_ids,
                    'instance': entity_map[node.uri]['instance'],
                    'bounding_box': {
                        'x': node.group_bounding_box.x,
                        'y': node.group_bounding_box.y,
                        'width': node.group_bounding_box.width,
                        'height': node.group_bounding_box.height
                    }
                }
                for key in entity_map[node.uri]:
                    entry[key] = entity_map[node.uri][key]
                entities[uri].append(entry)
    if text.endswith('\n'):
        text = text[:-1]
    return words, entities, text

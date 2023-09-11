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
from enum import Enum
from typing import List, Optional

# Class tag
IS: str = '@'
# Content segmentation schema
SEGMENTATION_SCHEMA_VERSION: str = '0.3'
SEGMENTATION_SCHEMA: str = f'will:seg/{SEGMENTATION_SCHEMA_VERSION}'

ROOT: str = f'{SEGMENTATION_SCHEMA}/Root'
TEXT_REGION: str = f'{SEGMENTATION_SCHEMA}/TextRegion'
TEXT_LINE: str = f'{SEGMENTATION_SCHEMA}/TextLine'
WORD: str = f'{SEGMENTATION_SCHEMA}/WordOfStrokes'

HAS_NAMED_ENTITY_DEFINITION: str = "hasNamedEntity"
PART_OF_NAMED_ENTITY: str = "isPartOfNamedEntity"
PART_OF_POS_ENTITY: str = "isPartOfPOSEntity"
REPRESENTS_VIEW: str = 'representsView'
GENERATED_BY: str = 'generatedBy'

# Named Entity Recognition schema
NER_SCHEMA_VERSION: str = '0.1'
NER_SCHEMA: str = f"will:ner/{NER_SCHEMA_VERSION}"
NAMED_ENTITY: str = f'{NER_SCHEMA}/NamedEntity'
HAS_TOPIC_ENTITY: str = 'hasDocumentCategory'
HAS_ARTICLE_URL: str = "hasArticleUrl"
HAS_URI: str = "hasURI"
HAS_SOURCE: str = "hasSource"
HAS_CONTENT: str = "hasContent"
HAS_LANGUAGE: str = "hasLanguage"
HAS_LABEL: str = "hasLabel"
HAS_ALTERNATIVE: str = "hasAltContent"
HAS_ABSTRACT: str = "hasAbstractText"
HAS_CREATION_DATE: str = "hasCreationDate"
HAS_PROVIDER: str = "hasProvider"
HAS_ONTOLOGY_TYPE: str = "hasProvidedOntologyType"
HAS_NAMED_ENTITY: str = "hasNamedEntity"
HAS_ARTICLE: str = "hasAbstractText"
HAS_THUMB: str = "hasThumbnailUrl"
HAS_IMAGE: str = "hasImageUrl"
HAS_TYPE: str = "hasProvidedEntityType"
HAS_CONFIDENCE: str = "hasConfidence"
HAS_UNIQUE_ID: str = "hasUniqueId"

# URI Templates
NODE_URI_PREFIX: str = 'uim:node/{}'
NODE_ENTITY_URI_PREFIX: str = 'uim:ne/{}'

# Document Properties
WILL_NAMESPACE: str = "will://"
DOCUMENT_NAMESPACE: str = WILL_NAMESPACE + "document/3.0/"
DOCUMENT_TITLE_OBJECT: str = DOCUMENT_NAMESPACE + 'Title'
DOCUMENT_CREATION_DATE_OBJECT: str = DOCUMENT_NAMESPACE + 'CreationData'
DOCUMENT_X_MIN_PROPERTY: str = DOCUMENT_NAMESPACE + 'hasMinX'
DOCUMENT_Y_MIN_PROPERTY: str = DOCUMENT_NAMESPACE + 'hasMiny'
DOCUMENT_WIDTH_PROPERTY: str = DOCUMENT_NAMESPACE + 'Width'
DOCUMENT_HEIGHT_PROPERTY: str = DOCUMENT_NAMESPACE + 'Height'


class CommonRDF(object):
    """
    Contains a list of used RDF types.
    """
    PRED_RDF_HAS_TYPE: str = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'  # Type according to RDF 1.1 XML Syntax.
    LOCALE: str = 'http://ogp.me/ns#locale'  # Locale as defined in Open Graph Protocol.


class CommonViews(Enum):
    """
    Contains a list of known ink model views.
    """
    CUSTOM_TREE = 'custom'  # Custom
    MAIN_INK_TREE = 'main'  # Main tree of ink strokes.
    MAIN_SENSOR_TREE = 'sdm'  # Main tree of sensor data objects.
    HWR_VIEW = 'hwr'  # Handwriting Recognition view.
    NER_VIEW = 'ner'  # Named Entity Recognition view.
    SEGMENTATION_VIEW = 'seg'  # Segmentation view.
    LEGACY_HWR_VIEW = 'will://views/3.0/HWR'  # Handwriting Recognition view (legacy constant - v3.0).
    LEGACY_NER_VIEW = 'will://views/3.0/NER'  # Named Entity Recognition view (legacy constant - v3.0).


# Mapping the view name to enum
NAME_TO_VIEW: dict = dict([(view.value, view) for view in CommonViews])

class SemanticTriple(object):
    """
    SemanticTriple
    ==============
    A semantic triple, or simply triple, is the atomic data entity data model.
    As its name indicates, a triple is a set of three entities that codifies a statement about semantic data in the
    form of subject predicate object expressions.

    Parameters
    ----------
    subject: str
        Subject
    predicate: str
        Predicate
    obj: str
        Object
    """

    def __init__(self, subject: str, predicate: str, obj: str):
        self.__subject = subject
        self.__predicate = predicate
        self.__object = obj

    @property
    def subject(self) -> str:
        """Subject of the statement. (`str`)"""
        return self.__subject

    @subject.setter
    def subject(self, subject: str):
        self.__subject = subject

    @property
    def predicate(self) -> str:
        """Predicate of the statement. (`str`)"""
        return self.__predicate

    @predicate.setter
    def predicate(self, predicate: str):
        self.__predicate = predicate

    @property
    def object(self) -> str:
        """Object of the statement. (`str`)"""
        return self.__object

    @object.setter
    def object(self, obj: str):
        self.__object = obj

    def __repr__(self):
        return '<Semantic triple : [subject:={}, predicate:={}, object:={}]>'.format(self.__subject, self.__predicate,
                                                                                     self.__object)

    def __dict__(self):
        return {'subject': self.__subject, 'predicate': self.__predicate, 'object': self.__object}

    def __eq__(self, obj):
        if not isinstance(obj, SemanticTriple):
            return False
        return (self.subject == obj.subject and
                self.predicate == obj.predicate and
                self.object == obj.object)

    def __json__(self):
        return {
            'subject': self.subject,
            'predicate': self.predicate,
            'object': self.object,
        }


class TripleStore(object):
    """
    TripleStore
    ===========

    Encapsulates a list of triple statements.

    Parameters
    ----------
    triple_statements: List[SemanticTriple]
        List of `SemanticTriple`s
    """

    def __init__(self, triple_statements: List[SemanticTriple] = None):
        self.__triple_statement: List[SemanticTriple] = triple_statements or []

    def append(self, triple_statement: SemanticTriple):
        """Appending the triple statement.

        Parameters
        ----------
        triple_statement: SemanticTriple
            Triple that needs to be added
        """
        self.__triple_statement.append(triple_statement)

    def add_semantic_triple(self, subject: str, predicate: str, obj: str):
        """
        Adding a semantic triple
        :param subject: subject of the statement
        :param predicate: predicate of the statement
        :param obj: object of the statement
        """
        self.append(SemanticTriple(subject, predicate, obj))

    def remove_semantic_triple(self, triple: SemanticTriple):
        """
        Removes a semantic triple from list.

        Parameters
        ----------
        triple: `SemanticTriple`
            Triple to be removed
        """
        self.__triple_statement.remove(triple)

    def clear_statements(self):
        """Remove all statements."""
        self.__triple_statement = []

    @property
    def statements(self) -> List[SemanticTriple]:
        """List of triple statements. (`List[SemanticTriple]`)"""
        return self.__triple_statement

    def all_statements_for(self, subject: str, predicate: str = None) -> List[SemanticTriple]:
        """
        Returns all statements for a specific subject.

        Parameters
        ----------
        subject: `str`
            Filter for the subject URI
        predicate: `str`
            Predicate filter [optional]

        Returns
        -------
        statements: `List[SemanticTriple]`
            List of statements that match the filters.
        """
        return [s for s in self.statements if s.subject == subject and
                (predicate is None or s.predicate == predicate)]

    def filter(self, subject: Optional[str] = None, predicate: Optional[str] = None, obj: Optional[str] = None) \
            -> List[SemanticTriple]:
        """
        Returns all statements for a specific subject.

        Parameters
        ----------
        subject: `Optional[str]`
            Filter for the subject URI [optional]
        predicate: `Optional[str]`
            Predicate filter [optional]
        obj: `Optional[str]`
            Object filter [optional]

        Returns
        -------
        statements: `List[SemanticTriple]`
            List of statements that match the filters.
        """

        results: List[SemanticTriple] = []
        for s in self.statements:
            if subject is not None and subject != s.subject:
                continue
            if predicate is not None and predicate != s.predicate:
                continue
            if obj is not None and obj != s.object:
                continue
            results.append(s)

        return results

    def determine_sem_type(self, node: 'InkNode', typedef_pred: str = CommonRDF.PRED_RDF_HAS_TYPE) -> Optional[str]:
        """
        Determine the Semantic Type of node.

        Parameters
        ----------
        node: `InkNode`
            `InkNode` to extract the semantics from
        typedef_pred: `str`
            Predicate string

        Returns
        -------
        semantic_type: `str`
             Semantic type of the `InkNode`. None if the node is not found or the predicate statement.
        """
        triples: List[SemanticTriple] = self.filter(subject=node.uri, predicate=typedef_pred)
        if len(triples) == 1:
            return triples[0].object
        else:
            return None

    def __iter__(self):
        return iter(self.__triple_statement)

    def __repr__(self):
        return '<TripleStore : [statements:={}]>'.format(self.__triple_statement)

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

IS: str = '@'
WILL_NAMESPACE: str = "will://"
SEM_NAMESPACE: str = f"{WILL_NAMESPACE}semantic/3.0/"
# Subject
INK_INPUT_DEVICE: str = WILL_NAMESPACE + "input/3.0/"
SEGMENTATION_NAMESPACE: str = WILL_NAMESPACE + "segmentation/3.0/"
DOCUMENT_NAMESPACE: str = WILL_NAMESPACE + "document/3.0/"
# Properties
DEVICE_SERIAL_NUMBER_PROPERTY: str = INK_INPUT_DEVICE + "SerialNumber"
DEVICE_MANUFACTURER_PROPERTY: str = INK_INPUT_DEVICE + "Manufacturer"
DEVICE_MODEL_PROPERTY: str = INK_INPUT_DEVICE + "Model"
# Predicate Syntax
SEMANTIC_NAMESPACE: str = WILL_NAMESPACE + "semantic/3.0/"
# HWR Semantics
SEMANTIC_HAS_ALT: str = SEMANTIC_NAMESPACE + "hasAlt"
SEMANTIC_IS: str = SEMANTIC_NAMESPACE + "is"
# Semantic Ink
SEMANTIC_HAS_CATEGORY: str = SEMANTIC_NAMESPACE + "hasCategory"
SEMANTIC_HAS_URI: str = SEMANTIC_NAMESPACE + "hasUri"
SEMANTIC_HAS_TYPE: str = SEMANTIC_NAMESPACE + "hasType"
SEMANTIC_HAS_RELEVANT_CONCEPT: str = SEMANTIC_NAMESPACE + "hasRelevantConcept"
SEMANTIC_HAS_ARTICLE: str = SEMANTIC_NAMESPACE + "hasArticle"
SEMANTIC_HAS_IMAGE: str = SEMANTIC_NAMESPACE + "hasImage"
SEMANTIC_HAS_THUMB: str = SEMANTIC_NAMESPACE + "hasThumb"
SEMANTIC_HAS_LABEL: str = SEMANTIC_NAMESPACE + "hasLabel"
SEMANTIC_HAS_EMAIL: str = SEMANTIC_NAMESPACE + "hasEmail"
SEMANTIC_HAS_FIRST_NAME: str = SEMANTIC_NAMESPACE + "hasFirstname"
SEMANTIC_HAS_LAST_NAME: str = SEMANTIC_NAMESPACE + "hasLastname"
SEMANTIC_HAS_START_DATE: str = SEMANTIC_NAMESPACE + "hasStartDate"
SEMANTIC_HAS_END_DATE: str = SEMANTIC_NAMESPACE + "hasEndDate"
SEMANTIC_HAS_CONFIDENCE: str = SEMANTIC_NAMESPACE + "hasConfidence"
SEMANTIC_HAS_NER_BACKEND: str = SEMANTIC_NAMESPACE + "nerBackend"
SEMANTIC_HAS_ABSTRACT: str = SEMANTIC_NAMESPACE + "hasAbstract"
SEMANTIC_HAS_SOURCE: str = SEMANTIC_NAMESPACE + "hasSource"
SEMANTIC_HAS_GEOLOCATION: str = SEMANTIC_NAMESPACE + "hasGeoLocation"
SEMANTIC_HAS_LOCATION: str = SEMANTIC_NAMESPACE + "hasLocation"

SEMANTIC_HAS_WEBSITE: str = SEMANTIC_NAMESPACE + "hasWebsite"
SEMANTIC_HAS_NAMED_ENTITY: str = SEMANTIC_NAMESPACE + "hasNamedEntityDefinition"
SEMANTIC_HAS_TOPIC_ENTITY: str = SEMANTIC_NAMESPACE + "hasTopicEntity"
SEMANTIC_HAS_LOCATION_TYPE: str = SEMANTIC_NAMESPACE + "hasLocationType"
# Document Properties
DOCUMENT_TITLE_OBJECT: str = DOCUMENT_NAMESPACE + 'Title'
DOCUMENT_CREATION_DATE_OBJECT: str = DOCUMENT_NAMESPACE + 'CreationData'
DOCUMENT_X_MIN_PROPERTY: str = DOCUMENT_NAMESPACE + 'hasMinX'
DOCUMENT_Y_MIN_PROPERTY: str = DOCUMENT_NAMESPACE + 'hasMiny'
DOCUMENT_WIDTH_PROPERTY: str = DOCUMENT_NAMESPACE + 'Width'
DOCUMENT_HEIGHT_PROPERTY: str = DOCUMENT_NAMESPACE + 'Height'

# Document Structure
TEXT_LINE: str = SEGMENTATION_NAMESPACE + "TextLine"
WORD: str = SEGMENTATION_NAMESPACE + "Word"
TEXT_REGION: str = SEGMENTATION_NAMESPACE + "TextRegion"
PARAGRAPH: str = SEGMENTATION_NAMESPACE + "Paragraph"
SENTENCE: str = SEGMENTATION_NAMESPACE + "Sentence"
PUNCTUATION: str = SEGMENTATION_NAMESPACE + "Punctuation"
PHRASE: str = SEGMENTATION_NAMESPACE + "Phrase"

# Graphics semantics
GRAPHICS_NAMESPACE: str = WILL_NAMESPACE + "shapes/3.0/"

MATH_NAMESPACE: str = 'uim://math/'
# Math
MATH_BLOCK: str = 'will://segmentation/3.0/MathBlock'
LATEX_REPRESENTATION: str = 'will://math/3.0/attr/hasLatexRepresentation'
MATHML_REPRESENTATION: str = 'will://math/3.0/attr/hasMathMLRepresentation'
# Math schema
MATH_CONTENT_BLOCK: str = MATH_NAMESPACE + 'MathBlock'
EXPRESSION_BLOCK: str = MATH_NAMESPACE + 'Expression'
GROUP_BLOCK: str = MATH_NAMESPACE + 'Group'
MATRIX_BLOCK: str = MATH_NAMESPACE + 'Matrix'
OPERAND_BLOCK: str = MATH_NAMESPACE + 'Operand'
OPERATOR: str = MATH_NAMESPACE + 'Operator'
SYMBOL: str = MATH_NAMESPACE + 'Symbol'
EQUALITY_SYMBOL: str = MATH_NAMESPACE + 'Equals'
FENCE: str = MATH_NAMESPACE + 'Fence'
SQUARE_ROOT: str = MATH_NAMESPACE + 'SquareRoot'
FRACTION: str = MATH_NAMESPACE + 'Fraction'
NUMBER: str = MATH_NAMESPACE + 'Number'
SUPERSCRIPT: str = MATH_NAMESPACE + 'SuperScript'
SUBSCRIPT: str = MATH_NAMESPACE + 'SubScript'
LATEX_EXPORT: str = MATH_NAMESPACE + 'attr/hasLatexRepresentation'
MATHML_EXPORT: str = MATH_NAMESPACE + 'attr/hasMathMLRepresentation'

POLYGON_TYPE: str = GRAPHICS_NAMESPACE + 'Polygon'
CIRCLE_TYPE: str = GRAPHICS_NAMESPACE + 'Circle'
ELLIPSE_TYPE: str = GRAPHICS_NAMESPACE + 'Ellipse'
TRIANGLE_TYPE: str = GRAPHICS_NAMESPACE + 'Triangle'
LINE_TYPE: str = GRAPHICS_NAMESPACE + 'Line'
RECTANGLE_TYPE: str = GRAPHICS_NAMESPACE + 'Rectangle'

# URI Templates
NODE_URI_PREFIX: str = 'uim:node/{}'
NODE_ENTITY_URI_PREFIX: str = 'uim:ne/{}'


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


class Semantics(object):
    """
    Contains types and entities that are used to store ontological knowledge definitions into the ink model's knowledge
    graph.
    """
    PRED_HAS_NAMED_ENTITY_DEFINITION: str = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    PRED_IS: str = f'{SEM_NAMESPACE}is'
    TYPE: str = '@'


class SegmentationSchema(object):
    """
    UIM content segmentation schema prototype (generic).
    """
    WODL_CLASS_PREFIX: str = 'will:seg/0.3/'
    BORDER: str = WODL_CLASS_PREFIX + 'Border'
    CONNECTOR: str = WODL_CLASS_PREFIX + 'Connector'
    CORRECTION: str = WODL_CLASS_PREFIX + 'Correction'
    DIAGRAM: str = WODL_CLASS_PREFIX + 'Diagram'
    DIAGRAM_CONNECTOR: str = WODL_CLASS_PREFIX + 'DiagramConnector'
    DRAWING: str = WODL_CLASS_PREFIX + 'Drawing'
    DRAWING_ITEM_GROUP: str = WODL_CLASS_PREFIX + 'DrawingItemGroup'
    DRAWING_ITEM: str = WODL_CLASS_PREFIX + 'DrawingItem'
    GARBAGE: str = WODL_CLASS_PREFIX + 'Garbage'
    LIST: str = WODL_CLASS_PREFIX + 'List'
    LIST_ITEM: str = WODL_CLASS_PREFIX + 'ListItem'
    LIST_ITEM_BODY: str = 'body'
    UNLABELLED: str = WODL_CLASS_PREFIX + 'Unlabelled'
    UNLABELLED_BLOCK: str = WODL_CLASS_PREFIX + 'UnlabelledBlock'
    UNLABELLED_ITEM_GROUP: str = WODL_CLASS_PREFIX + 'UnlabelledItemGroup'
    UNLABELLED_ITEM: str = WODL_CLASS_PREFIX + 'UnlabelledItem'
    MARKING: str = WODL_CLASS_PREFIX + 'Marking'
    MARKING_TYPE_UNDERLINING: str = 'underlining'
    MARKING_TYPE_PREDICATE: str = 'markingType'
    MARKING_TYPE_ENCIRCLING: str = 'encircling'
    MATH_BLOCK: str = WODL_CLASS_PREFIX + 'MathBlock'
    MATH_ITEM_GROUP: str = WODL_CLASS_PREFIX + 'MathItemGroup'
    MATH_ITEM: str = WODL_CLASS_PREFIX + 'MathItem'
    SEGMENTATION_ROOT: str = WODL_CLASS_PREFIX + 'Root'
    TABLE: str = WODL_CLASS_PREFIX + 'Table'
    TEXT_REGION: str = WODL_CLASS_PREFIX + 'TextRegion'
    TEXT_LINE: str = WODL_CLASS_PREFIX + 'TextLine'
    WORD: str = WODL_CLASS_PREFIX + 'WordOfStrokes'


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

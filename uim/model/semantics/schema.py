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
import logging
from enum import Enum
from logging import Logger
from typing import List, Optional, Any

logger: Logger = logging.getLogger(__name__)

# Class tag
IS: str = '@'
# URI Templates
NODE_URI_PREFIX: str = 'uim:node/{}'
NODE_ENTITY_URI_PREFIX: str = 'uim:ne/{}'

# Document Properties
WILL_NAMESPACE: str = "will://"
DOCUMENT_NAMESPACE: str = WILL_NAMESPACE + "document/3.0/"
DOCUMENT_TITLE_OBJECT: str = DOCUMENT_NAMESPACE + 'Title'
DOCUMENT_AUTHOR_OBJECT: str = DOCUMENT_NAMESPACE + 'Author'
DOCUMENT_APPLICATION_OBJECT: str = DOCUMENT_NAMESPACE + 'Application'
DOCUMENT_APPLICATION_VERSION_OBJECT: str = DOCUMENT_NAMESPACE + 'ApplicationVersion'
DOCUMENT_LOCALE_OBJECT: str = DOCUMENT_NAMESPACE + 'Locale'

DOCUMENT_CREATION_DATE_OBJECT: str = DOCUMENT_NAMESPACE + 'CreationData'
DOCUMENT_X_MIN_PROPERTY: str = DOCUMENT_NAMESPACE + 'hasMinX'
DOCUMENT_Y_MIN_PROPERTY: str = DOCUMENT_NAMESPACE + 'hasMiny'
DOCUMENT_WIDTH_PROPERTY: str = DOCUMENT_NAMESPACE + 'Width'
DOCUMENT_HEIGHT_PROPERTY: str = DOCUMENT_NAMESPACE + 'Height'
# Device properties
WILL_NAMESPACE: str = "will://"
# Subject
INK_INPUT_DEVICE: str = WILL_NAMESPACE + "input/3.0/"
SEGMENTATION_NAMESPACE: str = WILL_NAMESPACE + "segmentation/3.0/"
DOCUMENT_NAMESPACE: str = WILL_NAMESPACE + "document/3.0/"
# Properties
DEVICE_SERIAL_NUMBER_PROPERTY: str = INK_INPUT_DEVICE + "SerialNumber"
DEVICE_MANUFACTURER_PROPERTY: str = INK_INPUT_DEVICE + "Manufacturer"
DEVICE_MODEL_PROPERTY: str = INK_INPUT_DEVICE + "Model"


class SegmentationSchema:
    """
    SegmentationSchema
    ==================
    The segmentation schema is used to segment the content of the ink model.
    """
    # Content segmentation schema
    SEGMENTATION_SCHEMA_VERSION: str = '0.3'
    SEGMENTATION_SCHEMA: str = f'will:seg/{SEGMENTATION_SCHEMA_VERSION}'
    ROOT: str = f'{SEGMENTATION_SCHEMA}/Root'
    PART_OF_NAMED_ENTITY: str = "isPartOfNamedEntity"
    PART_OF_POS_ENTITY: str = "isPartOfPOSEntity"
    REPRESENTS_VIEW: str = 'representsView'
    GENERATED_BY: str = 'generatedBy'
    HAS_CONTENT: str = "hasContent"
    HAS_ALTERNATIVE: str = "hasAltContent"
    BORDER: str = SEGMENTATION_SCHEMA + 'Border'
    CONNECTOR: str = SEGMENTATION_SCHEMA + 'Connector'
    CORRECTION: str = SEGMENTATION_SCHEMA + 'Correction'
    DIAGRAM: str = SEGMENTATION_SCHEMA + 'Diagram'
    DIAGRAM_CONNECTOR: str = SEGMENTATION_SCHEMA + 'DiagramConnector'
    DIAGRAM_PART: str = SEGMENTATION_SCHEMA + 'DiagramPart'
    DRAWING: str = SEGMENTATION_SCHEMA + 'Drawing'
    DRAWING_ITEM_GROUP: str = SEGMENTATION_SCHEMA + 'DrawingItemGroup'
    DRAWING_ITEM: str = SEGMENTATION_SCHEMA + 'DrawingItem'
    GARBAGE: str = SEGMENTATION_SCHEMA + 'Garbage'
    LIST: str = SEGMENTATION_SCHEMA + 'List'
    LIST_ITEM: str = SEGMENTATION_SCHEMA + 'ListItem'
    LIST_ITEM_BODY: str = 'body'
    UNLABELLED: str = SEGMENTATION_SCHEMA + 'Unlabelled'
    UNLABELLED_BLOCK: str = SEGMENTATION_SCHEMA + 'UnlabelledBlock'
    UNLABELLED_ITEM_GROUP: str = SEGMENTATION_SCHEMA + 'UnlabelledItemGroup'
    UNLABELLED_ITEM: str = SEGMENTATION_SCHEMA + 'UnlabelledItem'
    MARKING: str = SEGMENTATION_SCHEMA + 'Marking'
    MARKING_TYPE_UNDERLINING: str = 'underlining'
    MARKING_TYPE_PREDICATE: str = 'markingType'
    MARKING_TYPE_ENCIRCLING: str = 'encircling'
    MATH_BLOCK: str = SEGMENTATION_SCHEMA + 'MathBlock'
    MATH_ITEM_GROUP: str = SEGMENTATION_SCHEMA + 'MathItemGroup'
    MATH_ITEM: str = SEGMENTATION_SCHEMA + 'MathItem'
    SEGMENTATION_ROOT: str = SEGMENTATION_SCHEMA + 'Root'
    TABLE: str = SEGMENTATION_SCHEMA + 'Table'
    EXTENDED_TEXT_REGION: str = SEGMENTATION_SCHEMA + 'ExtendedTextRegion'
    LINE: str = SEGMENTATION_SCHEMA + 'Line'
    TEXT_REGION: str = f'{SEGMENTATION_SCHEMA}/TextRegion'
    TEXT_LINE: str = f'{SEGMENTATION_SCHEMA}/TextLine'
    WORD: str = f'{SEGMENTATION_SCHEMA}/WordOfStrokes'
    CHEMISTRY_BLOCK: str = SEGMENTATION_SCHEMA + 'ChemistryBlock'
    PHYSICS_BLOCK: str = SEGMENTATION_SCHEMA + 'PhysicsBlock'
    CHEMICAL_STRUCTURE: str = SEGMENTATION_SCHEMA + 'ChemicalStructure'


class NamedEntityRecognitionSchema(SegmentationSchema):
    """
    NamedEntityRecognitionSchema
    ============================
    The Named Entity Recognition schema is used to recognize named entities in the ink model.
    """
    # Named Entity Recognition schema
    NER_SCHEMA_VERSION: str = '0.1'
    NER_SCHEMA: str = f"will:ner/{NER_SCHEMA_VERSION}"
    NAMED_ENTITY: str = f'{NER_SCHEMA}/NamedEntity'
    HAS_TOPIC_ENTITY: str = 'hasDocumentCategory'
    HAS_ARTICLE_URL: str = "hasArticleUrl"
    HAS_URI: str = "hasURI"
    HAS_SOURCE: str = "hasSource"
    HAS_LANGUAGE: str = "hasLanguage"
    HAS_LABEL: str = "hasLabel"
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


# --------------------------------------------- Math Constants ---------------------------------------------------------
class MathSchema(SegmentationSchema):
    """
    MathSchema
    ==========
    The Math schema is used to represent mathematical expressions in the ink model.
    """
    # Math schema
    MATH_SCHEMA_VERSION: str = "0.6"
    MATH_NAMESPACE: str = f'will:math/{MATH_SCHEMA_VERSION}/'
    MATH_BLOCK: str = f'{SegmentationSchema.SEGMENTATION_SCHEMA}MathBlock'
    # Properties
    LATEX_REPRESENTATION: str = 'hasLatex'
    MATHML_REPRESENTATION: str = 'hasMathML'
    
    # Term
    COMPOUND_TERM: str = f'{MATH_NAMESPACE}CompoundTerm'
    # Properties
    HAS_REPRESENTATION_PROP: str = 'representation'
    # Number class
    NUMBER: str = f'{MATH_NAMESPACE}Number'
    # Properties
    NUMBER_TYPE_PROP: str = 'numberType'
    NUMERIC_REPRESENTATION_PROP: str = 'representation'
    # Symbol class
    SYMBOL: str = f'{MATH_NAMESPACE}Symbol'
    HAS_SYMBOL_TYPE: str = 'symbolType'
    # Expression class
    EXPRESSION: str = f'{MATH_NAMESPACE}Expression'
    # Expression Properties
    HAS_CHILD_PROP: str = 'hasChild'
    ITEMS_PROP: str = 'items'
    # Matrix Class
    MATRIX: str = f'{MATH_NAMESPACE}Matrix'
    MATRIX_ROW: str = f'{MATH_NAMESPACE}Row'
    # Matrix / Matrix Row Properties
    MATRIX_ROW_PROP: str = 'hasRow'
    MATRIX_ROW_CELL_PROP: str = 'hasCell'
    
    # Square Root Class
    ROOT: str = f'{MATH_NAMESPACE}Root'
    # Square Root Properties
    ROOT_DEGREE_PROP: str = 'degree'
    ROOT_EXPRESSION_PROP: str = 'hasChild'
    ROOT_SIGN_PROP: str = 'rootSign'
    
    # Fraction Class
    FRACTION: str = f'{MATH_NAMESPACE}Fraction'
    # Fraction Properties
    FRACTION_NUMERATOR_PROP: str = 'numerator'
    FRACTION_DENOMINATOR_PROP: str = 'denominator'
    HAS_FRACTION_OPERATOR_PROP: str = 'operator'
    FRACTION_TYPE_PROP: str = "fractionType"
    # Indexed Class
    INDEXED: str = f'{MATH_NAMESPACE}Indexed'
    OPENING_BRACKET: str = "openingBracket"
    CLOSING_BRACKET: str = "closingBracket"
    HAS_SUPERSCRIPT: str = "superScript"
    HAS_SUBSCRIPT: str = "subScript"
    HAS_OVERSCRIPT: str = "overScript"
    HAS_UNDERSCRIPT: str = "underScript"
    HAS_PRESUBSCRIPT: str = "preSubScript"
    HAS_PRESUPERSCRIPT: str = "preSuperScript"
    
    FENCED: str = f"{MATH_NAMESPACE}Fenced"
    SYSTEM: str = f"{MATH_NAMESPACE}System"
    
    VERTICAL_FENCED: str = f"{MATH_NAMESPACE}Cases"
    HAS_BRACKET: str = 'hasBracket'
    HAS_OPENING_BRACKET_PROP: str = 'openingBracket'
    HAS_CLOSING_BRACKET_PROP: str = 'closingBracket'
    
    # Fraction Line
    FRACTION_LINE: str = f'{MATH_NAMESPACE}FractionLine'
    # Brackets
    BRACKETS: str = f'{MATH_NAMESPACE}Brackets'
    # Relation
    RELATION: str = f'{MATH_NAMESPACE}Relation'
    # Operator
    OPERATOR: str = f'{MATH_NAMESPACE}Operator'
# ----------------------------------------------- Math structure -------------------------------------------------------


class MathStructureSchema(SegmentationSchema):
    """
    MathStructureSchema
    ===================
    The Math structure schema is used to represent the structure of mathematical expressions in the ink model.
    """
    MATH_STRUCTURE_VERSION: str = "0.1"
    
    MATH_STRUCTURES_NAMESPACE: str = f'will:math-structures/{MATH_STRUCTURE_VERSION}/'
    MATH_BLOCK_STRUCTURES: str = f'{MATH_STRUCTURES_NAMESPACE}MathBlock'
    
    HAS_CHILD: str = "hasChild"
    HAS_ENTITY_LABEL: str = "hasEntityLabel"
    HAS_ENTITY_TYPE: str = "hasEntityType"
    IS_STRUCTURAL_ENTITY: str = "isStructuralEntity"
    IS_BASE_ENTITY: str = "isBaseEntity"
    MATH_ITEM: str = "MathItem"
    
    HAS_LATEX: str = "hasLatex"
    HAS_MATH_ML: str = "hasMathML"
    HAS_ASCII_MATH: str = "hasASCIIMath"
    STRUCTURES_EXPRESSION_LIST: str = f"{MATH_STRUCTURES_NAMESPACE}ExpressionList"
    STRUCTURES_SYSTEM: str = f"{MATH_STRUCTURES_NAMESPACE}System"
    HAS_EXPRESSIONS: str = "expressions"
    STRUCTURES_CASES: str = f"{MATH_STRUCTURES_NAMESPACE}Cases"
    EXPRESSIONS: str = "expressions"
    STRUCTURES_RADICAL: str = f"{MATH_STRUCTURES_NAMESPACE}Radical"
    INDEX: str = "index"
    RADICAL_SYMBOL: str = "radicalSymbol"
    RADICAND: str = "radicand"
    STRUCTURES_FENCE: str = f"{MATH_STRUCTURES_NAMESPACE}Fence"
    BODY: str = "body"
    STRUCTURES_FRACTION: str = f"{MATH_STRUCTURES_NAMESPACE}Fraction"
    NUMERATOR: str = "numerator"
    DENOMINATOR: str = "denominator"
    STRUCTURES_FRACTION_LINE: str = "fractionLine"
    FRACTION_TYPE: str = "fractionType"
    
    STRUCTURES_SUBSCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}Subscript"
    STRUCTURES_SUPERSCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}Superscript"
    STRUCTURES_SUB_SUPER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}SubSuperScript"
    STRUCTURES_PRE_SUPER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}PreSuperScript"
    STRUCTURES_PRE_SUB_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}PreSubScript"
    STRUCTURES_PRE_SUB_SUPER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}PreSubSuperScript"
    STRUCTURES_UNDER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}UnderScript"
    STRUCTURES_OVER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}OverScript"
    STRUCTURES_UNDER_OVER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}UnderOverScript"
    
    ROW: str = "Row"
    STRUCTURES_ROW_LIST: str = f"{MATH_STRUCTURES_NAMESPACE}RowList"
    STRUCTURES_ROW: str = f"{MATH_STRUCTURES_NAMESPACE}Row"
    STRUCTURES_MATRIX: str = f"{MATH_STRUCTURES_NAMESPACE}Matrix"
    ROWS: str = "rows"
    
    MATRIX_TYPE: str = "matrixType"
    STRUCTURES_GROUP: str = f"{MATH_STRUCTURES_NAMESPACE}Group"
    STRUCTURES_OPERATION: str = f"{MATH_STRUCTURES_NAMESPACE}Operation"
    OPERATION_TYPE: str = "operationType"
    STRUCTURES_RELATION: str = f"{MATH_STRUCTURES_NAMESPACE}Relation"
    STRUCTURES_SYMBOL: str = f"{MATH_STRUCTURES_NAMESPACE}Symbol"
    REPRESENTATION: str = "representation"
    SYMBOL_TYPE: str = "symbolType"
    STRUCTURES_MATHEMATICAL_TERM: str = f"{MATH_STRUCTURES_NAMESPACE}MathematicalTerm"
    STRUCTURES_UNIT: str = f"{MATH_STRUCTURES_NAMESPACE}Unit"
    OPERATOR_SYMBOL: str = f"{MATH_STRUCTURES_NAMESPACE}OperatorSymbol"
    RELATION_SYMBOL: str = f"{MATH_STRUCTURES_NAMESPACE}RelationSymbol"
    STRUCTURES_SEPARATOR: str = f"{MATH_STRUCTURES_NAMESPACE}Separator"
    SEPARATOR_TYPE: str = "separatorType"
    STRUCTURES_NUMBER: str = f"{MATH_STRUCTURES_NAMESPACE}Number"
    STRUCTURES_DIGIT: str = f"{MATH_STRUCTURES_NAMESPACE}Digit"
    STRUCTURES_NUMBER_ITEM: str = f"{MATH_STRUCTURES_NAMESPACE}NumberItem"


class CommonRDF:
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
NAME_TO_VIEW: dict = {view.value: view for view in CommonViews}


class SemanticTriple:
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

    def __eq__(self, other: Any):
        if not isinstance(other, SemanticTriple):
            logger.warning(f'Cannot compare {type(other)} with {type(self)}')
            return False
        return (self.subject == other.subject and
                self.predicate == other.predicate and
                self.object == other.object)

    def __repr__(self):
        return (f'<Semantic triple : [subject:={self.__subject}, predicate:={self.__predicate}, '
                f'object:={self.__object}]>')

    def __dict__(self):
        return  {
            'subject': self.subject,
            'predicate': self.predicate,
            'object': self.object,
        }

    def __json__(self):
        return self.__dict__()


class TripleStore:
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
        Adding a semantic triple.

        Parameters
        ----------
        subject: `str`
            Subject of the statement
        predicate: `str`
            Predicate of the statement
        obj: `str`
            Object of the statement
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
        Returns all statements for a specific subject. The filter ares are optional, if not provided, all statements.
        Otherwise, the statements that match the filters are returned.

        Parameters
        ----------
        subject: `Optional[str]` (optional) [default: None]
            Filter for the subject URI [optional]
        predicate: `Optional[str]` (optional) [default: None]
            Predicate filter [optional]
        obj: `Optional[str]` (optional) [default: None]
            Object filter [optional]

        Returns
        -------
        statements: `List[SemanticTriple]`
            List of statements that match the filters.

        Examples
        --------
        >>> store = TripleStore()
        >>> store.add_semantic_triple('subject-1', 'predicate', 'object-1')
        >>> store.add_semantic_triple('subject-2', 'predicate', 'object-2')
        >>> store.add_semantic_triple('subject-3', 'predicate-2', 'object-3')
        >>> store.filter('subject-1', 'predicate', 'object-1')
        [Semantic triple : [subject:=subject-1, predicate:=predicate, object:=object-1]]
        >>> store.filter('predicate')
        [Semantic triple : [subject:=subject-1, predicate:=predicate, object:=object-1],
         Semantic triple : [subject:=subject-2, predicate:=predicate, object:=object-2]]
        >>> store.filter()
        [Semantic triple : [subject:=subject-1, predicate:=predicate, object:=object-1],
         Semantic triple : [subject:=subject-2, predicate:=predicate, object:=object-2],
         Semantic triple : [subject:=subject-3, predicate:=predicate-2, object:=object-3]]
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
        typedef_pred: `str` (optional) [default: CommonRDF.PRED_RDF_HAS_TYPE]
            Predicate string

        Returns
        -------
        semantic_type: `str`
             Semantic type of the `InkNode`. None if the node is not found or the predicate statement.
        """
        triples: List[SemanticTriple] = self.filter(subject=node.uri, predicate=typedef_pred)
        if len(triples) == 1:
            return triples[0].object
        return None

    def __iter__(self):
        return iter(self.__triple_statement)

    def __repr__(self):
        return f'<TripleStore : [statements:={self.__triple_statement}]>'

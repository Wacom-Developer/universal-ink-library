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


class BaseSchema:
    """
    BaseSchema
    ==========
    Universal Ink Model base schema. Core structures that are used in several schemas.
    """
    STRUCTURE_VERSION: str = "1.1"
    STRUCTURES_NAMESPACE: str = f"will:uim/{STRUCTURE_VERSION}/"
    # -------------------------------------------- Classes -------------------------------------------------------------
    INK_MODEL: str = f"{STRUCTURES_NAMESPACE}InkModel"
    INK_NODE: str = f"{STRUCTURES_NAMESPACE}InkNode"
    ROOT: str = f"{STRUCTURES_NAMESPACE}Root"
    STROKE_NODE: str = f"{STRUCTURES_NAMESPACE}StrokeNode"
    STROKE_GROUP_NODE: str = f"{STRUCTURES_NAMESPACE}StrokeGroupNode"
    # -------------------------------------------- Properties ----------------------------------------------------------
    HAS_SCHEMA_INCLUDE: str = f"hasSchemaInclude"
    HAS_ROOT: str = f"hasRoot"
    HAS_CHILD: str = f"hasChild"
    HAS_PARENT: str = f"hasParent"
    HAS_REPRESENTS_VIEW: str = f"representsView"
    HAS_GENERATED_BY: str = f"generatedBy"
    HAS_PARENT_INK_MODEL: str = f"hasParentInkModel"
    HAS_STROKE: str = f"hasStroke"


class SimplifiedSegmentationSchema(BaseSchema):
    """
    SimplifiedSegmentationSchema
    ============================
    Universal Ink Model simplified content type segmentation schema.
    """
    STRUCTURE_VERSION: str = "0.1"
    STRUCTURES_NAMESPACE: str = f"will:smpl-seg/{STRUCTURE_VERSION}/"
    # -------------------------------------------- Classes -------------------------------------------------------------
    ROOT: str = f"{STRUCTURES_NAMESPACE}Root"
    SIMPLIFIED_BLOCK: str = f"{STRUCTURES_NAMESPACE}SimplifiedBlock"
    TEXT: str = f"{STRUCTURES_NAMESPACE}Text"
    MATH: str = f"{STRUCTURES_NAMESPACE}Math"
    MATH_REFERENCE: str = f"{STRUCTURES_NAMESPACE}MathReference"
    UNLABELLED: str = f"{STRUCTURES_NAMESPACE}Unlabelled"
    GARBAGE: str = f"{STRUCTURES_NAMESPACE}Garbage"
    DRAWING: str = f"{STRUCTURES_NAMESPACE}Drawing"
    DIAGRAM: str = f"{STRUCTURES_NAMESPACE}Diagram"
    ANNOTATION: str = f"{STRUCTURES_NAMESPACE}Annotation"
    # -------------------------------------------- Properties ----------------------------------------------------------
    HAS_PARENT: str = f"hasParent"
    HAS_CONTENT: str = f"hasContent"
    HAS_CONTENT_SCORE: str = f"hasContentScore"
    HAS_ALT_CONTENT: str = f"hasAltContent"
    HAS_ALT_CONTENT_SCORE: str = f"hasAltContentScore"
    HAS_LANGUAGE: str = f"hasLanguage"
    HAS_DIRECTION: str = f"hasDirection"
    HAS_CATEGORY_HINT: str = f"categoryHint"


class SegmentationSchema(BaseSchema):
    """
    SegmentationSchema
    ==================
    The segmentation schema is used to segment the content of the ink model.
    """
    SEG_STRUCTURE_VERSION: str = "0.3"
    SEG_STRUCTURES_NAMESPACE: str = f"will:seg/{SEG_STRUCTURE_VERSION}/"
    # -------------------------------------------- Classes -------------------------------------------------------------
    ROOT: str = f"{SEG_STRUCTURES_NAMESPACE}Root"
    CONTENT_BLOCK: str = f"{SEG_STRUCTURES_NAMESPACE}ContentBlock"
    TEXT_REGION: str = f"{SEG_STRUCTURES_NAMESPACE}TextRegion"
    TEXT_LINE: str = f"{SEG_STRUCTURES_NAMESPACE}TextLine"
    WORD: str = f"{SEG_STRUCTURES_NAMESPACE}Word"
    WORD_OF_STROKES: str = f"{SEG_STRUCTURES_NAMESPACE}WordOfStrokes"
    EXTENDED_TEXT_REGION: str = f"{SEG_STRUCTURES_NAMESPACE}ExtendedTextRegion"
    LINE: str = f"{SEG_STRUCTURES_NAMESPACE}Line"
    UNLABELLED_BLOCK: str = f"{SEG_STRUCTURES_NAMESPACE}UnlabelledBlock"
    UNLABELLED_ITEM_GROUP: str = f"{SEG_STRUCTURES_NAMESPACE}UnlabelledItemGroup"
    UNLABELLED_ITEM: str = f"{SEG_STRUCTURES_NAMESPACE}UnlabelledItem"
    DRAWING: str = f"{SEG_STRUCTURES_NAMESPACE}Drawing"
    DRAWING_ITEM_GROUP: str = f"{SEG_STRUCTURES_NAMESPACE}DrawingItemGroup"
    DRAWING_ITEM: str = f"{SEG_STRUCTURES_NAMESPACE}DrawingItem"
    EXPRESSION_BLOCK: str = f"{SEG_STRUCTURES_NAMESPACE}ExpressionBlock"
    GENERIC_EXPRESSION_BLOCK: str = f"{SEG_STRUCTURES_NAMESPACE}GenericExpressionBlock"
    GENERIC_EXPRESSION_ITEM_GROUP: str = f"{SEG_STRUCTURES_NAMESPACE}GenericExpressionItemGroup"
    GENERIC_EXPRESSION_ITEM: str = f"{SEG_STRUCTURES_NAMESPACE}GenericExpressionItem"
    MATH_BLOCK: str = f"{SEG_STRUCTURES_NAMESPACE}MathBlock"
    MATH_ITEM_GROUP: str = f"{SEG_STRUCTURES_NAMESPACE}MathItemGroup"
    MATH_ITEM: str = f"{SEG_STRUCTURES_NAMESPACE}MathItem"
    CHEMISTRY_BLOCK: str = f"{SEG_STRUCTURES_NAMESPACE}ChemistryBlock"
    CHEMISTRY_ITEM_GROUP: str = f"{SEG_STRUCTURES_NAMESPACE}ChemistryItemGroup"
    CHEMISTRY_ITEM: str = f"{SEG_STRUCTURES_NAMESPACE}ChemistryItem"
    PHYSICS_BLOCK: str = f"{SEG_STRUCTURES_NAMESPACE}PhysicsBlock"
    PHYSICS_ITEM_GROUP: str = f"{SEG_STRUCTURES_NAMESPACE}PhysicsItemGroup"
    PHYSICS_ITEM: str = f"{SEG_STRUCTURES_NAMESPACE}PhysicsItem"
    CONTENT_BLOCK_OF_STROKE_NODES: str = f"{SEG_STRUCTURES_NAMESPACE}ContentBlockOfStrokeNodes"
    CHEMICAL_STRUCTURE: str = f"{SEG_STRUCTURES_NAMESPACE}ChemicalStructure"
    SIGNATURE: str = f"{SEG_STRUCTURES_NAMESPACE}Signature"
    GARBAGE: str = f"{SEG_STRUCTURES_NAMESPACE}Garbage"
    UNLABELED: str = f"{SEG_STRUCTURES_NAMESPACE}Unlabeled"
    DOODLE: str = f"{SEG_STRUCTURES_NAMESPACE}Doodle"
    DIAGRAM: str = f"{SEG_STRUCTURES_NAMESPACE}Diagram"
    DIAGRAM_CONNECTOR: str = f"{SEG_STRUCTURES_NAMESPACE}DiagramConnector"
    DIAGRAM_PART: str = f"{SEG_STRUCTURES_NAMESPACE}DiagramPart"
    TABLE: str = f"{SEG_STRUCTURES_NAMESPACE}Table"
    BORDER: str = f"{SEG_STRUCTURES_NAMESPACE}Border"
    LIST: str = f"{SEG_STRUCTURES_NAMESPACE}List"
    LIST_ITEM: str = f"{SEG_STRUCTURES_NAMESPACE}ListItem"
    LIST_ITEM_BULLET: str = f"{SEG_STRUCTURES_NAMESPACE}ListItemBullet"
    ANNOTATION: str = f"{SEG_STRUCTURES_NAMESPACE}Annotation"
    MARKING: str = f"{SEG_STRUCTURES_NAMESPACE}Marking"
    CONNECTOR: str = f"{SEG_STRUCTURES_NAMESPACE}Connector"
    CORRECTION: str = f"{SEG_STRUCTURES_NAMESPACE}Correction"
    # -------------------------------------------- Properties ----------------------------------------------------------
    HAS_CHILD: str = f"hasChild"
    HAS_PARENT: str = f"hasParent"
    HAS_LANGUAGE: str = f"hasLanguage"
    HAS_CONTENT: str = f"hasContent"
    HAS_ALT_CONTENT: str = f"hasAltContent"
    HAS_CATEGORY_HINT: str = f"categoryHint"
    HAS_LATEX: str = f"hasLatex"
    HAS_MATHML: str = f"hasMathML"
    HAS_ASCII_MATH: str = f"hasASCIIMath"
    HAS_ENTITY_LABEL: str = f"hasEntityLabel"
    HAS_ENTITY_TYPE: str = f"hasEntityType"
    HAS_IS_STRUCTURAL_ENTITY: str = f"isStructuralEntity"
    HAS_IS_BASE_ENTITY: str = f"isBaseEntity"
    HAS_BULLET: str = f"bullet"
    HAS_BODY: str = f"body"
    HAS_MARKING_TYPE: str = f"markingType"
    HAS_ANNOTATES: str = f"annotates"
    HAS_CONNECTOR_TYPE: str = f"connectorType"
    HAS_CONNECTS: str = f"connects"
    HAS_CORRECTION_TYPE: str = f"correctionType"
    HAS_SOURCE: str = f"source"
    HAS_MODIFIER: str = f"modifier"


class NamedEntityRecognitionSchema(SegmentationSchema):
    """
    NamedEntityRecognitionSchema
    ============================
    The Named Entity Recognition schema is used to recognize named entities in the ink model.
    """
    NER_STRUCTURE_VERSION: str = '0.1'
    NER_STRUCTURE: str = f"will:ner/{NER_STRUCTURE_VERSION}/"
    # -------------------------------------------- Classes -------------------------------------------------------------
    NAMED_ENTITY: str = f'{NER_STRUCTURE}NamedEntity'
    # -------------------------------------------- Properties ----------------------------------------------------------
    HAS_NAMED_ENTITY: str = f"hasNamedEntity"
    HAS_IS_PART_OF_NAMED_ENTITY: str = f"isPartOfNamedEntity"
    HAS_URI: str = f"hasUri"
    HAS_IRI: str = f"hasIri"
    HAS_URN: str = f"hasUrn"
    HAS_UNIQUE_ID: str = f"hasUniqueId"
    HAS_IS_REFERENCE: str = f"isReference"
    HAS_PART: str = f"hasPart"
    HAS_CREATION_DATE: str = f"hasCreationDate"
    HAS_EXPIRATION_DATE: str = f"hasExpirationDate"
    HAS_LABEL: str = f"hasLabel"
    HAS_LANGUAGE: str = f"hasLanguage"
    HAS_PROVIDER: str = f"hasProvider"
    HAS_SOURCE: str = f"hasSource"
    HAS_CONFIDENCE: str = f"hasConfidence"
    HAS_NORM_CONFIDENCE: str = f"hasNormConfidence"
    HAS_ABSTRACT_TEXT: str = f"hasAbstractText"
    HAS_ARTICLE_URL: str = f"hasArticleUrl"
    HAS_WEBSITE_URL: str = f"hasWebsiteUrl"
    HAS_IMAGE_URL: str = f"hasImageUrl"
    HAS_THUMBNAIL_URL: str = f"hasThumbnailUrl"
    HAS_PROVIDED_ENTITY_TYPE: str = f"hasProvidedEntityType"
    HAS_PROVIDED_CATEGORY: str = f"hasProvidedCategory"
    HAS_PROVIDED_ONTOLOGY_TYPE: str = f"hasProvidedOntologyType"


class PartOfSpeechSchema(SegmentationSchema):
    """
    PosSchema
    ===================
    Part of Speech (POS) schema to tag handwritten text with part of POS tags.
    """
    POS_STRUCTURE_VERSION: str = "0.1"
    POS_STRUCTURES_NAMESPACE: str = f"will:pos/{POS_STRUCTURE_VERSION}/"
    # -------------------------------------------- Classes -------------------------------------------------------------
    PART_OF_SPEECH: str = f"{POS_STRUCTURES_NAMESPACE}PartOfSpeech"
    # -------------------------------------------- Properties ----------------------------------------------------------
    HAS_POS_ENTITY: str = f"hasPOSEntity"
    HAS_IS_PART_OF_POS_ENTITY: str = f"isPartOfPOSEntity"
    HAS_PART: str = f"hasPart"
    HAS_TAG: str = f"hasTag"


# ----------------------------------------------- Math structure -------------------------------------------------------
class MathStructureSchema(SegmentationSchema):
    """
    MathStructureSchema
    ===================
    The Math structure schema is used to represent the structure of mathematical expressions in the ink model.
    """
    MATH_STRUCTURE_VERSION: str = "0.1"
    MATH_STRUCTURES_NAMESPACE: str = f"will:math-structures/{MATH_STRUCTURE_VERSION}/"
    MATH_BLOCK_STRUCTURES: str = f"{MATH_STRUCTURES_NAMESPACE}MathBlock"
    # -------------------------------------------- Classes -------------------------------------------------------------
    MATH_BLOCK: str = f"{MATH_STRUCTURES_NAMESPACE}MathBlock"
    MATH_ITEM_GROUP: str = f"{MATH_STRUCTURES_NAMESPACE}MathItemGroup"
    MATH_ITEM: str = f"{MATH_STRUCTURES_NAMESPACE}MathItem"
    EXPRESSION_LIST: str = f"{MATH_STRUCTURES_NAMESPACE}ExpressionList"
    NUMBER: str = f"{MATH_STRUCTURES_NAMESPACE}Number"
    SYSTEM: str = f"{MATH_STRUCTURES_NAMESPACE}System"
    CASES: str = f"{MATH_STRUCTURES_NAMESPACE}Cases"
    RADICAL: str = f"{MATH_STRUCTURES_NAMESPACE}Radical"
    FENCE: str = f"{MATH_STRUCTURES_NAMESPACE}Fence"
    FRACTION: str = f"{MATH_STRUCTURES_NAMESPACE}Fraction"
    SUBSCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}Subscript"
    SUPERSCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}Superscript"
    SUB_SUPER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}SubSuperScript"
    PRE_SUPER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}PreSuperScript"
    PRE_SUB_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}PreSubScript"
    PRE_SUB_SUPER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}PreSubSuperScript"
    UNDER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}UnderScript"
    OVER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}OverScript"
    UNDER_OVER_SCRIPT: str = f"{MATH_STRUCTURES_NAMESPACE}UnderOverScript"
    ROW: str = f"{MATH_STRUCTURES_NAMESPACE}Row"
    ROW_LIST: str = f"{MATH_STRUCTURES_NAMESPACE}RowList"
    MATRIX: str = f"{MATH_STRUCTURES_NAMESPACE}Matrix"
    GROUP: str = f"{MATH_STRUCTURES_NAMESPACE}Group"
    OPERATION: str = f"{MATH_STRUCTURES_NAMESPACE}Operation"
    RELATION: str = f"{MATH_STRUCTURES_NAMESPACE}Relation"
    SYMBOL: str = f"{MATH_STRUCTURES_NAMESPACE}Symbol"
    MATHEMATICAL_TERM: str = f"{MATH_STRUCTURES_NAMESPACE}MathematicalTerm"
    UNIT: str = f"{MATH_STRUCTURES_NAMESPACE}Unit"
    OPERATOR_SYMBOL: str = f"{MATH_STRUCTURES_NAMESPACE}OperatorSymbol"
    RELATION_SYMBOL: str = f"{MATH_STRUCTURES_NAMESPACE}RelationSymbol"
    SEPARATOR: str = f"{MATH_STRUCTURES_NAMESPACE}Separator"
    DIGIT: str = f"{MATH_STRUCTURES_NAMESPACE}Digit"
    NUMBER_ITEM: str = f"{MATH_STRUCTURES_NAMESPACE}NumberItem"
    # -------------------------------------------- Properties ----------------------------------------------------------
    HAS_CHILD: str = f"hasChild"
    HAS_ENTITY_LABEL: str = f"hasEntityLabel"
    HAS_ENTITY_TYPE: str = f"hasEntityType"
    IS_STRUCTURAL_ENTITY: str = f"isStructuralEntity"
    IS_BASE_ENTITY: str = f"isBaseEntity"
    HAS_LATEX: str = f"hasLatex"
    HAS_MATHML: str = f"hasMathML"
    HAS_ASCII_MATH: str = f"hasASCIIMath"
    HAS_EXPRESSIONS: str = f"expressions"
    HAS_OPENING_BRACKET: str = f"openingBracket"
    HAS_CLOSING_BRACKET: str = f"closingBracket"
    HAS_INDEX: str = f"index"
    HAS_RADICAL_SYMBOL: str = f"radicalSymbol"
    HAS_RADICAND: str = f"radicand"
    HAS_BODY: str = f"body"
    HAS_NUMERATOR: str = f"numerator"
    HAS_DENOMINATOR: str = f"denominator"
    HAS_FRACTION_LINE: str = f"fractionLine"
    HAS_FRACTION_TYPE: str = f"fractionType"
    HAS_SUBSCRIPT: str = f"subScript"
    HAS_SUPERSCRIPT: str = f"superScript"
    HAS_PRE_SUPERSCRIPT: str = f"preSuperScript"
    HAS_PRE_SUBSCRIPT: str = f"preSubScript"
    HAS_UNDERSCRIPT: str = f"underScript"
    HAS_OVERSCRIPT: str = f"overScript"
    HAS_ROWS: str = f"rows"
    HAS_MATRIX_TYPE: str = f"matrixType"
    HAS_OPERATION_TYPE: str = f"operationType"
    HAS_REPRESENTATION: str = f"representation"
    HAS_SYMBOL_TYPE: str = f"symbolType"
    HAS_SEPARATOR_TYPE: str = f"separatorType"


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

    def __dict__(self):
        return {
            'statements': [s.__dict__() for s in self.__triple_statement]
        }

    def __iter__(self):
        return iter(self.__triple_statement)

    def __repr__(self):
        return f'<TripleStore : [statements:={self.__triple_statement}]>'

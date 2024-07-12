Module uim.model.semantics.schema
=================================

Classes
-------

`CommonRDF()`
:   Contains a list of used RDF types.

    ### Class variables

    `LOCALE: str`
    :

    `PRED_RDF_HAS_TYPE: str`
    :

`CommonViews(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Contains a list of known ink model views.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CUSTOM_TREE`
    :

    `HWR_VIEW`
    :

    `LEGACY_HWR_VIEW`
    :

    `LEGACY_NER_VIEW`
    :

    `MAIN_INK_TREE`
    :

    `MAIN_SENSOR_TREE`
    :

    `NER_VIEW`
    :

    `SEGMENTATION_VIEW`
    :

`MathSchema()`
:   MathSchema
    ==========
    The Math schema is used to represent mathematical expressions in the ink model.

    ### Ancestors (in MRO)

    * uim.model.semantics.schema.SegmentationSchema

    ### Class variables

    `BRACKETS: str`
    :

    `CLOSING_BRACKET: str`
    :

    `COMPOUND_TERM: str`
    :

    `EXPRESSION: str`
    :

    `FENCED: str`
    :

    `FRACTION: str`
    :

    `FRACTION_DENOMINATOR_PROP: str`
    :

    `FRACTION_LINE: str`
    :

    `FRACTION_NUMERATOR_PROP: str`
    :

    `FRACTION_TYPE_PROP: str`
    :

    `HAS_BRACKET: str`
    :

    `HAS_CHILD_PROP: str`
    :

    `HAS_CLOSING_BRACKET_PROP: str`
    :

    `HAS_FRACTION_OPERATOR_PROP: str`
    :

    `HAS_OPENING_BRACKET_PROP: str`
    :

    `HAS_OVERSCRIPT: str`
    :

    `HAS_PRESUBSCRIPT: str`
    :

    `HAS_PRESUPERSCRIPT: str`
    :

    `HAS_REPRESENTATION_PROP: str`
    :

    `HAS_SUBSCRIPT: str`
    :

    `HAS_SUPERSCRIPT: str`
    :

    `HAS_SYMBOL_TYPE: str`
    :

    `HAS_UNDERSCRIPT: str`
    :

    `INDEXED: str`
    :

    `ITEMS_PROP: str`
    :

    `LATEX_REPRESENTATION: str`
    :

    `MATHML_REPRESENTATION: str`
    :

    `MATH_BLOCK: str`
    :

    `MATH_NAMESPACE: str`
    :

    `MATH_SCHEMA_VERSION: str`
    :

    `MATRIX: str`
    :

    `MATRIX_ROW: str`
    :

    `MATRIX_ROW_CELL_PROP: str`
    :

    `MATRIX_ROW_PROP: str`
    :

    `NUMBER: str`
    :

    `NUMBER_TYPE_PROP: str`
    :

    `NUMERIC_REPRESENTATION_PROP: str`
    :

    `OPENING_BRACKET: str`
    :

    `OPERATOR: str`
    :

    `RELATION: str`
    :

    `ROOT: str`
    :

    `ROOT_DEGREE_PROP: str`
    :

    `ROOT_EXPRESSION_PROP: str`
    :

    `ROOT_SIGN_PROP: str`
    :

    `SYMBOL: str`
    :

    `SYSTEM: str`
    :

    `VERTICAL_FENCED: str`
    :

`MathStructureSchema()`
:   MathStructureSchema
    ===================
    The Math structure schema is used to represent the structure of mathematical expressions in the ink model.

    ### Ancestors (in MRO)

    * uim.model.semantics.schema.SegmentationSchema

    ### Class variables

    `BODY: str`
    :

    `DENOMINATOR: str`
    :

    `EXPRESSIONS: str`
    :

    `FRACTION_TYPE: str`
    :

    `HAS_ASCII_MATH: str`
    :

    `HAS_CHILD: str`
    :

    `HAS_ENTITY_LABEL: str`
    :

    `HAS_ENTITY_TYPE: str`
    :

    `HAS_EXPRESSIONS: str`
    :

    `HAS_LATEX: str`
    :

    `HAS_MATH_ML: str`
    :

    `INDEX: str`
    :

    `IS_BASE_ENTITY: str`
    :

    `IS_STRUCTURAL_ENTITY: str`
    :

    `MATH_BLOCK_STRUCTURES: str`
    :

    `MATH_ITEM: str`
    :

    `MATH_STRUCTURES_NAMESPACE: str`
    :

    `MATH_STRUCTURE_VERSION: str`
    :

    `MATRIX_TYPE: str`
    :

    `NUMERATOR: str`
    :

    `OPERATION_TYPE: str`
    :

    `OPERATOR_SYMBOL: str`
    :

    `RADICAL_SYMBOL: str`
    :

    `RADICAND: str`
    :

    `RELATION_SYMBOL: str`
    :

    `REPRESENTATION: str`
    :

    `ROW: str`
    :

    `ROWS: str`
    :

    `SEPARATOR_TYPE: str`
    :

    `STRUCTURES_CASES: str`
    :

    `STRUCTURES_DIGIT: str`
    :

    `STRUCTURES_EXPRESSION_LIST: str`
    :

    `STRUCTURES_FENCE: str`
    :

    `STRUCTURES_FRACTION: str`
    :

    `STRUCTURES_FRACTION_LINE: str`
    :

    `STRUCTURES_GROUP: str`
    :

    `STRUCTURES_MATHEMATICAL_TERM: str`
    :

    `STRUCTURES_MATRIX: str`
    :

    `STRUCTURES_NUMBER: str`
    :

    `STRUCTURES_NUMBER_ITEM: str`
    :

    `STRUCTURES_OPERATION: str`
    :

    `STRUCTURES_OVER_SCRIPT: str`
    :

    `STRUCTURES_PRE_SUB_SCRIPT: str`
    :

    `STRUCTURES_PRE_SUB_SUPER_SCRIPT: str`
    :

    `STRUCTURES_PRE_SUPER_SCRIPT: str`
    :

    `STRUCTURES_RADICAL: str`
    :

    `STRUCTURES_RELATION: str`
    :

    `STRUCTURES_ROW: str`
    :

    `STRUCTURES_ROW_LIST: str`
    :

    `STRUCTURES_SEPARATOR: str`
    :

    `STRUCTURES_SUBSCRIPT: str`
    :

    `STRUCTURES_SUB_SUPER_SCRIPT: str`
    :

    `STRUCTURES_SUPERSCRIPT: str`
    :

    `STRUCTURES_SYMBOL: str`
    :

    `STRUCTURES_SYSTEM: str`
    :

    `STRUCTURES_UNDER_OVER_SCRIPT: str`
    :

    `STRUCTURES_UNDER_SCRIPT: str`
    :

    `STRUCTURES_UNIT: str`
    :

    `SYMBOL_TYPE: str`
    :

`NamedEntityRecognitionSchema()`
:   NamedEntityRecognitionSchema
    ============================
    The Named Entity Recognition schema is used to recognize named entities in the ink model.

    ### Ancestors (in MRO)

    * uim.model.semantics.schema.SegmentationSchema

    ### Class variables

    `HAS_ABSTRACT: str`
    :

    `HAS_ARTICLE: str`
    :

    `HAS_ARTICLE_URL: str`
    :

    `HAS_CONFIDENCE: str`
    :

    `HAS_CREATION_DATE: str`
    :

    `HAS_IMAGE: str`
    :

    `HAS_LABEL: str`
    :

    `HAS_NAMED_ENTITY: str`
    :

    `HAS_ONTOLOGY_TYPE: str`
    :

    `HAS_PROVIDER: str`
    :

    `HAS_SOURCE: str`
    :

    `HAS_THUMB: str`
    :

    `HAS_TOPIC_ENTITY: str`
    :

    `HAS_TYPE: str`
    :

    `HAS_UNIQUE_ID: str`
    :

    `HAS_URI: str`
    :

    `NAMED_ENTITY: str`
    :

    `NER_SCHEMA: str`
    :

    `NER_SCHEMA_VERSION: str`
    :

`SegmentationSchema()`
:   SegmentationSchema
    ==================
    The segmentation schema is used to segment the content of the ink model.

    ### Descendants

    * uim.model.semantics.schema.MathSchema
    * uim.model.semantics.schema.MathStructureSchema
    * uim.model.semantics.schema.NamedEntityRecognitionSchema

    ### Class variables

    `BORDER: str`
    :

    `CHEMICAL_STRUCTURE: str`
    :

    `CHEMISTRY_BLOCK: str`
    :

    `CONNECTOR: str`
    :

    `CORRECTION: str`
    :

    `DIAGRAM: str`
    :

    `DIAGRAM_CONNECTOR: str`
    :

    `DIAGRAM_PART: str`
    :

    `DRAWING: str`
    :

    `DRAWING_ITEM: str`
    :

    `DRAWING_ITEM_GROUP: str`
    :

    `EXTENDED_TEXT_REGION: str`
    :

    `GARBAGE: str`
    :

    `GENERATED_BY: str`
    :

    `HAS_ALTERNATIVE: str`
    :

    `HAS_CONTENT: str`
    :

    `HAS_LANGUAGE: str`
    :

    `LINE: str`
    :

    `LIST: str`
    :

    `LIST_ITEM: str`
    :

    `LIST_ITEM_BODY: str`
    :

    `MARKING: str`
    :

    `MARKING_TYPE_ENCIRCLING: str`
    :

    `MARKING_TYPE_PREDICATE: str`
    :

    `MARKING_TYPE_UNDERLINING: str`
    :

    `MATH_BLOCK: str`
    :

    `MATH_ITEM: str`
    :

    `MATH_ITEM_GROUP: str`
    :

    `PART_OF_NAMED_ENTITY: str`
    :

    `PART_OF_POS_ENTITY: str`
    :

    `PHYSICS_BLOCK: str`
    :

    `REPRESENTS_VIEW: str`
    :

    `ROOT: str`
    :

    `SEGMENTATION_ROOT: str`
    :

    `SEGMENTATION_SCHEMA: str`
    :

    `SEGMENTATION_SCHEMA_VERSION: str`
    :

    `TABLE: str`
    :

    `TEXT_LINE: str`
    :

    `TEXT_REGION: str`
    :

    `UNLABELLED: str`
    :

    `UNLABELLED_BLOCK: str`
    :

    `UNLABELLED_ITEM: str`
    :

    `UNLABELLED_ITEM_GROUP: str`
    :

    `WORD: str`
    :

`SemanticTriple(subject: str, predicate: str, obj: str)`
:   SemanticTriple
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

    ### Instance variables

    `object: str`
    :   Object of the statement. (`str`)

    `predicate: str`
    :   Predicate of the statement. (`str`)

    `subject: str`
    :   Subject of the statement. (`str`)

`TripleStore(triple_statements: List[uim.model.semantics.schema.SemanticTriple] = None)`
:   TripleStore
    ===========
    
    Encapsulates a list of triple statements.
    
    Parameters
    ----------
    triple_statements: List[SemanticTriple]
        List of `SemanticTriple`s

    ### Instance variables

    `statements: List[uim.model.semantics.schema.SemanticTriple]`
    :   List of triple statements. (`List[SemanticTriple]`)

    ### Methods

    `add_semantic_triple(self, subject: str, predicate: str, obj: str)`
    :   Adding a semantic triple.
        
        Parameters
        ----------
        subject: `str`
            Subject of the statement
        predicate: `str`
            Predicate of the statement
        obj: `str`
            Object of the statement

    `all_statements_for(self, subject: str, predicate: str = None) ‑> List[uim.model.semantics.schema.SemanticTriple]`
    :   Returns all statements for a specific subject.
        
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

    `append(self, triple_statement: uim.model.semantics.schema.SemanticTriple)`
    :   Appending the triple statement.
        
        Parameters
        ----------
        triple_statement: SemanticTriple
            Triple that needs to be added

    `clear_statements(self)`
    :   Remove all statements.

    `determine_sem_type(self, node: InkNode, typedef_pred: str = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type') ‑> Optional[str]`
    :   Determine the Semantic Type of node.
        
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

    `filter(self, subject: Optional[str] = None, predicate: Optional[str] = None, obj: Optional[str] = None) ‑> List[uim.model.semantics.schema.SemanticTriple]`
    :   Returns all statements for a specific subject. The filter ares are optional, if not provided, all statements.
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

    `remove_semantic_triple(self, triple: uim.model.semantics.schema.SemanticTriple)`
    :   Removes a semantic triple from list.
        
        Parameters
        ----------
        triple: `SemanticTriple`
            Triple to be removed
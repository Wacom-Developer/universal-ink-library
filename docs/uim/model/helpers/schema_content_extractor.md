Module uim.model.helpers.schema_content_extractor
=================================================

Functions
---------

    
`uim_schema_semantics_from(ink_model: uim.model.ink.InkModel, semantic_view: str = 'hwr') ‑> List[Dict[str, Any]]`
:   Extract schema semantics from the ink model.
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
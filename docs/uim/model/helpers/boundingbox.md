Module uim.model.helpers.boundingbox
====================================

Functions
---------

    
`union(b0: uim.model.semantics.structures.BoundingBox, b1: uim.model.semantics.structures.BoundingBox)`
:   Union of two bounding boxes.
    
    Parameters
    ----------
    b0: BoundingBox
        Bounding box 1
    b1: BoundingBox
        Bounding box 1
    
    Returns
    -------
    union_box: BoundingBox
        Union bounding box

    
`union_all(bounds: List[uim.model.semantics.structures.BoundingBox]) ‑> uim.model.semantics.structures.BoundingBox`
:   Create union of all bounding boxes.
    
    Parameters
    ----------
    bounds: List[BoundingBox]
        List of bounding boxes
    
    Returns
    -------
    union: BoundingBox
        Union of all bounding boxes.
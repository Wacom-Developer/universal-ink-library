Module uim.model.semantics.structures
=====================================

Classes
-------

`BoundingBox(x: float, y: float, width: float, height: float)`
:   BoundingBox
    ===========
    Bounding boxes are represented as rectangle.
    Each rectangle is composed of a x, y coordinate representing the lower left point and the height and width.
    
    Parameters
    ----------
    x: float
        x-coordinate
    y: float
        y-coordinate
    width: float
        Width of the bounding box
    height: float
        Height of the bounding box

    ### Ancestors (in MRO)

    * abc.ABC

    ### Instance variables

    `height: float`
    :   Height of the bounding box. ('float', read-only)

    `width: float`
    :   Width of the bounding box. ('float', read-only)

    `x: float`
    :   X coordinate of the lower left x coordinate of the bounding box. ('float', read-only)

    `y: float`
    :   y coordinate of the lower left y coordinate of the bounding box. ('float', read-only)

    ### Methods

    `enclosing_bounding_box(self, bb: BoundingBox) ‑> uim.model.semantics.structures.BoundingBox`
    :   Enclosing bounding box.
        
        Parameters
        ----------
        bb: `BoundingBox`
            Other bounding box
        
        Returns
        -------
        bb: `BoundingBox`
            Enclosing bounding box
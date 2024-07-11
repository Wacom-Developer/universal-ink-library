Module uim.utils.matrix
=======================

Classes
-------

`Matrix4x4()`
:   Matrix4x4
    ==========
    Collection of helpers for matrices.
    
    Representation of a 4x4 affine matrix
    
        | m00  m01  m02  m03 |
        | m10  m11  m12  m13 |
        | m20  m21  m22  m23 |
        | m30  m31  m32  m33 |

    ### Ancestors (in MRO)

    * abc.ABC

    ### Static methods

    `create_scale(scale: float) ‑> List[List[float]]`
    :   Create a scale matrix.
        Parameters
        ----------
        scale: float
            Scale factor
        
        Returns
        -------
        List[List[float]]
            4x4 scale matrix

    `create_translation(translation: List[float]) ‑> List[List[float]]`
    :   Create a translation matrix.
        Parameters
        ----------
        translation: List[float]
            Translation vector
        
        Returns
        -------
        List[List[float]]
            4x4 translation matrix
        
        Raises
        ------
        ValueError
            Translation must be a 3D vector
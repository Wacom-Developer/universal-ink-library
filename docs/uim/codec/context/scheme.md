Module uim.codec.context.scheme
===============================

Classes
-------

`PrecisionScheme(mask_value: int = 0)`
:   PrecisionScheme
    ===============
    Contains information for the decimal precision of data in different channels.
    
    Parameters
    ----------
    mask_value: int (optional) [default: 0]
        Mask value which encodes the path precision.

    ### Class variables

    `OFFSET_SHIFT_BITS: int`
    :

    `POSITION_SHIFT_BITS: int`
    :

    `ROTATION_SHIFT_BITS: int`
    :

    `SCALE_SHIFT_BITS: int`
    :

    `SIZE_SHIFT_BITS: int`
    :

    ### Instance variables

    `offset_precision: int`
    :   Gets or sets the data precision for the Offset (OffsetX, OffsetY, OffsetZ) channels. (`int`, read-only)

    `position_precision: int`
    :   Gets or sets the data precision for position (X, Y, Z) channels. (`int`, read-only)

    `rotation_precision: int`
    :   Gets or sets the data precision for the Rotation channel. (`int`, read-only)

    `scale_precision: int`
    :   Gets or sets the data precision for the Scale (ScaleX, ScaleY, ScaleZ) channels. (`int`, read-only)

    `size_precision: int`
    :   Gets or sets the data precision for the Size channel. (`int`, read-only)

    `value: int`
    :   Value that encodes the bits. (`int`)
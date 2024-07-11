Module uim.codec.writer.encoder.encoder_3_1_0
=============================================

Classes
-------

`UIMEncoder310()`
:   UIMEncoder310
    =============
    Universal Ink Model. (v3.1.0)
    
    Formats the Universal Ink Model Data file codec.

    ### Ancestors (in MRO)

    * uim.codec.writer.encoder.base.CodecEncoder
    * uim.codec.writer.encoder.base.Codec
    * abc.ABC

    ### Class variables

    `CHUNK_SIZE: int`
    :

    `MAP_INK_METRICS_TYPE: dict`
    :

    `MAP_INPUT_PROVIDER: dict`
    :

    `MAP_ROTATION_MODE: dict`
    :

    `MAP_STATE_TYPE: dict`
    :

    `VERSION_MAJOR: bytes`
    :

    `VERSION_MINOR: bytes`
    :

    `VERSION_PATCH: bytes`
    :

    ### Methods

    `encode(self, ink_model: uim.model.ink.InkModel, *args, **kwargs) ‑> bytes`
    :   Formats input data document in the WILL 3.0 codec.
        Parameters
        ----------
        ink_model: InkModel
            InkModel object
        args: List[Any]
            Additional arguments
        
        Returns
        -------
        bytes
            Byte stream of the encoded data
        
        Raises
        ------
        InkModelException
            If the input data is not an InkModel object
        FormatException
            If the format is not matching the expected format
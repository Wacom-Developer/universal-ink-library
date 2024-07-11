Module uim.codec.writer.encoder.base
====================================

Classes
-------

`Codec()`
:   Codec
    =====
    Abstract codec encoder class.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * uim.codec.writer.encoder.base.CodecEncoder

    ### Methods

    `encode(self, ink_model: uim.model.ink.InkModel, *args, **kwargs) ‑> bytes`
    :   Encodes Ink Model object the chosen file codec.
        
        Parameters
        ----------
        ink_model: `InkModel`
            Universal Ink Model (memory model)
        args: List[Any]
            Additional arguments
        kwargs: dict
            Additional parameters
        
        Returns
        -------
        content - bytes
            File content encode in bytes UIM v3.1.0

`CodecEncoder()`
:   CodecEncoder
    ============
    Abstract content parser for the different versions of the Universal Ink Model (UIM).

    ### Ancestors (in MRO)

    * uim.codec.writer.encoder.base.Codec
    * abc.ABC

    ### Descendants

    * uim.codec.writer.encoder.encoder_3_1_0.UIMEncoder310
Module uim.codec.context.encoder
================================

Classes
-------

`EncoderContext(version: uim.codec.context.version.Version, ink_model: uim.model.ink.InkModel)`
:   EncoderContext
    ==============
    
    Context used while encoding an ink file.
    
    The context is used to store the state of the encoding process, such as the encoded strokes and the
    current state of the ink model.
    
    Parameters
    ----------
    version: `Version`
        Version of the ink file
    ink_model: `InkModel`
        Reference of the `InkModel` that will be encoded

    ### Static methods

    `view_name(view_name: str, target_format: uim.codec.parser.base.SupportedFormats) ‑> str`
    :   Depending on the target format the appropriate view name is chosen.
        
        Parameters
        ----------
        view_name: `str`
            Name of the view
        target_format: `SupportedFormats`
            Chosen target format
        
        Returns
        -------
            name - str
                Name of view depending on the format. UIM v3.1.0 and v3.0.0 have different conventions

    ### Instance variables

    `format_version: uim.codec.context.version.Version`
    :   Version of the format. (`Version`, read-only)

    `ink_model: uim.model.ink.InkModel`
    :   Current state of the ink model. (`InkModel`, read-only)

    `stroke_index_map: Dict[uuid.UUID, int]`
    :   Stroke index map. (`Dict[uuid.UUID, int]`, read-only)
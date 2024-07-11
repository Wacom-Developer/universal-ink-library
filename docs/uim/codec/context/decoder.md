Module uim.codec.context.decoder
================================

Classes
-------

`DecoderContext(version: uim.codec.context.version.Version, ink_model: uim.model.ink.InkModel)`
:   DecoderContext
    ==============
    Decoder Context used while parsing an ink file.
    
    The context is used to store the state of the parsing process, such as the parsed strokes
    and the current state of the ink model.
    
    Parameters
    ----------
    version: `Version`
        Version of the parsed ink file
    ink_model: `InkModel`
        Reference of the `InkModel` that will be available after parsing process is finished

    ### Instance variables

    `decoder_map: Dict[str, Any]`
    :   Map of the decoder. (`Dict[str, Any]`, read-only)

    `format_version: uim.codec.context.version.Version`
    :   Version of the format. (`Version`, read-only)

    `ink_model: uim.model.ink.InkModel`
    :   Current state of the ink model. (`InkModel`, read-only)

    `path_point_properties: List[uim.model.inkdata.strokes.PathPointProperties]`
    :   List of the path point properties. (`List[PathPointProperties]`, read-only)

    `strokes: List[uim.model.inkdata.strokes.Stroke]`
    :   List of the parsed strokes. (`List[Stroke]`, read-only)

    ### Methods

    `is_stroke_registered(self, identifier: str) ‑> bool`
    :   Check if a stroke is already registered.
        
        Parameters
        ----------
        identifier: str
            Identifier from a different format
        
        Returns
        -------
        bool
            True if the stroke is already registered

    `register_stroke(self, stroke: uim.model.inkdata.strokes.Stroke, stroke_identifier: str)`
    :   Register a stroke for the context.
        
        Parameters
        ----------
        stroke: `Stroke`
            Stroke structure
        stroke_identifier: str
            Identifier from a different format

    `stroke_by_identifier(self, identifier: str) ‑> uim.model.inkdata.strokes.Stroke`
    :   Retrieve stroke by using the registered identifier.
        
        Parameters
        ----------
        identifier: str
            Registered identifier
        
        Returns
        -------
        stroke - Stroke
            Stroke which is registered for identifier
        
        Raises
        ------
            ValueError
                if the identifier is not registered

    `upgrade_uris(self)`
    :   Upgrade the URIs for groups from UIM 3.0.0 to UIM 3.1.0.
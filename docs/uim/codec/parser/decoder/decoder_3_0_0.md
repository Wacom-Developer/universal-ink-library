Module uim.codec.parser.decoder.decoder_3_0_0
=============================================

Classes
-------

`UIMDecoder300()`
:   UIDecoder300
    ============
    
    The UIMDecoder300 decodes the Universal Ink Model v3.0.0 and maps it into the model for v3.1.0.
    
    References
    ----------
    [1]  Universal Ink Model documentation - URL https://developer-docs.wacom.com/sdk-for-ink/docs/model

    ### Ancestors (in MRO)

    * uim.codec.parser.decoder.base.CodecDecoder
    * abc.ABC

    ### Class variables

    `MAP_BLEND_MODE: Dict[int, uim.model.inkdata.brush.BlendMode]`
    :   Mapping for blending mode.

    `MAP_CHANNEL_TYPE: Dict[int, uim.model.inkinput.inputdata.InkSensorType]`
    :   Mapping for channel type.

    `MAP_INK_METRICS_TYPE: Dict[int, uim.model.inkinput.inputdata.InkSensorMetricType]`
    :   Mapping metric types from UIM v3.0.0 to internal enum.

    `MAP_INPUT_PROVIDER_TYPE: Dict[int, uim.model.inkinput.inputdata.InkInputType]`
    :   Mapping for input provider.

    `MAP_ROTATION_MODE: Dict[int, uim.model.inkdata.brush.RotationMode]`
    :

    `MAP_STATE_TYPE: Dict[int, uim.model.inkinput.sensordata.InkState]`
    :   Mapping of the uim input data states.

    ### Static methods

    `decode(riff: _io.BytesIO, size_head: int) ‑> uim.model.ink.InkModel`
    :   Decoding Universal Ink Model (RIFF / Protobuf encoded) content file.
        
        Parameters
        ----------
        riff: `BytesIO`
            RIFF content with encoded UIM v3.0.0 content.
        size_head: `int`
            Size of  the header
        
        Returns
        -------
            model - `InkModel`
                Parsed `InkModel` from UIM v3.0.0 ink content
        
        Raises
        ------
        FormatException
            Raised if the data header is missing.

    `decode_document(document: will_3_pb2.InkObject) ‑> uim.model.ink.InkModel`
    :   Decoding Protobuf content file.
        
        Parameters
        ----------
        document: `uim_3_0_0.InkObject`
            Parsed protobuf structure.
        
        Returns
        -------
            model - `InkModel`
                Parsed `InkModel` from UIM v3.0.0 ink content

    `decode_json(fp: <class 'BinaryIO'>) ‑> uim.model.ink.InkModel`
    :   Decoding Universal Ink Model (JSON Protobuf encoded) content file.
        
        Parameters
        ----------
        fp: `BinaryIO`
            JSON with encoded UIM v3.0.0 content.
        
        Returns
        -------
            model - `InkModel`
                Parsed `InkModel` from UIM v3.0.0 ink content
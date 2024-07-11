Module uim.codec.parser.decoder.decoder_3_1_0
=============================================

Classes
-------

`UIMDecoder310()`
:   UIModelDecoder310
    =================
    
    The UIMDecoder310 decodes the Universal Ink Model v3.1.0.
    
    References
    ----------
    [1]  Universal Ink Model documentation - URL https://developer-docs.wacom.com/sdk-for-ink/docs/model

    ### Ancestors (in MRO)

    * uim.codec.parser.decoder.base.CodecDecoder
    * abc.ABC

    ### Class variables

    `MAP_BLEND_MODE: Dict[int, uim.model.inkdata.brush.BlendMode]`
    :   Mapping of blend modes.

    `MAP_CHANNEL_TYPE: Dict[str, uim.model.inkinput.inputdata.InkSensorType]`
    :   Mapping of channel types.

    `MAP_CHUNK_TYPE: Dict[bytes, Any]`
    :   Mapping of the different chunk types.

    `MAP_COMPRESSION_TYPE: Dict[bytes, uim.codec.base.CompressionType]`
    :   Mapping of the `CompressionType`.

    `MAP_CONTENT_TYPE: Dict[bytes, uim.codec.base.ContentType]`
    :   Mapping of the `ContentType`.

    `MAP_INK_METRICS_TYPE: Dict[int, uim.model.inkinput.inputdata.InkSensorMetricType]`
    :   Mapping unit types.

    `MAP_INPUT_PROVIDER_TYPE: Dict[int, uim.model.inkinput.inputdata.InkInputType]`
    :   Mapping of input providers.

    `MAP_ROTATION_MODE: Dict[int, uim.model.inkdata.brush.RotationMode]`
    :   Map for rotation mode

    `MAP_STATE_TYPE: Dict[int, uim.model.inkinput.sensordata.InkState]`
    :   Mapping of the uim input data states.

    ### Static methods

    `decode(riff: _io.BytesIO, size_head: int)`
    :   Decoding Universal Ink Model (RIFF / Protobuf encoded) content file.
        
        Parameters
        ----------
        riff: `BytesIO`
            RIFF content with encoded UIM v3.1.0 content.
        size_head: `int`
            Size of  the header
        
        Returns
        -------
            model - `InkModel`
                Parsed `InkModel` from UIM v3.1.0 ink content

    `four_cc(content: bytes) ‑> Tuple[int, int, int, uim.codec.base.ContentType, uim.codec.base.CompressionType]`
    :   Parse the version information.
        
        Parameters
        ----------
        content: bytes
            RIFF bytes
        
        Returns
        -------
            chunk_major_version: int
                Major version of the file
            chunk_minor_version: int
                Minor version of the file
            chunk_patch_version: int
                Patch version of the file
            content_type: `ContentType`
                Content type of the file Protobuf, text, binary, ...
            compression_type: `CompressionType
                Type of compression used for encoding the content.

    `parse_brushes(context: uim.codec.context.decoder.DecoderContext, brushes: UIM_3_1_0_pb2.Brushes)`
    :   Parse brush definitions.
        
        Parameters
        ----------
        context: `DecoderContext`
            Decoder context
        brushes: `uim_3_1_0.Brushes`
            Protobuf structure for brushes

    `parse_ink_data(context: uim.codec.context.decoder.DecoderContext, ink_data: UIM_3_1_0_pb2.InkData)`
    :   Parse Protobuf structure and assign it to internal structure.
        
        Parameters
        ----------
        context: DecoderContext
            Decoder context
        ink_data: uim_3_1_0.InkData
            Protobuf structure for ink data

    `parse_ink_structure(context: uim.codec.context.decoder.DecoderContext, ink_structure: UIM_3_1_0_pb2.InkStructure)`
    :   Parse ink structure.
        
        Parameters
        ----------
        context: DecoderContext
            Decoder context
        ink_structure: uim_3_1_0.InkStructure
            Protobuf structure for ink structure

    `parse_input_data(context: uim.codec.context.decoder.DecoderContext, input_data: UIM_3_1_0_pb2.InputData)`
    :   Parse input data Protobuf structure and assign it to internal structure.
        
        Parameters
        ----------
        context: DecoderContext
            Decoder context
        input_data: uim_3_1_0.InputData
            Protobuf structure for input data (sensor data)s

    `parse_knowledge(context: uim.codec.context.decoder.DecoderContext, triple_store: UIM_3_1_0_pb2.TripleStore)`
    :   Parse TripleStore protobuf message and return `TripleStore` object.
        Parameters
        ----------
        context: DecoderContext
            Decoder context
        triple_store: TripleStore
            triple_store protobuf message 'TripleStore'

    `parse_properties(context: uim.codec.context.decoder.DecoderContext, properties: UIM_3_1_0_pb2.Properties)`
    :   Parse properties Protobuf structure and assign it to internal structure.
        
        Parameters
        ----------
        context: `DecoderContext`
            Decoder context
        properties: `uim_3_1_0.Properties`
            Protobuf structure for properties
Module uim.codec.base
=====================

Variables
---------

    
`BRUSHES_HEADER: bytes`
:   Bytes header for brushes chunk

    
`CHUNK_DESCRIPTION: int`
:   Size of each description chunk in UIM v3.1.0

    
`CHUNK_ID_BYTES_SIZE: int`
:   Size of the chunk id in UIM v3.1.0

    
`DATA_HEADER: bytes`
:   Data header string

    
`HEAD_HEADER: bytes`
:   Header string

    
`INK_DATA_HEADER: bytes`
:   Bytes header for ink data chunk

    
`INK_STRUCTURE_HEADER: bytes`
:   Bytes header for ink structure chunk

    
`INPUT_DATA_HEADER: bytes`
:   Bytes header for input data chunk

    
`KNOWLEDGE_HEADER: bytes`
:   Bytes header for knowledge graph chunk

    
`PADDING: bytes`
:   Padding byte

    
`PROPERTIES_HEADER: bytes`
:   Bytes header for properties chunk

    
`RESERVED: bytes`
:   Reserved byte

    
`RIFF_HEADER: bytes`
:   RIFF header string

    
`SIZE_BYTE_SIZE: int`
:   Size of the size bytes in UIM v3.1.0

    
`UIM_HEADER: bytes`
:   Universal Ink Model file header.

Classes
-------

`CompressionType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   CompressionType
    ===============
    Enum of RIFF chunk supported compression types.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `LZMA`
    :   LZMA compression for particular chunk

    `NONE`
    :   Compression not applied

    `ZIP`
    :   ZIP compression for particular chunk

`ContentType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   "
    ContentType
    ===========
    Enum of RIFF chunk content types.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `BINARY`
    :   Binary encoding of content, binary/octet-stream.

    `JSON`
    :   JSON encoding of content, application/json.

    `PROTOBUF`
    :   Protobuf encoding of content, application/protobuf.

    `TEXT`
    :   Text encoding of content, text/plain.

`FileExtension()`
:   FileExtension
    =============
    File extension of ink content files.
    
    The file extensions are:
    - JSON
    - UIM JSON
    - UIM binary
    - InkML
    - WILL

    ### Class variables

    `INKML_FORMAT_EXTENSION: str`
    :   InkML encoding.

    `JSON_FORMAT_EXTENSION: str`
    :   JSON file encoding.

    `UIM_BINARY_FORMAT_EXTENSION: str`
    :   UIM binary encoding.

    `UIM_JSON_FORMAT_EXTENSION: str`
    :   UIM JSON file encoding.

    `WILL_FORMAT_EXTENSION: str`
    :   Wacom Ink Layer Language (WILL) file encoding.

`MimeTypes()`
:   MimeTypes
    =========
    Mime types for ink formats.
    
    The mime types are:
    - Universal Ink Model
    - WILL 3 documents
    - WILL 2 documents
    - WILL 2 strokes

    ### Class variables

    `UNIVERSAL_INK_MODEL: str`
    :

    `WILL2_FILE_FORMAT: str`
    :

    `WILL2_STROKES_FORMAT: str`
    :
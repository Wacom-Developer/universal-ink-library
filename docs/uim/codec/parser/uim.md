Module uim.codec.parser.uim
===========================

Classes
-------

`UIMParser()`
:   UIMParser
    =========
    
    Parser for Universal Ink Model data codec (UIM).
    The parser is able to parse UIM files in version 3.0.0 and 3.1.0.
    
    Examples
    --------
    >>> from uim.codec.parser.uim import UIMParser
    >>> from uim.model.ink import InkModel
    >>> parser: UIMParser = UIMParser()
    >>> ink_model: InkModel = parser.parse('../ink/uim_3.1.0/5) Cell Structure 1 (3.1 delta).uim')
    
    See also
    --------
    ´WILL2Parser´ - Parser for WILL files

    ### Ancestors (in MRO)

    * uim.codec.parser.base.Parser
    * abc.ABC

    ### Static methods

    `parse_json(path: Union[str, pathlib.Path]) ‑> uim.model.ink.InkModel`
    :   Parse ink file from either a `Path`, `str`.
        
        Parameters
        ----------
        path: Union[str, Path]
            Location of the JSON file
        
        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream
        
        Raises
        ------
        ValueError
            Raises if path is not a `str` or `Path`
        FormatException
            Raises if file does not exist.

    ### Methods

    `parse(self, path_or_stream: Union[str, bytes, memoryview, _io.BytesIO, pathlib.Path]) ‑> uim.model.ink.InkModel`
    :   Parse the Universal Ink Model codec.
        
        Parameters
        ----------
        path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]
            `Path` of file, path as str, stream, or byte array.
        
        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream
        
        Raises
        ------
        FormatException
            Raises if the file is not an UIM file.
        TypeError
            Raises if the type is not supported.
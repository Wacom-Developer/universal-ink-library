Module uim.codec.parser.base
============================

Classes
-------

`EndOfStream(*args, **kwargs)`
:   EndOfStream
    ===========
    
    Exception thrown whenever the end of the stream has been reached.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`FormatException(*args, **kwargs)`
:   FormatException
    ===============
    Exception thrown while parsing ink files.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

`Parser()`
:   Parser
    ======
    
    Parser is responsible to parse an ink file .

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * uim.codec.parser.uim.UIMParser
    * uim.codec.parser.will.WILL2Parser

    ### Methods

    `parse(self, path_or_stream: Union[str, bytes, memoryview, _io.BytesIO, pathlib.Path]) ‑> InkModel`
    :   Parse the content of the ink file to the Universal Ink memory model.
        
        Parameters
        ----------
        path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]
            `Path` of file, path as str, stream, or byte array.
        
        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream

`Stream(stream: bytes)`
:   Stream
    ======
    
    Stream class to read bytes from byte array.
    
    Parameters
    ----------
    stream: bytes
        Content byte arrays

    ### Methods

    `read(self, num: int) ‑> Union[bytes, int]`
    :   Read bytes from byte array.
        Parameters
        ----------
        num: int
            Number of bytes to be read
        
        Returns
        -------
            value: Union[bytes, int]
        Raises
        ------
        EndOfStream
            Raised if the end of the stream has been reached

`SupportedFormats(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   SupportedFormats
    ================
    Supported formats enum.
    All formats that are currently support by the library.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `INKML_VERSION: uim.codec.context.version.Version`
    :

    `NOT_SUPPORTED: uim.codec.context.version.Version`
    :

    `UIM_VERSION_3_0_0: uim.codec.context.version.Version`
    :

    `UIM_VERSION_3_1_0: uim.codec.context.version.Version`
    :

    `WILL_DATA_VERSION_2_0_0: uim.codec.context.version.Version`
    :

    `WILL_FILE_VERSION_2_0_0: uim.codec.context.version.Version`
    :
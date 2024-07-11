Module uim.codec.context.version
================================

Classes
-------

`Version(major: int, minor: int, patch: int, ink_format: str = 'Unknown')`
:   Version
    =======
    Version encodes the semantic versioning concept a version number MAJOR.MINOR.PATCH, increment the:
    
    Parameters
    ----------
    major: int
        Major encodes the MAJOR version number. This number is incremented when you make incompatible API changes.
    minor: int
        Minor encodes the MINOR version number. This number is incremented when you add functionality in a backwards
        compatible manner.
    patch: int
        Patch encodes the version number. This number is incremented when you make backwards compatible bug fixes.
    ink_format: str
        String that defines the identifier string for the format that is related to the version.
    
    References
    ----------
    .. [1] Semantic Versioning 2.0.0 URL https://semver.org/

    ### Instance variables

    `ink_format: str`
    :   Version is associated to this format. (`str`)

    `major: int`
    :   MAJOR version. (`int`, read-only)

    `minor: int`
    :   MINOR version.  (`int`, read-only)

    `patch: int`
    :   PATCH version. (`int`, read-only)
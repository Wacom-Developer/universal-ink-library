Module uim.model.helpers.serialize
==================================

Functions
---------

    
`json_encode(obj: Union[uim.model.base.Identifier, uim.model.ink.InkModel, uim.model.inkinput.inputdata.InputContextRepository, uim.model.ink.SensorDataRepository, uim.model.inkdata.brush.Brushes, uim.model.inkdata.strokes.Style, uim.model.semantics.node.StrokeFragment], indent: int = 4) ‑> str`
:   Encodes the given object to a JSON string.
    
    Parameters
    ----------
    obj: `Identifier`
        Object to encode
    indent: int
        Indentation
    
    Returns
    -------
    str
        JSON string

    
`serialize_json(ink_model: uim.model.ink.InkModel, path: pathlib.Path)`
:   Serialize the ink model to a JSON file.
    
    Parameters
    ----------
    ink_model: InkModel
        Ink model
    path: Path
        Path to save the JSON file

    
`serialize_sensor_data_csv(ink_model: uim.model.ink.InkModel, path: pathlib.Path, layout: Optional[List[uim.model.inkdata.strokes.InkStrokeAttributeType]] = None, policy: uim.model.helpers.policy.HandleMissingDataPolicy = HandleMissingDataPolicy.FILL_WITH_ZEROS, delimiter: str = ',')`
:   Serialize the sensor data to a CSV file.
    
    Parameters
    ----------
    ink_model: InkModel
        Ink model
    path: Path
        Path to save the CSV file
    layout: List[InkStrokeAttributeType]
        Layout of the CSV file
    policy: HandleMissingDataPolicy
        Policy to handle missing data
    delimiter: str
        Delimiter

Classes
-------

`UniversalInkModelEncoder(*, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, sort_keys=False, indent=None, separators=None, default=None)`
:   UniversalInkModelEncoder
    ========================
    Universal Ink Model Encoder is a JSONEncoder that can be used to serialize
    
    Constructor for JSONEncoder, with sensible defaults.
    
    If skipkeys is false, then it is a TypeError to attempt
    encoding of keys that are not str, int, float or None.  If
    skipkeys is True, such items are simply skipped.
    
    If ensure_ascii is true, the output is guaranteed to be str
    objects with all incoming non-ASCII characters escaped.  If
    ensure_ascii is false, the output can contain non-ASCII characters.
    
    If check_circular is true, then lists, dicts, and custom encoded
    objects will be checked for circular references during encoding to
    prevent an infinite recursion (which would cause an OverflowError).
    Otherwise, no such check takes place.
    
    If allow_nan is true, then NaN, Infinity, and -Infinity will be
    encoded as such.  This behavior is not JSON specification compliant,
    but is consistent with most JavaScript based encoders and decoders.
    Otherwise, it will be a ValueError to encode such floats.
    
    If sort_keys is true, then the output of dictionaries will be
    sorted by key; this is useful for regression tests to ensure
    that JSON serializations can be compared on a day-to-day basis.
    
    If indent is a non-negative integer, then JSON array
    elements and object members will be pretty-printed with that
    indent level.  An indent level of 0 will only insert newlines.
    None is the most compact representation.
    
    If specified, separators should be an (item_separator, key_separator)
    tuple.  The default is (', ', ': ') if *indent* is ``None`` and
    (',', ': ') otherwise.  To get the most compact JSON representation,
    you should specify (',', ':') to eliminate whitespace.
    
    If specified, default is a function that gets called for objects
    that can't otherwise be serialized.  It should return a JSON encodable
    version of the object or raise a ``TypeError``.

    ### Ancestors (in MRO)

    * json.encoder.JSONEncoder

    ### Methods

    `default(self, obj: Any)`
    :   Implement this method in a subclass such that it returns
        a serializable object for ``o``, or calls the base implementation
        (to raise a ``TypeError``).
        
        For example, to support arbitrary iterators, you could
        implement default like this::
        
            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                # Let the base class default method raise the TypeError
                return JSONEncoder.default(self, o)
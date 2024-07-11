Module uim.model.helpers.text_extractor
=======================================

Functions
---------

    
`uim_extract_text_and_semantics(uim_bytes: bytes, hwr_view: str = 'hwr') ‑> tuple`
:   Extracting the text from Universal Ink Model.
    
    Parameters
    ----------
    uim_bytes: `bytes`
        Byte array with RIFF file from Universal Ink Model
    hwr_view: `str`
       HWR view.
    
    Returns
    -------
    text: `List[dict]`
        List of text lines. Each line has its own dict containing the  bounding box, and all words
    entities.
    
    Raises
    ------
        `InkModelException`
            If the Universal Ink Model does not contain the view with the requested view name.

    
`uim_extract_text_and_semantics_from(ink_model: uim.model.ink.InkModel, hwr_view: str = 'hwr') ‑> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]], str]`
:   Extracting the text from Universal Ink Model.
    
    Parameters
    ----------
    ink_model: InkModel
        Universal Ink Model
    hwr_view: str
       Name of the HWR view.
    
    Returns
    -------
    words: `List[dict]`
        List of words. Each word has its own dict containing the text, bounding box, and all alternatives.
    entities: `Dict[str, List[dict]]`
        Dictionary of entities. Each entity has its own dict containing the label, instance, and path ids.
    text: `str`
        Text extracted from the Universal Ink Model.
    
    Raises
    ------
        `InkModelException`
            If the Universal Ink Model does not contain the view with the requested view name.
    
     Examples
    --------
    >>> from pathlib import Path
    >>> from typing import Dict, Any
    >>> from uim.codec.parser.uim import UIMParser
    >>> from uim.model.helpers.text_extractor import uim_extract_text_and_semantics_from
    >>> path: Path = Path('ink_3_1_0.uim')
    >>> parser: UIMParser = UIMParser()
    >>> ink_model: InkModel = parser.parse(path)
    >>> words, entities, text = uim_extract_text_and_semantics_from(ink_model, CommonViews.HWR_VIEW.value)
    >>> for word in words:
    >>>     print(f"[text]: {word['text']}")
    >>>     print(f"[alternatives]: {'|'.join(word['alternatives'])}")
    >>>     print(f"[path ids]: {word['path_id']}")
    >>>     print(f"[word URI]: {word['word-uri']}")
    >>>     print(f"[bounding box]: x: {word['bounding_box']['x']}, y: {word['bounding_box']['y']}, "
    >>>           f"width: {word['bounding_box']['width']}, height: {word['bounding_box']['height']}")
    >>> for entity_uri, entity_hits in entities.items():
    >>>     print(f"[entity URI]: {entity_uri}")
    >>>     for entity in entity_hits:
    >>>         print(f"[entity]: {entity}")
    >>>         print(f"[path ids]: {entity['path_id']}")
    >>>         print(f"[instance]: {entity['instance']}")
    >>>         print(f"[provider]: {entity['provider']}")
    >>>         print(f"[uri]: {entity['uri']}")
    >>>         print(f"[image]: {entity['image']}")
    >>>         print(f"[description]: {entity['description']}")
    >>>         print(f"[label]: {entity['label']}")
    >>>         print(f"[bounding box]: x: {entity['bounding_box']['x']}, y: {entity['bounding_box']['y']}, "
    >>>               f"width: {entity['bounding_box']['width']}, height: {entity['bounding_box']['height']}")
    >>> print(f"[text]: {text}")
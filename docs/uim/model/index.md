Module uim.model
================
Package for the UIM model.
This package contains the data model for the UIM.

Sub-modules
-----------
* uim.model.base
* uim.model.helpers
* uim.model.ink
* uim.model.inkdata
* uim.model.inkinput
* uim.model.semantics

Classes
-------

`UUIDIdentifier(identifier: uuid.UUID)`
:   UUID Identifier
    ===============
    Identifier based on UUID.
    
    Parameters
    ----------
    identifier: `UUID`
        Identifier

    ### Ancestors (in MRO)

    * uim.model.base.Identifier
    * abc.ABC

    ### Descendants

    * uim.model.inkdata.strokes.Stroke
    * uim.model.inkinput.sensordata.ChannelData
    * uim.model.inkinput.sensordata.SensorData
    * uim.model.semantics.node.InkNode

    ### Class variables

    `SEPARATOR: str`
    :

    ### Static methods

    `id_generator() ‑> uuid.UUID`
    :   UUID generator function.
        
        Returns
        -------
        random: UUID
            Random generated UUID
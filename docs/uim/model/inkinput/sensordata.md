Module uim.model.inkinput.sensordata
====================================

Classes
-------

`ChannelData(sensor_channel_id: uuid.UUID, values: Optional[List[Union[float, int]]] = None)`
:   ChannelData
    ===========
    
    List of data items.
    
    Parameters
    ----------
    sensor_channel_id: `uuid.UUID`
        The sensor channel id.
    values:Optional[List[Union[float, int]]] (optional) [default: None]
        List of values. If not provided, an empty list is created.

    ### Ancestors (in MRO)

    * uim.model.base.UUIDIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `values: List[Union[float, int]]`
    :   Sample values delta encoded with provided precision. (List[Union[float, int]])

`InkState(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   InkState
    =========
     The Universal Ink Model (UIM) input data state defines the state of the Ink input data.
     UIM supports different modes:
    
       - Writing on a plane,
       - Hovering above a surface,
       - Moving in air (VR/AR/MR) interaction,
       - Only hovering in the air.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `HOVERING`
    :

    `IN_VOLUME`
    :

    `PLANE`
    :

    `START_TRACKING`
    :

    `STOP_TRACKING`
    :

    `VOLUME_HOVERING`
    :

`SensorData(sid: Optional[uuid.UUID] = None, input_context_id: Optional[uuid.UUID] = None, state: Optional[uim.model.inkinput.sensordata.InkState] = None, timestamp: Optional[int] = None)`
:   SensorData
    ==========
    The SensorData Repository is a data repository, which holds a collection of SensorData instances.
    
    A data-frame structure represents a collection of raw input data sequences, produced by one or more on-board
    device sensors, including data points, re-sampling information, and input sources from fingerprints and metadata.
    
    Remark:
    --------
    Once a SensorData instance is added to the SensorData repository, it is considered immutable.
    
    Parameters
    ----------
    sid: Optional[uuid.UUID] (optional) [default: None]
        Sensor data identifier.
    input_context_id: Optional[uuid.UUID] (optional) [default: None]
        Referencing the InputContext via id.
    state: Optional[InkState] (optional) [default: None]
        The state of the input provider during the capturing of this data frame.
    timestamp: Optional[int] (optional) [default: None]
        Timestamp for first sample of the stroke, measured in milliseconds.

    ### Ancestors (in MRO)

    * uim.model.base.UUIDIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `data_channels: List[uim.model.inkinput.sensordata.ChannelData]`
    :   List of the different channels. (List[ChannelData], read-only)

    `input_context_id: uuid.UUID`
    :   Id of the input context. (UUID)

    `state: uim.model.inkinput.sensordata.InkState`
    :   State of the uim sensor sequence. (InkState, read-only)

    `timestamp: int`
    :   Timestamp of the first data sample in this sequence. (int, read-only)

    ### Methods

    `add_data(self, sensor_channel: uim.model.inkinput.inputdata.SensorChannel, values: List[float])`
    :   Adding data to sensor channel.
        
        Parameters
        ----------
        sensor_channel: SensorChannel
            Sensor channel.
        values: List[float]
            List of values.

    `add_timestamp_data(self, sensor_channel: uim.model.inkinput.inputdata.SensorChannel, values: List[float])`
    :   Adding timestamp data.
        
        Parameters
        ----------
        sensor_channel: SensorChannel
            Sensor channel.
        values: List[float]
            List of values.
        
        Raises
        ------
        ValueError:
            Issue with the parameter

    `get_data_by_id(self, channel_id: uuid.UUID) ‑> uim.model.inkinput.sensordata.ChannelData`
    :   Returns data channel.
        
        Parameters
        ----------
        channel_id: `uuid.UUID`
            The sensor channel id.
        Returns
        -------
        ChannelData
            The channel data.
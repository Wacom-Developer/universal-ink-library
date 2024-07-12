Module uim.model.inkinput.inputdata
===================================

Variables
---------

    
`CONVERSION_SCALAR`
:   Mapping containing the factors to convert from one unit: <source-unit> into the other: <target-unit>.

Functions
---------

    
`si_unit(unit_type: uim.model.inkinput.inputdata.Unit) ‑> uim.model.inkinput.inputdata.Unit`
:   Return the SI unit for a specific unit type.
    
    Parameters
    ----------
    unit_type: `Unit`
        Unit
    
    Returns
    -------
    si_unit: Unit
        SI unit for a unit, e.g., for a lengths unit cm the SI unit is m.

    
`unit2unit(source_unit: uim.model.inkinput.inputdata.Unit, target_unit: uim.model.inkinput.inputdata.Unit, value: float) ‑> float`
:   Convert value with a source unit to the target unit.
    
    Parameters
    ----------
    source_unit: Unit
        Source unit
    target_unit: Unit
        Target unit
    value: float
        Value in source unit
    
    Returns
    -------
    value: `float`
        value converted to target unit
    
    Raises
    ------
    ValueError:
        Unit is not supported

    
`unit2unit_matrix(source_unit: uim.model.inkinput.inputdata.Unit, target_unit: uim.model.inkinput.inputdata.Unit) ‑> <built-in function array>`
:   Matrix for unit 2 unit conversion.
    
    Parameters
    ----------
    source_unit: Unit
        Source unit
    target_unit: Unit
        Target unit
    
    Returns
    -------
        matrix: `np.array`
            matrix for conversion

    
`virtual_resolution_for_si_unit(source_unit: uim.model.inkinput.inputdata.Unit) ‑> float`
:   Calculate a virtual resolution for source unit.
    
    Parameters
    ----------
    source_unit: unit
        Source unit
    Returns
    -------
    resolution: `float`
        Virtual resolution

Classes
-------

`DataType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   DataType
    ========
    Data types for channels.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `BOOLEAN`
    :

    `FLOAT32`
    :

    `FLOAT64`
    :

    `INT32`
    :

    `INT64`
    :

    `UINT32`
    :

    `UINT64`
    :

`Environment(env_id: Optional[uuid.UUID] = None, properties: Optional[List[Tuple[str, str]]] = None)`
:   Environment
    ===========
    The class `Environment` represents for the virtual environment in which the sensor data has been produced, e.g.,:
    
        - os.name - Name of the operating system
        - os.version.name - Name of the version
        - os.version.release - Release build number
        - wacom.ink.sdk.name - Name of the Wacom Ink technology
        - wacom.ink.sdk.version - Version number of the SDK
    
    Parameters
    ----------
    env_id: Optional[uuid.UUID] (optional) [default: None]
        Internal environment UUID
    properties: List[Tuple[str, str]]
        Properties of the environment
    
    Examples
    --------
    >>> from uim.model.inkinput.inputdata import Environment
    >>> # Create an environment
    >>> env: Environment = Environment()
    >>> env.properties.append(("env.name", "My Environment"))
    >>> env.properties.append(("os.id", "98765"))
    >>> env.properties.append(("os.name", "Windows"))
    >>> env.properties.append(("os.version", "10.0.18362.239"))
    >>> env.properties.append(("os.build", "239"))
    >>> env.properties.append(("os.platform", "whatever"))

    ### Ancestors (in MRO)

    * uim.model.base.HashIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `properties: List[Tuple[str, str]]`
    :   Environment properties. (`List[Tuple[str, str]]`)

    ### Methods

    `add_environment_property(self, key: str, value: str)`
    :   Adding a property for environment.
        
        Parameters
        ----------
        key: str
            Name of the property
        value: str
            Value of the property

`InkInputProvider(provider_id: Optional[uuid.UUID] = None, input_type: Optional[uim.model.inkinput.inputdata.InkInputType] = None, properties: Optional[List[Tuple[str, str]]] = None)`
:   InkInputProvider
    ================
    The class InkInputProvider stands for the generic input data source - it identifies how the data has been generated
    (using touch input, mouse, stylus, hardware controller, etc.).
    
    The properties which can be used to describe the InkInputProvider:
    
        - pen.type - Type of the pen device
    
    Parameters
    ----------
    provider_id: Optional[UUID] (optional) [default: None]
        internal id or input data name.
    input_type: InkInputType -
        type of used hardware - PEN, TOUCH, MOUSE, or CONTROLLER.
    properties: List[Tuple[str, str]] -
        Properties assigned to ink input provider
    
    Examples
    --------
    >>> from uim.model.inkinput.inputdata import InkInputProvider
    >>> # Ink input provider can be pen, mouse or touch.
    >>> provider: InkInputProvider = InkInputProvider(input_type=InkInputType.MOUSE)
    >>> provider.properties.append(("pen.id", "1234567"))

    ### Ancestors (in MRO)

    * uim.model.base.HashIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `properties: List[Tuple[str, str]]`
    :   Properties of input data provider. (`List[Tuple[str, str]]`, read-only)

    `type: uim.model.inkinput.inputdata.InkInputType`
    :   Input provider type. (`InkInputType`,  read-only)

`InkInputType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   InkInputType
    ============
    Defining the different types of input data.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CONTROLLER`
    :   3-DOF or 6-DOF input data devices.

    `MOUSE`
    :   Mouse input data.

    `PEN`
    :   Stylus, smart pens, pen displays, signature capturing input data, ...

    `TOUCH`
    :   Touch controller input data: Finger or passive stylus.

`InkSensorMetricType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   InkSensorMetricType
    ===================
    Metric for the channel.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ANGLE`
    :   Angle; underling si unit is radian

    `FORCE`
    :   Force; underling si unit is newton

    `LENGTH`
    :   Length; underling si unit is meter

    `NORMALIZED`
    :   Normalized; percentage, expressed as a fraction(1.0 = 100 %) relative to max - min

    `TIME`
    :   Time; underling  si unit is second

`InkSensorType(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   InkSensorType
    =============
    Pre-defined SensorData types.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `ALTITUDE`
    :   Elevation angle of the pen (pitch)

    `AZIMUTH`
    :   Azimuth angle of the pen (yaw)

    `PRESSURE`
    :   Input pressure.

    `RADIUS_X`
    :   Touch radius by X

    `RADIUS_Y`
    :   Touch radius by Y

    `ROTATION`
    :   Rotation (counter-clockwise rotation about pen axis)

    `TIMESTAMP`
    :   Time (of the sample point)

    `X`
    :   X coordinate. This is the horizontal pen position on the writing surface.

    `Y`
    :   Y coordinate. This is the vertical position on the writing surface.

    `Z`
    :   Z coordinate. This is the height of pen above the writing surface.

`InputContext(ctx_id: Optional[uuid.UUID] = None, environment_id: Optional[uuid.UUID] = None, sensor_context_id: Optional[uuid.UUID] = None)`
:   InputContext
    ============
    Capturing context of the uim input data with reference to the Environment and the SensorContext.
    
    Parameters
    ----------
    ctx_id: Optional[uuid.UUID] (optional) [default: None]
        Internal id
    environment_id: Optional[uuid.UUID] (optional) [default: None]
        Reference to environment
    sensor_context_id: Optional[uuid.UUID] (optional) [default: None]
        Rendering to sensor context

    ### Ancestors (in MRO)

    * uim.model.base.HashIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `environment_id: Optional[uuid.UUID]`
    :   Reference to environment. (`UUID`, read-only)

    `sensor_context_id: Optional[uuid.UUID]`
    :   Reference for sensor context. (`UUID`, read-only)

`InputContextRepository(input_contexts: Optional[List[uim.model.inkinput.inputdata.InputContext]] = None, ink_input_providers: Optional[List[uim.model.inkinput.inputdata.InkInputProvider]] = None, input_devices: Optional[List[uim.model.inkinput.inputdata.InputDevice]] = None, environments: Optional[List[uim.model.inkinput.inputdata.Environment]] = None, sensor_contexts: Optional[List[uim.model.inkinput.inputdata.SensorContext]] = None)`
:   InputContext Repository
    =======================
    
    The InputContext Repository is a data repository responsible for storing information about where the raw input
    data-frame originates from, by allowing unique identification of the exact input source. The repository stores
    information about the device itself, the environment and the on-board device sensors for each data point.
    
    The repository holds the following data collections:
    
        - **ink_input_providers** - a collection of InkInputProvider instances
        - **input_devices** - a collection of InputDevice instances
        - **environments** - a collection of Environment instances
        - **sensor_contexts** - a collection of SensorContext instances
        - **input_contexts** - a collection of InputContext instances
        
    Parameters
    ----------
    input_contexts: Optional[List[InputContext]] (optional) [default: None]
        List of input data contexts
    ink_input_providers: Optional[List[InkInputProvider]] (optional) [default: None]
        List of input data providers
    input_devices: Optional[List[InputDevice]] (optional) [default: None]
        List of input data devices
    environments: Optional[List[Environment]] (optional) [default: None]
        List of environment setups
    sensor_contexts: Optional[List[SensorContext]] (optional) [default: None]
        List of sensor contexts

    ### Ancestors (in MRO)

    * abc.ABC

    ### Instance variables

    `devices: List[uim.model.inkinput.inputdata.InputDevice]`
    :   Input devices. (`List[InputDevice]`)

    `environments: List[uim.model.inkinput.inputdata.Environment]`
    :   List of Environments. (`List[Environment]`)

    `ink_input_providers: List[uim.model.inkinput.inputdata.InkInputProvider]`
    :   List of `InkInputProvider`s. (`List[InkInputProvider]`)

    `input_contexts: List[uim.model.inkinput.inputdata.InputContext]`
    :   List of input contexts. (`List[InputContext]`)

    `sensor_contexts: List[uim.model.inkinput.inputdata.SensorContext]`
    :   List of SensorContexts. (`List[SensorContext]`)

    ### Methods

    `add_environment(self, environment: uim.model.inkinput.inputdata.Environment)`
    :   Adding environment.
        
        Parameters
        ----------
        environment: Environment
            Environment instance

    `add_ink_device(self, ink_device: uim.model.inkinput.inputdata.InputDevice)`
    :   Adding input device.
        
        Parameters
        ----------
        ink_device: `InputDevice`
            Adds an input device

    `add_input_context(self, input_context: uim.model.inkinput.inputdata.InputContext)`
    :   Adding context.
        
        Parameters
        ----------
        input_context: `InputContext`
            Input context instance

    `add_input_provider(self, input_provider: uim.model.inkinput.inputdata.InkInputProvider)`
    :   Adding input data provider.
        
        Parameters
        ----------
        input_provider: `InkInputProvider`
            Input data provider instance

    `add_sensor_context(self, sensor_context: uim.model.inkinput.inputdata.SensorContext)`
    :   Adding sensor context.
        
        Parameters
        ----------
        sensor_context: `SensorContext`
            Instance of `SensorContext`

    `get_input_context(self, ctx_id: uuid.UUID) ‑> uim.model.inkinput.inputdata.InputContext`
    :   Returns the InputContext.
        
        Parameters
        ----------
        ctx_id: `UUID`
            Input context id
        
        Returns
        -------
        context: InputContext
            Input  context
        
        Raises
        ------
        InkModelException
            If the `InputContext` for the id is not available.

    `get_input_device(self, device_id: uuid.UUID) ‑> uim.model.inkinput.inputdata.InputDevice`
    :   Returns the InputDevice.
        
        Parameters
        ----------
        device_id: `UUID`
            Input device id
        
        Returns
        -------
        context: InputDevice
            Input  device
        
        Raises
        ------
        InkModelException
            If the `InputDevice` for the id is not available.

    `get_sensor_context(self, ctx_id: uuid.UUID) ‑> uim.model.inkinput.inputdata.SensorContext`
    :   Returns the `SensorContext` for the id.
        
        Parameters
        ----------
        ctx_id: `UUID`input context id
        
        Returns
        --------
        instance: `SensorContext`
            `SensorContext` instance
        
        Raises
        ------
        InkModelException
            If the `SensorContext` for the id is not available

    `has_configuration(self) ‑> bool`
    :   Check if any configuration is available.
        
        Returns
        -------
        flag: bool
            Flag if either ink input provide, input device, or sensor context are defined

`InputDevice(device_id: uuid.UUID = None, properties: List[Tuple[str, str]] = None)`
:   InputDevice
    ===========
    The class `InputDevice` represents the hardware device, on which the sensor data has been produced
    (touch enabled mobile device, touch capable monitor, digitizer, etc.).
    InputDevice with properties.
    
    The properties can contain:
    
      - Communication Protocol: USB, BTC, BLE, SPP, WIFI,
      - Communication ID: VID, PID; MAC; UID; COM_PORT,
      - Device Name: Wacom Intuos Pro M, Apple iPad 8, Samsung GalaxyTab 10,
      - PenID,
      - Serial number,
      - Firmware Version (MCU),
      - Secondary Firmware Version (BT, WIFI) - different modules provides version for itself,
      - Orientation: PORTRAIT, LANDSCAPE, PORTRAIT_REVERSE, LANDSCAPE_REVERSE or 0, 90, 180, 270,
      - Sensor size.
    
    Parameters
    ----------
    device_id: `UUID`
        Internal input device id
    properties: List[Tuple[str, str]]
        Properties of the input device
    
    Examples
    --------
    >>> from uim.model.inkinput.inputdata import InputDevice
    >>> # Input device is the sensor (pen tablet, screen, etc.)
    >>> input_device: InputDevice = InputDevice()
    >>> input_device.properties.append(("dev.id", "123454321"))
    >>> input_device.properties.append(("dev.manufacturer", "Wacom"))
    >>> input_device.properties.append(("dev.model", "Wacom Movink"))
    >>> input_device.properties.append(("dev.cpu", "Intel"))
    >>> input_device.properties.append(("dev.graphics.display", "Dell 1920x1080 32bit"))
    >>> input_device.properties.append(("dev.graphics.adapter", "NVidia"))

    ### Ancestors (in MRO)

    * uim.model.base.HashIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `properties: List[Tuple[str, str]]`
    :   Properties of the InputDevice. (` List[Tuple[str, str]]`, read-only)

    ### Methods

    `add_property(self, key: str, value)`
    :   Adding property.
        
        Parameters
        ----------
        key: str
            Name of the property
        value: str
            Value of the property

`SensorChannel(channel_id: Optional[uuid.UUID] = None, channel_type: Optional[uim.model.inkinput.inputdata.InkSensorType] = None, metric: Optional[uim.model.inkinput.inputdata.InkSensorMetricType] = None, resolution: float = 1.0, channel_min: float = 0.0, channel_max: float = 0.0, precision: int = 2, index: int = 0, name: Optional[str] = None, data_type: uim.model.inkinput.inputdata.DataType = DataType.FLOAT32, ink_input_provider_id: Optional[uuid.UUID] = None, input_device_id: Optional[uuid.UUID] = None)`
:   SensorChannel
    =============
    The `SensorChannel` represents a generic sensor channel definition, which has the following properties:
    
    - **type** - URI uniquely identifying the type of the sensor channel
    - **metric** - The type of the data to the SI metric system
    - **resolution** - A factor multiplication value (power of 10) used to convert the stored data values to the
                      specified SI metric
    - **min, max** - Lower and upper bounds of the reported values range
    - **precision** - The precision of the sensor when reporting floating-point values (defined as an int value,
                      used as a power of 10 during the serialization/deserialization phase)
    
    Parameters
    ----------
    channel_id: Optional[UUID] (optional) [default: None]
        Sensor channel descriptor. If no channel_id is set the MD5 hashing is generating the id
    channel_type: Optional[`InkSensorType`] (optional) [default: None]
        Indicates metric used in calculating the resolution for the data item.
    metric: Optional[`InkSensorMetricType`] (optional) [default: None]
        Indicates metric used in calculating the resolution for the data item.
    resolution: `float` (optional) [default: 1.0]
        Is a decimal number giving the number of data item increments. Per physical unit., e.g. if the
        physical unit is in m and input data units. Resolution is 100000, then the value 150 would be
        0.0015 m.
    channel_min: `float` (optional) [default: 0.0]
        Minimal value of the channel
    channel_max: `float` (optional) [default: 0.0]
        Maximal value of the channel
    precision: `int` (optional) [default: 2]
        Precision of integer encoding, needed for encoded float values
    index: `int`
        Index of the channel
    name: Optional[`str`] (optional) [default: None]
        Name of the channel
    data_type: `DataType` (optional) [default: DataType.FLOAT32]
        Type of data within the channel
    ink_input_provider_id: Optional[UUID] (optional) [default: None]
        Reference to the ink input provider
    input_device_id: Optional[UUID] (optional) [default: None]
        Reference to the ink input device
    
    Examples
    --------
    >>> from uim.model.inkinput.inputdata import SensorChannel, InkSensorType
    >>> # Create a group of sensor channels
    >>> sensor_channels: list = [
    >>>     SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
    >>>     SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
    >>>     SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0)
    >>> ]

    ### Ancestors (in MRO)

    * uim.model.base.HashIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `data_type: uim.model.inkinput.inputdata.DataType`
    :   Data type encoding. (`DataType`, read-only)

    `index: int`
    :   Index within a list of values, e.g. used in InkML encoding. (`int`, read-only)

    `ink_input_provider: uuid.UUID`
    :   Reference to the `InkInputProvider` of the channel. (`UUID`)

    `input_device_id: uuid.UUID`
    :   Reference to the `InputDevice` of the channel. (`UUID`)

    `max: float`
    :   Maximum value of the channel. (`float`, read-only)

    `metric: uim.model.inkinput.inputdata.InkSensorMetricType`
    :   Metric of the sensor channel. (`InkSensorMetricType`)

    `min: float`
    :   Minimal value of the channel. (`float`, read-only)

    `name: str`
    :   Name of the channel. (`str`, read-only)

    `precision: int`
    :   Precision of integer encoding, needed for encoded float values. (`int`, read-only)

    `resolution: float`
    :   Resolution. Is a decimal number giving the number of data item increments. Per physical unit., e.g. if the
        physical unit is in m and input data units. (`float`, read-only)

    `type: uim.model.inkinput.inputdata.InkSensorType`
    :   Type of the sensor channel.(`InkSensorType`, read-only)

`SensorChannelsContext(sid: Optional[uuid.UUID] = None, channels: Optional[List[uim.model.inkinput.inputdata.SensorChannel]] = None, sampling_rate_hint: Optional[int] = None, latency: Optional[int] = None, ink_input_provider_id: Optional[uuid.UUID] = None, input_device_id: Optional[uuid.UUID] = None)`
:   SensorChannelsContext
    =====================
    
    The class `SensorChannelsContext` is defined as an unique combination of:
    
        - An `InkInputProvider` instance
        - An `InputDevice` instance and
        - A list of sensor channel definitions (by holding a collection of `SensorChannel` instances)
        
    Parameters
    ----------
    sid: Optional[uuid.UUID] (optional) [default: None]
        Group that provides X and Y channels is the one that is referred from StrokeRelation and it's id could be
        always XY.
    channels: Optional[`List[SensorChannel]`] (optional) [default: None]
        A list of sensor channel descriptors.
    sampling_rate_hint: Optional[`int`] (optional) [default: None]
        Optional hint for the intended sampling rate of the sensor.[Optional].
    latency: Optional[`int`] (optional) [default: None]
        Latency measure in milliseconds [Optional].
    ink_input_provider_id: Optional[uuid.UUID] (optional) [default: None]
        Reference to the 'InkInputProvider`.
    input_device_id: Optional[uuid.UUID] (optional) [default: None]
        Reference to the `InputDevice`.
    
    Notes
    ------
    Once a SensorChannelsContext instance is added to the InputContext repository, it is considered immutable.
    The SensorChannelsContext identifier is unique in the scope of the InkModel and is auto-generated based on the
    MD5-hash based Unique Identifier Generation Algorithm using tag "SensorChannelsContext" and the
    following components:
    
        - Identifier of the InkInputProvider instance
        - Identifier of the InputDevice instance
        - List of the identifiers of the SensorChannel instances contained within the current SensorChannelsContext
    
    Examples
    --------
    >>> from uim.model.inkinput.inputdata import InkInputProvider, InkInputType, SensorChannel,     >>>       InkSensorType, InkSensorMetricType, SensorChannelsContext
    >>> # Ink input provider can be pen, mouse or touch.
    >>> provider: InkInputProvider = InkInputProvider(input_type=InkInputType.MOUSE)
    >>> provider.properties.append(("pen.id", "1234567"))
    >>>
    >>> # We can create an additional input device, for example one providing pressure via Bluetooth
    >>> input_device: InputDevice = InputDevice()
    >>> input_device.properties.append(("dev.id", "345456567"))
    >>> input_device.properties.append(("dev.manufacturer", "Apple"))
    >>>
    >>> # Create a group of sensor channels
    >>> sensor_channels: list = [
    >>>     SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0),
    >>>     SensorChannel(channel_type=InkSensorType.X, metric=InkSensorMetricType.LENGTH, resolution=1.0),
    >>>     SensorChannel(channel_type=InkSensorType.Y, metric=InkSensorMetricType.LENGTH, resolution=1.0)
    >>> ]
    >>>
    >>> scc_tablet: SensorChannelsContext = SensorChannelsContext(channels=sensor_channels,
    >>>                                                           ink_input_provider_id=provider.id,
    >>>                                                           input_device_id=input_device.id)

    ### Ancestors (in MRO)

    * uim.model.base.HashIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `channels: List[uim.model.inkinput.inputdata.SensorChannel]`
    :   Array of the `SensorChannel`s associated with the context. (`List[SensorChannel]`, read-only)

    `input_device_id: uuid.UUID`
    :   Reference to `InkInputDevice`. (`UUID`, read-only)

    `input_provider_id: uuid.UUID`
    :   Reference id to the ink `InputProvider` that produces the ink. (`UUID`, read-only)

    `latency: int`
    :   Gets the latency measurement in milliseconds. (`int`, read-only)

    `sampling_rate: int`
    :   Hint for sampling rate valid for all channels. (`int`, read-only)

    ### Methods

    `add_sensor_channel(self, channel: uim.model.inkinput.inputdata.SensorChannel)`
    :   Adding a channel.
        
        Parameters
        ----------
        channel: `SensorChannel`
            sensor channel

    `get_channel_by_type(self, channel_type: uim.model.inkinput.inputdata.InkSensorType) ‑> uim.model.inkinput.inputdata.SensorChannel`
    :   Returns instance of Channel.
        
        Parameters
        ----------
        channel_type: `InkSensorType`
            type  of the channel
        
        Returns
        -------
        instance: SensorChannel
            Instance of the `SensorChannel` for the `InkSensorType`
        
        Raises
        ------
        InkModelException
            If the `SensorChannel` is not available.

    `has_channel_type(self, channel_type: uim.model.inkinput.inputdata.InkSensorType)`
    :   Checks if channel types is available.
        
        Parameters
        ----------
        channel_type: `InkSensorType`
            sensor type
        
        Returns
        -------
        flag: `boolean`
            True if available, False if not

`SensorContext(context_id: Optional[uuid.UUID] = None, sensor_channels_contexts: Optional[List[uim.model.inkinput.inputdata.SensorChannelsContext]] = None)`
:   SensorContext
    =============
    Each input data has a SensorContext describing the available sensors of a input data.
    One file can contains Ink data from two input data of the same type with a shared context.
    
    Parameters
    -----------
    context_id: Optional[uuid.UUID] (optional) [default: None]
        Id of the context
    sensor_channels_contexts: Optional[`List[SensorChannelsContext]`] (optional) [default: None]
        List of `SensorChannelsContext`

    ### Ancestors (in MRO)

    * uim.model.base.HashIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `sensor_channels_contexts: List[uim.model.inkinput.inputdata.SensorChannelsContext]`
    :   List of channel contexts. (`List[SensorChannelsContext]`)

    ### Methods

    `add_sensor_channels_context(self, channel_ctx: uim.model.inkinput.inputdata.SensorChannelsContext)`
    :   Adding a sensor.
        
        Parameters
        ----------
        channel_ctx: `SensorChannelsContext`
            Adding a channel

    `get_channel_by_id(self, channel_id: uuid.UUID) ‑> uim.model.inkinput.inputdata.SensorChannel`
    :   Returns the channel for a specific id.
        
         Parameters
         ----------
        channel_id: bytes -
            id of channel
        
        Returns
        -------
        instance: `SensorChannel`
            Instance of `SensorChannel`
        
        Raises
        ------
            InkModelException: Raised if no channel for channel id.

    `get_channel_by_type(self, channel_type: uim.model.inkinput.inputdata.InkSensorType) ‑> uim.model.inkinput.inputdata.SensorChannel`
    :   Returns the channel for a specific `InkSensorType`.
        
        Parameters
        ----------
        channel_type: `InkSensorType`
            Channel type
        
        Returns
        -------
        instance: `SensorChannel`
            Instance of channel
            
        Raises
        ------
        InkModelException
            Raised if no `SensorChannel` for the id is not available.

    `has_channel_type(self, channel_type: uim.model.inkinput.inputdata.InkSensorType) ‑> bool`
    :   Check if the SensorContext has a channel with type.
        
        Parameters
        ----------
        channel_type: `InkSensorType`
            type of channel
        
        Returns
        -------
        flag: `bool`
            True if channel exists, False if not

`Unit(value, names=None, *, module=None, qualname=None, type=None, start=1)`
:   Unit
    ====
    The class `Unit` represents the unit of the sensor data, which can be used to convert the data into the SI metric
    system. The unit can be used to convert the data into the SI metric system.

    ### Ancestors (in MRO)

    * enum.Enum

    ### Class variables

    `CM`
    :   centimeters

    `DEG`
    :   degrees

    `DIP`
    :   device independent pixel (1DIP = 1/96 in)

    `IN`
    :   inches

    `LOGICAL_VALUE`
    :   logical value

    `M`
    :   meters

    `MM`
    :   millimeters

    `MS`
    :   milliseconds

    `N`
    :   Newtons

    `NS`
    :   nanoseconds

    `PC`
    :   picas (1pc = 1/22 pt)

    `PERCENTAGE`
    :   percentage, expressed as a fraction (1.0 = 100%) relative to max-min

    `PT`
    :   points (1pt = 1/72 in)

    `RAD`
    :   radians

    `S`
    :   seconds

    `UNDEFINED`
    :   Undefined unit
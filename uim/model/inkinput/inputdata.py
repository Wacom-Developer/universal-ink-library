# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import logging
import uuid
from abc import ABC
from enum import Enum
from logging import Logger
from math import isclose
from typing import List, Tuple, Any, Optional

import numpy as np

import uim.codec.format.UIM_3_0_0_pb2 as uim
from uim.model.base import HashIdentifier, Identifier, UUIDIdentifier, InkModelException

logger: Logger = logging.getLogger(__name__)
TOLERANCE_VALUE_COMPARISON: float = 1e-2


class DataType(Enum):
    """
    DataType
    ========
    Data types for channels.
    """
    BOOLEAN = 0
    FLOAT32 = 1
    FLOAT64 = 2
    INT32 = 3
    INT64 = 4
    UINT32 = 5
    UINT64 = 6


class InkInputType(Enum):
    """
    InkInputType
    ============
    Defining the different types of input data.
    """
    PEN = uim.PEN
    """Stylus, smart pens, pen displays, signature capturing input data, ..."""
    TOUCH = uim.TOUCH
    """Touch controller input data: Finger or passive stylus."""
    MOUSE = uim.MOUSE
    """Mouse input data."""
    CONTROLLER = uim.CONTROLLER
    """3-DOF or 6-DOF input data devices."""


class InkSensorMetricType(Enum):
    """
    InkSensorMetricType
    ===================
    Metric for the channel.
    """
    LENGTH = uim.LENGTH
    """Length; underling si unit is meter"""
    TIME = uim.TIME
    """Time; underling  si unit is second"""
    FORCE = uim.FORCE
    """Force; underling si unit is newton"""
    ANGLE = uim.ANGLE
    """Angle; underling si unit is radian"""
    NORMALIZED = uim.NORMALIZED
    """Normalized; percentage, expressed as a fraction(1.0 = 100 %) relative to max - min"""


class Unit(Enum):
    """
    Unit
    ====
    The class `Unit` represents the unit of the sensor data, which can be used to convert the data into the SI metric
    system. The unit can be used to convert the data into the SI metric system.
    """
    # Lengths units
    UNDEFINED = 0
    """Undefined unit"""
    M = 10
    """meters"""
    CM = 11
    """centimeters"""
    MM = 12
    """millimeters"""
    IN = 13
    """inches"""
    PT = 14
    """points (1pt = 1/72 in)"""
    PC = 15
    """picas (1pc = 1/22 pt)"""
    DIP = 16
    """device independent pixel (1DIP = 1/96 in)"""
    # Time units
    S = 20
    """seconds"""
    MS = 21
    """milliseconds"""
    NS = 22
    """nanoseconds"""
    # Force units
    N = 30
    """Newtons"""
    # Angle
    RAD = 42
    """radians"""
    DEG = 41
    """degrees"""
    # General
    PERCENTAGE = 50
    """percentage, expressed as a fraction (1.0 = 100%) relative to max-min"""
    LOGICAL_VALUE = 60
    """logical value"""


# --------------------------------- Conversion values ------------------------------------------------------------------

CONVERSION_SCALAR = {
    # Length units
    Unit.M: {
        Unit.M: 1.,
        Unit.CM: 100,
        Unit.MM: 1000,
        Unit.IN: 39.3701,
        Unit.PT: 2834.65,
        Unit.PC: 236.222,
        Unit.DIP: (39.3701 * 96.)
    },
    Unit.CM: {
        Unit.M: 0.01,
        Unit.CM: 1.,
        Unit.MM: 10.,
        Unit.IN: 0.393701,
        Unit.PT: 28.3465,
        Unit.PC: 2.36222,
        Unit.DIP: (0.393701 * 96.)
    },
    Unit.MM: {
        Unit.M: 0.001,
        Unit.CM: 0.1,
        Unit.MM: 1.,
        Unit.IN: 0.0393701,
        Unit.PT: 2.83465,
        Unit.PC: 0.236222,
        Unit.DIP: (0.0393701 * 96.)
    },
    Unit.IN: {
        Unit.M: 0.0254,
        Unit.CM: 2.54,
        Unit.MM: 25.4,
        Unit.IN: 1.,
        Unit.PT: 72,
        Unit.PC: 6.,
        Unit.DIP: (1. * 96.)
    },
    Unit.PT: {
        Unit.M: 0.000352778,
        Unit.CM: 0.0352778,
        Unit.MM: 0.352778,
        Unit.IN: 0.0138888889,
        Unit.PT: 1.,
        Unit.PC: 0.08333333,
        Unit.DIP: (0.0138888889 * 96.)
    },
    Unit.PC: {
        Unit.M: 0.0042333333,
        Unit.CM: 0.4233333333,
        Unit.MM: 4.2333333333,
        Unit.IN: 0.166665,
        Unit.PT: 12.,
        Unit.PC: 1.,
        Unit.DIP: (0.166665 * 96.)
    },
    Unit.DIP: {
        Unit.M: (0.0254 / 96.),
        Unit.CM: (2.54 / 96.),
        Unit.MM: (25.4 / 96.),
        Unit.IN: (1. / 96.),
        Unit.PT: (72 / 96.),
        Unit.PC: (6. / 96.),
        Unit.DIP: 1.
    },
    # Time unit
    Unit.S: {
        Unit.S: 1.,
        Unit.MS: 1000.,
        Unit.NS: 1000000000.
    },
    Unit.MS: {
        Unit.S: 0.001,
        Unit.MS: 1.,
        Unit.NS: 1000000.
    },
    Unit.NS: {
        Unit.S: 0.000000001,
        Unit.MS: 0.000001,
        Unit.NS: 1.
    }
}
"""Mapping containing the factors to convert from one unit: <source-unit> into the other: <target-unit>."""


class InkSensorType(Enum):
    """
    InkSensorType
    =============
    Pre-defined SensorData types.
    """
    X = 'will://input/3.0/channel/X'
    """X coordinate. This is the horizontal pen position on the writing surface."""
    Y = 'will://input/3.0/channel/Y'
    """Y coordinate. This is the vertical position on the writing surface. """
    Z = 'will://input/3.0/channel/Z'
    """Z coordinate. This is the height of pen above the writing surface."""
    TIMESTAMP = 'will://input/3.0/channel/Timestamp'
    """Time (of the sample point)"""
    PRESSURE = 'will://input/3.0/channel/Pressure'
    """Input pressure."""
    RADIUS_X = 'will://input/3.0/channel/RadiusX'
    """Touch radius by X"""
    RADIUS_Y = 'will://input/3.0/channel/RadiusY'
    """Touch radius by Y"""
    AZIMUTH = 'will://input/3.0/channel/Azimuth'
    """Azimuth angle of the pen (yaw)"""
    ALTITUDE = 'will://input/3.0/channel/Altitude'
    """Elevation angle of the pen (pitch)"""
    ROTATION = 'will://input/3.0/channel/Rotation'
    """Rotation (counter-clockwise rotation about pen axis)"""


# --------------------------------- Token mapping ----------------------------------------------------------------------


TOKEN_MAP: dict = {
    InkInputType.PEN: InkInputType.PEN.name,
    InkInputType.MOUSE: InkInputType.MOUSE.name,
    InkInputType.TOUCH: InkInputType.TOUCH.name,
    InkInputType.CONTROLLER: InkInputType.CONTROLLER.name,
    InkSensorMetricType.TIME: InkSensorMetricType.TIME.name,
    InkSensorMetricType.LENGTH: InkSensorMetricType.LENGTH.name,
    InkSensorMetricType.FORCE: InkSensorMetricType.FORCE.name,
    InkSensorMetricType.ANGLE: InkSensorMetricType.ANGLE.name,
    InkSensorMetricType.NORMALIZED: InkSensorMetricType.NORMALIZED.name,
    InkSensorType.X: InkSensorType.X.value,
    InkSensorType.Y: InkSensorType.Y.value,
    InkSensorType.Z: InkSensorType.Z.value,
    InkSensorType.TIMESTAMP: InkSensorType.TIMESTAMP.value,
    InkSensorType.PRESSURE: InkSensorType.PRESSURE.value,
    InkSensorType.RADIUS_X: InkSensorType.RADIUS_X.value,
    InkSensorType.RADIUS_Y: InkSensorType.RADIUS_Y.value,
    InkSensorType.AZIMUTH: InkSensorType.AZIMUTH.value,
    InkSensorType.ALTITUDE: InkSensorType.ALTITUDE.value,
    InkSensorType.ROTATION: InkSensorType.ROTATION.value
}

# --------------------------------- Conversion functions ---------------------------------------------------------------


def virtual_resolution_for_si_unit(source_unit: Unit) -> float:
    """
    Calculate a virtual resolution for source unit.

    Parameters
    ----------
    source_unit: unit
        Source unit
    Returns
    -------
    resolution: `float`
        Virtual resolution
    """
    si: Unit = si_unit(source_unit)
    if si == Unit.UNDEFINED:
        return 1.
    return 1. / CONVERSION_SCALAR[source_unit][si]


def si_unit(unit_type: Unit) -> Unit:
    """
    Return the SI unit for a specific unit type.

    Parameters
    ----------
    unit_type: `Unit`
        Unit

    Returns
    -------
    si_unit: Unit
        SI unit for a unit, e.g., for a lengths unit cm the SI unit is m.
    """
    # SI unit for length is m
    if unit_type in [Unit.M, Unit.CM, Unit.MM, Unit.IN, Unit.PT, Unit.PC, Unit.DIP]:
        return Unit.M
    # SI unit for time is s
    if unit_type in [Unit.S, Unit.MS, Unit.NS]:
        return Unit.S
    return Unit.UNDEFINED


def unit2unit(source_unit: Unit, target_unit: Unit, value: float) -> float:
    """
    Convert value with a source unit to the target unit.

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
    """
    if Unit.UNDEFINED in (source_unit, target_unit):
        return value
    if source_unit not in CONVERSION_SCALAR:
        raise ValueError(f'Source unit not supported. Unit:={source_unit}')
    if target_unit not in CONVERSION_SCALAR[source_unit]:
        raise ValueError(f'Target unit not supported. Unit:={target_unit} for source unit:={source_unit}')
    return CONVERSION_SCALAR[source_unit][target_unit] * value


def unit2unit_matrix(source_unit: Unit, target_unit: Unit) -> np.array:
    """
    Matrix for unit 2 unit conversion.

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
    """
    matrix: np.array = np.identity(3)
    if Unit.UNDEFINED in (source_unit, target_unit):
        return matrix
    if source_unit not in CONVERSION_SCALAR:
        raise ValueError('Source unit not supported.')
    if target_unit not in CONVERSION_SCALAR[source_unit]:
        raise ValueError('Target unit not supported.')
    matrix[0, 0] = CONVERSION_SCALAR[source_unit][target_unit]
    matrix[1, 1] = CONVERSION_SCALAR[source_unit][target_unit]
    return matrix


# --------------------------------- Data context --------------------------------------------------------------------


class InputDevice(HashIdentifier):
    """
    InputDevice
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
    """

    def __init__(self, device_id: uuid.UUID = None, properties: List[Tuple[str, str]] = None):
        super().__init__(device_id)
        self.__properties: List[Tuple[str, str]] = properties or []

    @property
    def properties(self) -> List[Tuple[str, str]]:
        """Properties of the InputDevice. (` List[Tuple[str, str]]`, read-only)"""
        return self.__properties

    def add_property(self, key: str, value):
        """Adding property.

        Parameters
        ----------
        key: str
            Name of the property
        value: str
            Value of the property
        """
        self.__properties.append((key, value))

    def __tokenize__(self):
        return ['InputDevice', self.properties]

    def __dict__(self):
        return {
            "id": str(self.id),
            "properties": dict(self.properties)
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, InputDevice):
            logger.warning(f"Comparing InputDevice with different type: {type(other)}")
            return False
        return self.properties == other.properties

    def __repr__(self):
        return f'<InputDevice : [id:={self.id}, num properties:={self.properties}>'


class InputContext(HashIdentifier):
    """
    InputContext
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
    """

    def __init__(self, ctx_id: Optional[uuid.UUID] = None, environment_id: Optional[uuid.UUID] = None, 
                 sensor_context_id: Optional[uuid.UUID] = None):
        super().__init__(ctx_id)
        self.__environment_id: Optional[uuid.UUID] = environment_id
        self.__sensor_context_id: Optional[uuid.UUID]  = sensor_context_id

    def __tokenize__(self) -> list:
        return ["InputContext", self.environment_id, self.sensor_context_id]

    @property
    def environment_id(self) -> Optional[uuid.UUID] :
        """Reference to environment. (`UUID`, read-only)"""
        return self.__environment_id

    @property
    def sensor_context_id(self) -> Optional[uuid.UUID] :
        """Reference for sensor context. (`UUID`, read-only)"""
        return self.__sensor_context_id

    @sensor_context_id.setter
    def sensor_context_id(self, value: uuid.UUID):
        logger.warning(f"Sensor context id has been changed. This is not recommended. "
                       f"Old value {self.__sensor_context_id}, new value {value}.")
        self.__sensor_context_id = value

    def __dict__(self):
        return {
            'id': str(self.id),
            'environment_id': str(self.environment_id),
            'sensor_context_id': str(self.sensor_context_id)
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, InputContext):
            logger.warning(f"Comparing InputContext with different type: {type(other)}")
            return False
        if self.environment_id != other.environment_id:
            logger.warning(f"Environment id is different: {self.environment_id} != {other.environment_id}")
            return False
        if self.sensor_context_id != other.sensor_context_id:
            logger.warning(f"Sensor context id is different: {self.sensor_context_id} != {other.sensor_context_id}")
            return False
        return True

    def __repr__(self):
        env_id: str = Identifier.uimid_to_s_form(self.environment_id) if self.environment_id else "None"
        sc_id: str = Identifier.uimid_to_s_form(self.sensor_context_id) if self.sensor_context_id else "None"
        return f'<InputContext : [id:={self.id_h_form}, environment id:={env_id}, sensor context id:={sc_id}>'


class Environment(HashIdentifier):
    """
    Environment
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
    """

    def __init__(self, env_id: Optional[uuid.UUID] = None, properties: Optional[List[Tuple[str, str]]] = None):
        super().__init__(env_id)
        self.__properties = properties or []

    def __tokenize__(self) -> List[Any]:
        token: List[Any] = ['Environment', self.properties]
        return token

    @property
    def properties(self) -> List[Tuple[str, str]]:
        """Environment properties. (`List[Tuple[str, str]]`) """
        return self.__properties

    def add_environment_property(self, key: str, value: str):
        """
        Adding a property for environment.

        Parameters
        ----------
        key: str
            Name of the property
        value: str
            Value of the property
        """
        self.properties.append((key, value))

    def __dict__(self):
        return {
            'id': str(self.id),
            'properties': dict(self.properties)
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, Environment):
            logger.warning(f"Comparing Environment with different type: {type(other)}")
            return False
        return self.properties == other.properties

    def __repr__(self):
        return f'<Environment: [id:={self.id.hex}, #properties:={self.properties}>'


class InkInputProvider(HashIdentifier):
    """
    InkInputProvider
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
    """

    def __init__(self, provider_id: Optional[uuid.UUID] = None, input_type: Optional[InkInputType] = None,
                 properties: Optional[List[Tuple[str, str]]] = None):
        super().__init__(provider_id)
        self.__type: InkInputType = input_type
        self.__properties: List[Tuple[str, str]] = properties or []

    def __tokenize__(self):
        return ['InkInputProvider', TOKEN_MAP.get(self.type), self.properties]

    @property
    def type(self) -> InkInputType:
        """Input provider type. (`InkInputType`,  read-only)"""
        return self.__type

    @property
    def properties(self) -> List[Tuple[str, str]]:
        """Properties of input data provider. (`List[Tuple[str, str]]`, read-only)"""
        return self.__properties

    def __dict__(self):
        return {
            'id': str(self.id),
            'type': self.type.name,
            'properties': dict(self.properties)
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other):
        if not isinstance(other, InkInputProvider):
            logger.warning(f"Comparing InkInputProvider with different type: {type(other)}")
            return False
        return self.type == other.type and self.properties == other.properties

    def __repr__(self):
        return f'<InkInputProvider: [id:={self.id}, type:={self.type}, properties:={self.properties}]>'


class SensorChannel(HashIdentifier):
    """
    SensorChannel
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
    """

    def __init__(self, channel_id: Optional[uuid.UUID] = None,
                 channel_type: Optional[InkSensorType] = None, metric: Optional[InkSensorMetricType] = None,
                 resolution: float = 1., channel_min: float = 0., channel_max: float = 0.,
                 precision: int = 2, index: int = 0, name: Optional[str] = None, data_type: DataType = DataType.FLOAT32,
                 ink_input_provider_id: Optional[uuid.UUID] = None, input_device_id: Optional[uuid.UUID] = None):
        super().__init__(channel_id)
        self.__type: InkSensorType = channel_type
        self.__metric: InkSensorMetricType = metric
        self.__resolution: float = float(resolution)
        self.__min: float = float(channel_min)
        self.__max: float = float(channel_max)
        self.__precision: int = precision
        self.__index: int = index
        self.__name: str = name
        self.__data_type: DataType = data_type
        self.__ink_input_provider: uuid.UUID = ink_input_provider_id
        self.__input_device_id: uuid.UUID = input_device_id

    def __tokenize__(self) -> list:
        return ["SensorChannel", self.__ink_input_provider, self.__input_device_id, TOKEN_MAP[self.type],
                TOKEN_MAP[self.metric], self.resolution, self.min, self.max, self.precision]

    @property
    def ink_input_provider(self) -> uuid.UUID:
        """Reference to the `InkInputProvider` of the channel. (`UUID`)"""
        return self.__ink_input_provider

    @ink_input_provider.setter
    def ink_input_provider(self, value: uuid.UUID):
        self.__ink_input_provider = value

    @property
    def input_device_id(self) -> uuid.UUID:
        """Reference to the `InputDevice` of the channel. (`UUID`)"""
        return self.__input_device_id

    @input_device_id.setter
    def input_device_id(self, value: uuid.UUID):
        self.__input_device_id = value

    @property
    def type(self) -> InkSensorType:
        """Type of the sensor channel.(`InkSensorType`, read-only) """
        return self.__type

    @property
    def metric(self) -> InkSensorMetricType:
        """Metric of the sensor channel. (`InkSensorMetricType`)"""
        return self.__metric

    @property
    def resolution(self) -> float:
        """Resolution. Is a decimal number giving the number of data item increments. Per physical unit., e.g. if the
        physical unit is in m and input data units. (`float`, read-only)"""
        return self.__resolution

    @property
    def min(self) -> float:
        """Minimal value of the channel. (`float`, read-only)"""
        return self.__min

    @property
    def max(self) -> float:
        """Maximum value of the channel. (`float`, read-only)"""
        return self.__max

    @property
    def precision(self) -> int:
        """Precision of integer encoding, needed for encoded float values. (`int`, read-only)"""
        return self.__precision

    @property
    def index(self) -> int:
        """Index within a list of values, e.g. used in InkML encoding. (`int`, read-only)"""
        return self.__index

    @property
    def name(self) -> str:
        """Name of the channel. (`str`, read-only)"""
        return self.__name

    @property
    def data_type(self) -> DataType:
        """ Data type encoding. (`DataType`, read-only)"""
        return self.__data_type

    def __dict__(self):
        return {
            'id': str(self.id),
            'type': self.type.name,
            'metric': self.metric.name,
            'resolution': self.resolution,
            'min': self.min,
            'max': self.max,
            'precision': self.precision,
            'index': self.index,
            'name': self.name,
            'data_type': self.data_type.name,
            'ink_input_provider': str(self.ink_input_provider),
            'input_device_id': str(self.input_device_id)
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, SensorChannel):
            logger.warning(f"Comparing SensorChannel with different type: {type(other)}")
            return False
        if self.ink_input_provider != other.ink_input_provider:
            logger.warning(f"Comparing SensorChannel with different ink input provider: {self.ink_input_provider} != "
                           f"{other.ink_input_provider}")
            return False
        if self.input_device_id != other.input_device_id:
            logger.warning(f"Comparing SensorChannel with different input device: {self.input_device_id} != "
                           f"{other.input_device_id}")
            return False
        if self.name != other.name:
            logger.warning(f"Comparing SensorChannel with different name: {self.name} != {other.name}")
            return False
        if self.index != other.index:
            logger.warning(f"Comparing SensorChannel with different index: {self.index} != {other.index}")
            return False
        if self.data_type != other.data_type:
            logger.warning(f"Comparing SensorChannel with different data type: {self.data_type} != {other.data_type}")
            return False
        if self.type != other.type:
            logger.warning(f"Comparing SensorChannel with different type: {self.type} != {other.type}")
            return False
        if self.metric != other.metric:
            logger.warning(f"Comparing SensorChannel with different metric: {self.metric} != {other.metric}")
            return False
        if self.resolution != other.resolution:
            logger.warning(f"Comparing SensorChannel with different resolution: {self.resolution} != "
                           f"{other.resolution}")
            return False
        if not isclose(self.min, other.min, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Comparing SensorChannel with different min: {self.min} != {other.min}")
            return False
        if not isclose(self.max, other.max, abs_tol=TOLERANCE_VALUE_COMPARISON):
            logger.warning(f"Comparing SensorChannel with different max: {self.max} != {other.max}")
            return False
        if self.precision != other.precision:
            logger.warning(f"Comparing SensorChannel with different precision: {self.precision} != {other.precision}")
            return False
        return True

    def __repr__(self):
        return (f'<SensorChannel: [id:={self.id.hex}, type:={self.__type}, metric:={self.__metric}, '
                f'resolution:={self.__resolution}, min:={ self.__min}, max:={self.__max}, '
                f'precision:={self.__precision}, index:={self.__index}, name:={self.__name}>')


class SensorChannelsContext(HashIdentifier):
    """
    SensorChannelsContext
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
    >>> from uim.model.inkinput.inputdata import InkInputProvider, InkInputType, SensorChannel, \
    >>>       InkSensorType, InkSensorMetricType, SensorChannelsContext
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
    """

    def __init__(self, sid: Optional[uuid.UUID] = None, channels: Optional[List[SensorChannel]] = None,
                 sampling_rate_hint: Optional[int] = None, latency: Optional[int] = None,
                 ink_input_provider_id: Optional[uuid.UUID] = None, input_device_id: Optional[uuid.UUID] = None):
        super().__init__(sid)
        self.__channels: List[SensorChannel] = channels or []
        self.__sampling_rate_hint: int = sampling_rate_hint if sampling_rate_hint else 0
        self.__latency: int = latency if latency else 0
        self.__ink_input_provider_id: uuid.UUID = ink_input_provider_id
        self.__input_device_id: uuid.UUID = input_device_id
        # Set bind channels to input provider and input device
        for c in self.__channels:
            c.ink_input_provider = ink_input_provider_id
            c.input_device_id = input_device_id

    def __tokenize__(self) -> list:
        token: list = ["SensorChannelsContext"]
        token.extend([c.id for c in self.channels])
        token.append(self.sampling_rate if self.sampling_rate != 0 else '')
        token.append(self.latency if self.latency != 0 else '')
        token.append(self.input_provider_id)
        token.append(self.input_device_id)
        return token

    @property
    def channels(self) -> List[SensorChannel]:
        """Array of the `SensorChannel`s associated with the context. (`List[SensorChannel]`, read-only) """
        return self.__channels

    @property
    def sampling_rate(self) -> int:
        """Hint for sampling rate valid for all channels. (`int`, read-only)"""
        return self.__sampling_rate_hint if self.__sampling_rate_hint else 0

    @property
    def latency(self) -> int:
        """Gets the latency measurement in milliseconds. (`int`, read-only)"""
        return self.__latency if self.__latency else 0

    @property
    def input_provider_id(self) -> uuid.UUID:
        """Reference id to the ink `InputProvider` that produces the ink. (`UUID`, read-only)"""
        return self.__ink_input_provider_id

    @property
    def input_device_id(self) -> uuid.UUID:
        """Reference to `InkInputDevice`. (`UUID`, read-only)"""
        return self.__input_device_id

    def add_sensor_channel(self, channel: SensorChannel):
        """
        Adding a channel.

        Parameters
        ----------
        channel: `SensorChannel`
            sensor channel
        """
        self.__channels.append(channel)

    def has_channel_type(self, channel_type: InkSensorType):
        """
        Checks if channel types is available.

        Parameters
        ----------
        channel_type: `InkSensorType`
            sensor type

        Returns
        -------
        flag: `boolean`
            True if available, False if not
        """
        return any(c.type == channel_type for c in self.channels)

    def get_channel_by_type(self, channel_type: InkSensorType) -> SensorChannel:
        """Returns instance of Channel.

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
        """
        for c in self.__channels:
            if c.type == channel_type:
                return c
        raise InkModelException(f'No channel available for the type: {channel_type}')

    def __dict__(self):
        return {
            'id': str(self.id),
            'channels': [c.__dict__() for c in self.channels],
            'sampling_rate': self.sampling_rate,
            'latency': self.latency,
            'input_provider_id': str(self.input_provider_id),
            'input_device_id': str(self.input_device_id)
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, SensorChannelsContext):
            logger.warning(f"Comparing SensorChannelsContext with different type: {type(other)}")
            return False
        for c_1, c_2 in zip(self.channels, other.channels):
            if c_1 != c_2:
                logger.warning(f"SensorChannels are not equal: {c_1} != {c_2}")
                return False
        if len(self.channels) != len(other.channels):
            logger.warning(f"Length of SensorChannels are not equal: {len(self.channels)} != {len(other.channels)}")
            return False
        if self.sampling_rate != other.sampling_rate:
            logger.warning(f"Sampling rates are not equal: {self.sampling_rate} != {other.sampling_rate}")
            return False
        if self.latency != other.latency:
            logger.warning(f"Latencies are not equal: {self.latency} != {other.latency}")
            return False
        if self.input_provider_id != other.input_provider_id:
            logger.warning(f"Input provider ids are not equal: {self.input_provider_id} != {other.input_provider_id}")
            return False
        if self.input_device_id != other.input_device_id:
            logger.warning(f"Input device ids are not equal: {self.input_device_id} != {other.input_device_id}")
            return False
        return True

    def __repr__(self):
        return (f'<SensorChannelsContext: [id:={self.id_h_form}, sampling rate hint:={self.sampling_rate}, '
                f'latency:={self.latency}, '
                f'input data provider id:={UUIDIdentifier.uimid_to_h_form(self.input_provider_id)}, '
                f'input data id:={UUIDIdentifier.uimid_to_h_form(self.input_device_id)}>')


class SensorContext(HashIdentifier):
    """
    SensorContext
    =============
    Each input data has a SensorContext describing the available sensors of a input data.
    One file can contains Ink data from two input data of the same type with a shared context.

    Parameters
    -----------
    context_id: Optional[uuid.UUID] (optional) [default: None]
        Id of the context
    sensor_channels_contexts: Optional[`List[SensorChannelsContext]`] (optional) [default: None]
        List of `SensorChannelsContext`
    """

    def __init__(self, context_id: Optional[uuid.UUID] = None,
                 sensor_channels_contexts: Optional[List[SensorChannelsContext]] = None):
        super().__init__(context_id)
        self.__sensor_channels_contexts: List[SensorChannelsContext] = sensor_channels_contexts or []

    def __tokenize__(self) -> list:
        token: list = ["SensorContext"]
        token.extend([c.id for c in self.sensor_channels_contexts])
        return token

    @property
    def sensor_channels_contexts(self) -> List[SensorChannelsContext]:
        """List of channel contexts. (`List[SensorChannelsContext]`)"""
        return self.__sensor_channels_contexts

    def add_sensor_channels_context(self, channel_ctx: SensorChannelsContext):
        """Adding a sensor.

        Parameters
        ----------
        channel_ctx: `SensorChannelsContext`
            Adding a channel
        """
        self.__sensor_channels_contexts.append(channel_ctx)

    def has_channel_type(self, channel_type: InkSensorType) -> bool:
        """
        Check if the SensorContext has a channel with type.

        Parameters
        ----------
        channel_type: `InkSensorType`
            type of channel

        Returns
        -------
        flag: `bool`
            True if channel exists, False if not
        """
        return any(c.has_channel_type(channel_type) for c in self.__sensor_channels_contexts)

    def get_channel_by_id(self, channel_id: uuid.UUID) -> SensorChannel:
        """
         Returns the channel for a specific id.

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
        """
        for cs in self.sensor_channels_contexts:
            for c in cs.channels:
                if c.id == channel_id:
                    return c
        raise InkModelException(f'No channel with channel id: {channel_id}.')

    def get_channel_by_type(self, channel_type: InkSensorType) -> SensorChannel:
        """
        Returns the channel for a specific `InkSensorType`.
        
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
        """
        for c in self.__sensor_channels_contexts:
            if c.has_channel_type(channel_type):
                return c.get_channel_by_type(channel_type)
        raise InkModelException(f'No channel with channel type: {channel_type}.')

    def __dict__(self):
        return {
            'id': str(self.id),
            'sensor_channels_contexts': [c.__dict__() for c in self.sensor_channels_contexts]
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, SensorContext):
            logger.warning(f"Comparing SensorContext with different type: {type(other)}")
            return False
        for sc_1, sc_2 in zip(self.sensor_channels_contexts, other.sensor_channels_contexts):
            if sc_1 != sc_2:
                logger.warning(f"SensorChannelsContexts are not equal: {sc_1} != {sc_2}")
                return False
        if len(self.sensor_channels_contexts) != len(other.sensor_channels_contexts):
            logger.warning(f"Length of SensorChannelsContexts are not equal: {len(self.sensor_channels_contexts)} != "
                           f"{len(other.sensor_channels_contexts)}")
            return False
        return True

    def __repr__(self):
        return f'<SensorContext: [context_id:={self.id}, sensor_channels_contexts:={self.sensor_channels_contexts}]>'


class InputContextRepository(ABC):
    """
    InputContext Repository
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
    """

    def __init__(self, input_contexts: Optional[List[InputContext]] = None,
                 ink_input_providers: Optional[List[InkInputProvider]] = None,
                 input_devices: Optional[List[InputDevice]] = None,
                 environments: Optional[List[Environment]] = None,
                 sensor_contexts: Optional[List[SensorContext]] = None):
        self.__input_contexts: List[InputContext] = input_contexts or []
        self.__ink_input_providers: List[InkInputProvider] = ink_input_providers or []
        self.__input_devices: List[InputDevice] = input_devices or []
        self.__environments: List[Environment] = environments or []
        self.__sensor_contexts: List[SensorContext] = sensor_contexts or []

    def add_ink_device(self, ink_device: InputDevice):
        """
        Adding input device.

        Parameters
        ----------
        ink_device: `InputDevice`
            Adds an input device
        """
        self.__input_devices.append(ink_device)

    @property
    def devices(self) -> List[InputDevice]:
        """
        Input devices. (`List[InputDevice]`)"""
        return self.__input_devices

    def add_input_context(self, input_context: InputContext):
        """
        Adding context.

        Parameters
        ----------
        input_context: `InputContext`
            Input context instance
        """
        self.__input_contexts.append(input_context)

    @property
    def input_contexts(self) -> List[InputContext]:
        """ List of input contexts. (`List[InputContext]`)"""
        return self.__input_contexts

    def get_input_context(self, ctx_id: uuid.UUID) -> InputContext:
        """
        Returns the InputContext.

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
        """
        for ctx in self.input_contexts:
            if ctx.id == ctx_id:
                return ctx
        raise InkModelException(f'No input context with id:={ctx_id}.')

    def get_input_device(self, device_id: uuid.UUID) -> InputDevice:
        """
        Returns the InputDevice.

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
        """
        for dev in self.devices:
            if dev.id == device_id:
                return dev
        raise InkModelException(f'No input device with id:={device_id}.')

    def get_sensor_context(self, ctx_id: uuid.UUID) -> SensorContext:
        """
        Returns the `SensorContext` for the id.

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
        """
        for ctx in self.sensor_contexts:
            if ctx.id == ctx_id:
                return ctx
        raise InkModelException(f'No sensor context with id:={ctx_id}.')

    def add_input_provider(self, input_provider: InkInputProvider):
        """
        Adding input data provider.

        Parameters
        ----------
        input_provider: `InkInputProvider`
            Input data provider instance
        """
        self.__ink_input_providers.append(input_provider)

    @property
    def ink_input_providers(self) -> List[InkInputProvider]:
        """List of `InkInputProvider`s. (`List[InkInputProvider]`)"""
        return self.__ink_input_providers

    def add_environment(self, environment: Environment):
        """
        Adding environment.

        Parameters
        ----------
        environment: Environment
            Environment instance
        """
        self.environments.append(environment)

    @property
    def environments(self) -> List[Environment]:
        """List of Environments. (`List[Environment]`)"""
        return self.__environments

    def add_sensor_context(self, sensor_context: SensorContext):
        """
        Adding sensor context.

        Parameters
        ----------
        sensor_context: `SensorContext`
            Instance of `SensorContext`
        """
        self.__sensor_contexts.append(sensor_context)

    @property
    def sensor_contexts(self) -> List[SensorContext]:
        """List of SensorContexts. (`List[SensorContext]`)"""
        return self.__sensor_contexts

    def has_configuration(self) -> bool:
        """Check if any configuration is available.

        Returns
        -------
        flag: bool
            Flag if either ink input provide, input device, or sensor context are defined
        """
        return len(self.input_contexts) > 0 or len(self.sensor_contexts) > 0 or len(self.ink_input_providers) > 0 or \
            len(self.devices) > 0 or len(self.environments)

    def __dict__(self):
        return {
            "environments": [env.__dict__() for env in self.environments],
            "devices": [dev.__dict__() for dev in self.devices],
            "ink_input_providers": [ink.__dict__() for ink in self.ink_input_providers],
            "input_contexts": [ctx.__dict__() for ctx in self.input_contexts],
            "sensor_contexts": [sc.__dict__() for sc in self.sensor_contexts]
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, InputContextRepository):
            logger.warning(f"Comparing InputContextRepository with different type: {type(other)}")
            return False
        if len(self.input_contexts) != len(other.input_contexts):
            logger.warning(f"Length of InputContexts are not equal: {len(self.input_contexts)} != "
                           f"{len(other.input_contexts)}")
            return False
        for ic_1, ic_2 in zip(self.input_contexts, other.input_contexts):
            if ic_1 != ic_2:
                logger.warning(f"InputContexts are not equal: {ic_1} != {ic_2}")
                return False

        if len(self.sensor_contexts) != len(other.sensor_contexts):
            logger.warning(f"Length of SensorContexts are not equal: {len(self.sensor_contexts)} !="
                           f" {len(other.sensor_contexts)}")
            return False
        for sc_1, sc_2 in zip(self.sensor_contexts, other.sensor_contexts):
            if sc_1 != sc_2:
                logger.warning(f"SensorContexts are not equal: {sc_1} != {sc_2}")
                return False

        if len(self.ink_input_providers) != len(other.ink_input_providers):
            logger.warning(f"Length of InkInputProviders are not equal: {len(self.ink_input_providers)} != "
                           f"{len(other.ink_input_providers)}")
            return False
        for ip_1, ip_2 in zip(self.ink_input_providers, other.ink_input_providers):
            if ip_1 != ip_2:
                logger.warning(f"InkInputProviders are not equal: {ip_1} != {ip_2}")
                return False
        if len(self.devices) != len(other.devices):
            logger.warning(f"Length of InputDevices are not equal: {len(self.devices)} != {len(other.devices)}")
            return False
        for dev_1, dev_2 in zip(self.devices, other.devices):
            if dev_1 != dev_2:
                logger.warning(f"InputDevices are not equal: {dev_1} != {dev_2}")
                return False
        if len(self.environments) != len(other.environments):
            logger.warning(f"Length of Environments are not equal: {len(self.environments)} !="
                           f" {len(other.environments)}")
            return False
        for env_1, env_2 in zip(self.environments, other.environments):
            if env_1 != env_2:
                logger.warning(f"Environments are not equal: {env_1} != {env_2}")
                return False
        return True

    def __repr__(self):
        return (f'<InputContextRepository: [#context:={len(self.input_contexts)}, '
                f'#providers:={len(self.ink_input_providers)},'
                f' #devices:={len(self.devices)}, #environments:={len(self.environments)}, '
                f'#sensors:={len(self.sensor_contexts)}]>')

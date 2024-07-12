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
import math
import uuid
from enum import Enum
from typing import List, Union, Optional, Any

from uim.model.base import UUIDIdentifier
from uim.model.inkinput.inputdata import InkSensorType, SensorChannel, Unit, unit2unit

logger: logging.Logger = logging.getLogger(__name__)
TOLERANCE_VALUE_COMPARISON: float = 1e-2


class InkState(Enum):
    """
    InkState
    =========
     The Universal Ink Model (UIM) input data state defines the state of the Ink input data.
     UIM supports different modes:

       - Writing on a plane,
       - Hovering above a surface,
       - Moving in air (VR/AR/MR) interaction,
       - Only hovering in the air.
    """
    PLANE = 0              # Ink input data is writing on a surface.
    HOVERING = 1           # Hovering over a surface.
    IN_VOLUME = 2          # Using the uim input data in the air, with active inking.
    VOLUME_HOVERING = 3    # Moving the pen in the air with disabled inking.
    START_TRACKING = 4     # For Hovering and VR entering the proximity sensor needs to be flagged, as well ...
    STOP_TRACKING = 5      # As leaving the proximity sensor respectively VR tracking.


class ChannelData(UUIDIdentifier):
    """
    ChannelData
    ===========

    List of data items.

    Parameters
    ----------
    sensor_channel_id: `uuid.UUID`
        The sensor channel id.
    values:Optional[List[Union[float, int]]] (optional) [default: None]
        List of values. If not provided, an empty list is created.
    """
    def __init__(self, sensor_channel_id: uuid.UUID, values: Optional[List[Union[float, int]]] = None):
        super().__init__(sensor_channel_id)
        self.__values: list = values or []

    @property
    def values(self) -> List[Union[float, int]]:
        """Sample values delta encoded with provided precision. (List[Union[float, int]])"""
        return self.__values

    @values.setter
    def values(self, values: list):
        self.__values = values

    def __dict__(self):
        return {
            'id': str(self.id),
            'values': self.values
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, ChannelData):
            logger.warning(f'Comparing ChannelData with incompatible type: {type(other)}')
            return False
        if self.id != other.id:
            logger.warning(f'Comparing ChannelData with different id: {self.id} != {other.id}')
            return False
        for v_org, v_diff in zip(self.values, other.values):
            if v_org != v_diff:
                logger.warning(f'Comparing ChannelData with different values: {v_org} != {v_diff}')
                return False

    def __repr__(self):
        return f'<ChannelData : [id:={self.id}, num channels:={len(self.values)}]>'


class SensorData(UUIDIdentifier):
    """
    SensorData
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
    """
    def __init__(self, sid: Optional[uuid.UUID] = None, input_context_id: Optional[uuid.UUID] = None,
                 state: Optional[InkState] = None, timestamp: Optional[int] = None):
        super().__init__(sid)
        self.__input_context_id: uuid.UUID = input_context_id
        self.__state: InkState = state
        self.__timestamp: int = timestamp
        self.__map_channels: dict = {}
        self.__map_idx: dict = {}

    @property
    def input_context_id(self) -> uuid.UUID:
        """Id of the input context. (UUID)"""
        return self.__input_context_id

    @input_context_id.setter
    def input_context_id(self, value: uuid.UUID):
        """[WARNING]: Setting the input context id is not recommended."""
        logger.info(f"Setting input context id: {value}")
        self.__input_context_id = value

    @property
    def state(self) -> InkState:
        """State of the uim sensor sequence. (InkState, read-only)"""
        return self.__state

    @property
    def timestamp(self) -> int:
        """Timestamp of the first data sample in this sequence. (int, read-only)"""
        return self.__timestamp

    @property
    def data_channels(self) -> List[ChannelData]:
        """List of the different channels. (List[ChannelData], read-only)"""
        return [self.__map_channels[self.__map_idx[idx]] for idx in sorted(self.__map_idx.keys())]

    def get_data_by_id(self, channel_id: uuid.UUID) -> ChannelData:
        """Returns data channel.

        Parameters
        ----------
        channel_id: `uuid.UUID`
            The sensor channel id.
        Returns
        -------
        ChannelData
            The channel data.
        """
        if channel_id in self.__map_channels:
            return self.__map_channels[channel_id]
        # Create channel data if not existing
        channel: ChannelData = ChannelData(channel_id)
        self.__map_channels[channel_id] = channel
        self.__map_idx[len(self.__map_channels) - 1] = channel_id
        return channel

    def add_timestamp_data(self, sensor_channel: SensorChannel, values: List[float]):
        """
        Adding timestamp data.

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
        """
        if sensor_channel is None:
            raise ValueError("Sensor channel is null")

        if sensor_channel.type != InkSensorType.TIMESTAMP:
            raise ValueError(f"The specified sensor channel must be of the {InkSensorType.TIMESTAMP} type")

        if values is None:
            raise ValueError("Values are null")

        if len(values) == 0:
            return
        channel_data: ChannelData = self.get_data_by_id(sensor_channel.id)
        channel_data.values = values
        self.__timestamp = round(unit2unit(Unit.S, Unit.MS, values[0]))

    def add_data(self, sensor_channel: SensorChannel, values: List[float]):
        """
        Adding data to sensor channel.

        Parameters
        ----------
        sensor_channel: SensorChannel
            Sensor channel.
        values: List[float]
            List of values.
       """
        if sensor_channel is None:
            raise ValueError("Sensor channel is null")

        if values is None:
            raise ValueError("Values are null")

        if len(values) == 0:
            return
        channel_data: ChannelData = self.get_data_by_id(sensor_channel.id)
        channel_data.values = values

    def __dict__(self):
        return {
            'id': str(self.id),
            'input_context_id': str(self.input_context_id),
            'state': self.state.name if self.state is not None else None,
            'timestamp': self.timestamp,
            'data_channels': [dc.__dict__() for dc in self.data_channels]
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other):
        if not isinstance(other, SensorData):
            logger.warning(f'Comparing SensorData with incompatible type: {type(other)}')
            return False
        if len(self.data_channels) != len(other.data_channels):
            logger.warning(f'Comparing SensorData with different number of channels: {len(self.data_channels)} != '
                           f'{len(other.data_channels)}')
            return False
        if self.input_context_id != other.input_context_id:
            logger.warning(f'Comparing SensorData with different input context id: {self.input_context_id} != '
                           f'{other.input_context_id}')
            return False
        if self.id != other.id:
            logger.warning(f'Comparing SensorData with different id: {self.id} != {other.id}')
            return False
        for dc_org, dc_diff in zip(self.data_channels, other.data_channels):
            if dc_org.id != dc_diff.id:
                logger.warning(f'Comparing SensorData with different channel id: {dc_org.id} != {dc_diff.id}')
                return False
            for v_org, v_diff in zip(dc_org.values, dc_diff.values):
                if not math.isclose(v_org, v_diff, abs_tol=TOLERANCE_VALUE_COMPARISON):
                    logger.warning(f'Comparing SensorData with different channel values: {v_org} != {v_diff}')
                    return False
        return True

    def __repr__(self):
        return f'<SensorData : [id:={self.id_h_form}, num channels:={len(self.data_channels)}]>'

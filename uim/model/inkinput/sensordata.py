# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom Authors. All Rights Reserved.
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
import uuid
from enum import Enum
from typing import List

from uim.model.base import UUIDIdentifier
from uim.model.inkinput.inputdata import InkSensorType, SensorChannel, Unit, unit2unit


class InkState(Enum):
    """
         The uim input data state defines the state of the Ink input data.
         WILL 3.0 supports different modes:
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
        List of data items.
    """
    def __init__(self, sensor_channel_id: uuid.UUID, values: list = None):
        """
        Constructs channel data object.
        :param sensor_channel_id: Referencing InkSensorChannel via id.
        :param values: Sample values delta encoded with provided precision.
        """
        super().__init__(sensor_channel_id)
        self.__values: list = values or []

    @property
    def values(self) -> list:
        """Sample values delta encoded with provided precision.

        :return: values
        """
        return self.__values

    @values.setter
    def values(self, values: list):
        self.__values = values

    def __repr__(self):
        return '<ChannelData : [id:={}, num channels:={}]>'.format(self.id, len(self.values))


class SensorData(UUIDIdentifier):
    """
    SensorData
    ----------
    The SensorData Repository is a data repository, which holds a collection of SensorData instances.

    A data-frame structure represents a collection of raw input data sequences, produced by one or more on-board
    device sensors, including data points, re-sampling information, and input sources from fingerprints and metadata.

    Remark:
    --------
    Once a SensorData instance is added to the SensorData repository, it is considered immutable.
    """
    def __init__(self, sid: uuid.UUID = None, input_context_id: uuid.UUID = None, state: InkState = None,
                 timestamp: int = None):
        """
        Constructs a sensor data item.
        :param sid: bytes -
            Sensor data identifier.
        :param input_context_id: bytes -
            Referencing the InputContext via id.
        :param state: InkState -
            The state of the input provider during the capturing of this data frame.
        :param timestamp: int -
            Timestamp for first sample of the stroke, measured in milliseconds.
        """
        super().__init__(sid)
        self.__input_context_id: uuid.UUID = input_context_id
        self.__state: InkState = state
        self.__timestamp: int = timestamp
        self.__map_channels: dict = {}
        self.__map_idx: dict = {}

    @property
    def input_context_id(self) -> uuid.UUID:
        """Id of the input context.

        :return: reference id for the input context
        """
        return self.__input_context_id

    @property
    def state(self) -> InkState:
        """State of the uim sensor sequence.

        :return: InkState enum instance
        """
        return self.__state

    @property
    def timestamp(self) -> int:
        """Timestamp of the first data sample in this sequence.

        :return: long timestamp
        """
        return self.__timestamp

    @property
    def data_channels(self) -> List[ChannelData]:
        """List of the different channels.

        :return: list of DataChannel instances
        """
        return [self.__map_channels[self.__map_idx[idx]] for idx in sorted(self.__map_idx.keys())]

    def get_data_by_id(self, channel_id: uuid.UUID) -> ChannelData:
        """Returns data channel.
        :param channel_id: bytes -
            id of the DataChannel
        :return : data channel
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
        :param sensor_channel: SensorChannel -
            The sensor channel which sourced the data.
        :param values:
            A list of timestamp values with the configured unit type.
        :raises:
            ValueError: Issue with the parameter
        """
        if sensor_channel is None:
            raise ValueError("Sensor channel is null")

        if sensor_channel.type != InkSensorType.TIMESTAMP:
            raise ValueError(f"The specified sensor channel must be of the {InkSensorType.Timestamp} type")

        if values is None:
            raise ValueError()

        if len(values) == 0:
            return
        channel_data: ChannelData = self.get_data_by_id(sensor_channel.id)
        channel_data.values = values
        self.__timestamp = round(unit2unit(Unit.S, Unit.MS, values[0]))

    def add_data(self, sensor_channel: SensorChannel, values: List[float]):
        """
       Adding data.
       :param sensor_channel: SensorChannel -
           The sensor channel which sourced the data.
       :param values:
           A list of values.
       :raises:
           ValueError: Issue with the parameter
       """
        if sensor_channel is None:
            raise ValueError("Sensor channel is null")

        if values is None:
            raise ValueError()

        if len(values) == 0:
            return
        channel_data: ChannelData = self.get_data_by_id(sensor_channel.id)
        channel_data.values = values

    def __eq__(self, other):
        if not isinstance(other, SensorData):
            return False
        if len(self.data_channels) != len(other.data_channels):
            return False
        if self.input_context_id != other.input_context_id:
            return False
        if self.id != other.id:
            return False
        return True

    def __repr__(self):
        return '<SensorData : [id:={}, num channels:={}]>'.format(self.id_h_form, len(self.data_channels))

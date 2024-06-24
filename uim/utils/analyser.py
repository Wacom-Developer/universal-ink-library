# -*- coding: utf-8 -*-
# Copyright © 2023-present Wacom Authors. All Rights Reserved.
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
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

import numpy as np

from uim.model.base import InkModelException
from uim.model.helpers.policy import HandleMissingDataPolicy
from uim.model.ink import InkModel, InkTree, logger
from uim.model.inkdata.strokes import Stroke
from uim.model.inkinput.inputdata import InkSensorType, InputContext, SensorContext, SensorChannel
from uim.model.inkinput.sensordata import SensorData, ChannelData


def safe_zero_div(x: float, y: float) -> float:
    """
    Safely divide two numbers. If the denominator is zero, return zero.
    Parameters
    ----------
    x: float
        Numerator
    y: float
        Denominator

    Returns
    -------
    division: float
        x / y or 0. if y == 0.
    """
    try:
        return x / y
    except ZeroDivisionError:
        return 0.


class ModelAnalyzer(ABC):
    """
    Model analyzer
    ==============

    Abstract class for model analysis.
    """
    KNOWN_TYPE_PREDICATES: List[str] = ["@", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"]
    """Known type predicates"""

    @staticmethod
    @abstractmethod
    def analyze(model: InkModel) -> Dict[str, Any]:
        """
        Analyze the model.
        Parameters
        ----------
        model: InkModel
            Ink model to analyze

        Returns
        -------
        summary: Dict[str, Any]
            Summary of the analysis
        """

    @staticmethod
    def __assume_view_type_predicate__(model: InkModel, view: InkTree) -> Optional[str]:
        statements = model.knowledge_graph.all_statements_for(subject=view.root.uri)
        for statement in statements:
            if statement.predicate in ModelAnalyzer.KNOWN_TYPE_PREDICATES:
                return statement.predicate
        return None

    @staticmethod
    def __extract_sensor_data_info__(model: InkModel, stroke: Stroke, stats: Dict[str, Any]):
        try:
            sd: SensorData = model.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
            ic: InputContext = model.input_configuration.get_input_context(sd.input_context_id)
            sc: SensorContext = model.input_configuration.get_sensor_context(ic.sensor_context_id)
        except InkModelException as e:
            logger.error(f"Error while extracting sensor data info: {e}")
            return

        for scc in sc.sensor_channels_contexts:
            for channel in scc.channels:
                channel: SensorChannel = channel
                channel_type = channel.type
                existing_channel = stats['sensor_channels'].get(channel_type.name)

                if existing_channel is None:
                    stats['sensor_channels'][channel_type.name] = {
                        'strokes_count': 0, 'percent': 0, 'values': [], "metric": channel.metric.name,
                        "resolution": channel.resolution, "precision": channel.precision,
                        "channel_min": channel.min, "channel_max": channel.max
                    }

                stats['sensor_channels'][channel_type.name]['strokes_count'] += 1

                values = sd.get_data_by_id(channel.id).values
                if channel.type == InkSensorType.TIMESTAMP:
                    values = [v + sd.timestamp for v in values]

                stats['sensor_channels'][channel_type.name]['values'].extend(values)

    @staticmethod
    def __post_process_sensor_channels_info__(stats):
        for k, v in stats['sensor_channels'].items():
            stats['sensor_channels'][k]["min"] = min(v['values'])
            stats['sensor_channels'][k]["max"] = max(v['values'])
            stats['sensor_channels'][k]["mean"] = np.mean(v['values'])
            stats['sensor_channels'][k]["median"] = np.median(v['values'])
            stats['sensor_channels'][k].pop('values', None)


def get_channel_data_values(ink_model: InkModel, stroke: Stroke, ink_sensor_type: InkSensorType) -> List[float]:
    """
    Get channel data values for a given stroke and sensor type.
    Parameters
    ----------
    ink_model: InkModel
        Ink model
    stroke: Stroke
        Stroke
    ink_sensor_type: InkSensorType
        Sensor type

    Returns
    -------
    channel_data: List[float]
        Channel data values
    """
    channel_data: Optional[ChannelData] = get_channel_data_instance(ink_model, stroke, ink_sensor_type)
    if channel_data is None:
        return []

    if ink_sensor_type == InkSensorType.TIMESTAMP:
        sd: SensorData = ink_model.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
        return [v + sd.timestamp for v in channel_data.values]
    return channel_data.values.copy()


def get_channel_data_instance(ink_model: InkModel, stroke: Stroke, ink_sensor_type: InkSensorType) \
        -> Optional[ChannelData]:
    """
    Get channel data instance for a given stroke and sensor type.
    Parameters
    ----------
    ink_model: InkModel
        Ink model
    stroke: Stroke
        Stroke
    ink_sensor_type: InkSensorType
        Sensor type

    Returns
    -------
    channel_data: Optional[ChannelData]
        Channel data instance
    """
    sd: SensorData = ink_model.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
    sc: Optional[SensorChannel] = None
    input_context: InputContext = ink_model.input_configuration.get_input_context(sd.input_context_id)
    if input_context is not None:
        sensor_context = ink_model.input_configuration.get_sensor_context(input_context.sensor_context_id)
        if sensor_context is not None:

            if sensor_context.has_channel_type(ink_sensor_type):
                sc = sensor_context.get_channel_by_type(ink_sensor_type)

    if sd is None or sc is None or sd.get_data_by_id(sc.id) is None:
        return None
    return sd.get_data_by_id(sc.id)


def as_strided_array(ink_model: InkModel, stroke: Stroke, handle_missing_data=HandleMissingDataPolicy.FILL_WITH_ZEROS) \
        -> Optional[List[float]]:
    """
    Convert stroke to strided array.

    Parameters
    ----------
    ink_model: InkModel
        Ink model
    stroke: Stroke
        Stroke
    handle_missing_data: HandleMissingDataPolicy
        Handle missing data policy

    Returns
    -------
    points: Optional[List[float]]
        Strided array
    """
    # Remove the first and last element, which are added by the spline producer
    xs: List[float] = stroke.splines_x[1:-1]
    ys: List[float] = stroke.splines_y[1:-1]

    if stroke.sensor_data_id is None:
        ts: List[float] = []
        ps: List[float] = []
    else:
        ts: List[float] = get_channel_data_values(ink_model, stroke, InkSensorType.TIMESTAMP)
        ps: List[float] = get_channel_data_values(ink_model, stroke, InkSensorType.PRESSURE)

    # Handle missing timestamp according to policy
    if len(ts) == 0:
        if handle_missing_data == HandleMissingDataPolicy.FILL_WITH_ZEROS:
            ts = [0 for i in range(len(xs))]
        elif handle_missing_data == HandleMissingDataPolicy.FILL_WITH_NAN:
            NaN = float("nan")
            ts = [NaN for i in range(len(xs))]
        elif handle_missing_data == HandleMissingDataPolicy.SKIP_STROKE:
            return None
        elif handle_missing_data == HandleMissingDataPolicy.THROW_EXCEPTION:
            raise ValueError("There is no timestamp data for this stroke.")

    target_len: int = len(ts) if len(ts) > 0 else len(xs)

    # Handle missing pressure according to policy
    if len(ps) == 0:
        if handle_missing_data == HandleMissingDataPolicy.FILL_WITH_ZEROS:
            ps = [0 for i in range(target_len)]
        elif handle_missing_data == HandleMissingDataPolicy.FILL_WITH_NAN:
            NaN: float = float("nan")
            ps = [NaN for i in range(target_len)]
        elif handle_missing_data == HandleMissingDataPolicy.SKIP_STROKE:
            return None
        elif handle_missing_data == HandleMissingDataPolicy.THROW_EXCEPTION:
            raise ValueError("There is no pressure data for this stroke.")

    xs = xs[0:target_len]
    ys = ys[0:target_len]

    points: List[float] = []

    sensor_data_mapping = stroke.sensor_data_mapping

    if len(sensor_data_mapping) == 0:  # Mapping is 1:1
        limit: int = min(stroke.sensor_data_offset + len(xs), len(ts))
        sensor_data_mapping = range(stroke.sensor_data_offset, limit)

    i: int = 0

    for map_i in sensor_data_mapping:
        points.append(xs[i])
        points.append(ys[i])

        if len(ts) == 0:
            points.append(0)
        else:
            points.append(ts[map_i])

        if len(ps) == 0:
            points.append(0)
        else:
            points.append(ps[map_i])

        i += 1
    return points

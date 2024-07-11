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
import copy
import logging
from collections import defaultdict
from logging import Logger
from typing import List, Tuple, Union, Optional, Dict, Any

import numpy as np

from uim.model.ink import InkModel
from uim.model.inkdata.strokes import InkStrokeAttributeType, Stroke
from uim.model.inkinput.sensordata import InkSensorType

VALUES_SENSOR_ATTRIBUTES: List[int] = list(range(101, 108))
logger: Logger = logging.getLogger(__name__)


class StrokeResamplerInkModelWrapper:
    """
    StrokeResamplerInkModelWrapper
    ==============================
    Class for resampling the ink model.
    """

    def resample_ink_model(self, ink_model: InkModel, points_thresholds: Union[int, List[int]] = 20,
                           curvature_rate_threshold: float = 0.15):
        """Method for resampling the ink model.

        Parameters
        ----------
        ink_model : InkModel
            The ink model to be resampled.
        points_thresholds : Union[int, List[int]], optional
            The number of points in the spline that needs to be reached after running the algorithm.
            If a list is passed, the size should match the number of strokes in the ink model. Defaults to 20.
        curvature_rate_threshold : float, optional
            Before reaching this threshold, we interpolate every piece. Defaults to 0.15.

        Raises
        ------
        ValueError
            When 'points_threshold' is passed as List[int] its size should match ink_model.strokes.
            There is a single threshold per stroke, where the order of the list is taken into account.
            When 'points_threshold' is passed as int, the value is used as threshold for all strokes in the ink model.
        """
        calculator: CurvatureBasedInterpolationCalculator = (
            CurvatureBasedInterpolationCalculator(curvature_rate_threshold=curvature_rate_threshold))
        already_reinitialized: list = []
        if isinstance(points_thresholds, list):
            if len(points_thresholds) != len(ink_model.strokes):
                raise ValueError("When 'points_threshold' is passed as List[int] its size should match "
                                 "ink_model.strokes. There is a single threshold per stroke, where the order of the "
                                 "list is taken into account. When 'points_threshold' is passed as int, the value "
                                 "is used as threshold for all strokes in the ink model.")
        else:
            points_thresholds = [points_thresholds] * len(ink_model.strokes)

        sensor_warning_given: bool = False
        for curr_threshold, stroke in zip(points_thresholds, ink_model.strokes):
            sensor_layout = ink_model.get_sensor_channel_types(stroke)

            # Reinit the sensor channels which are going to be used, if not done already
            for sensor_type in sensor_layout:
                if (sensor_type not in already_reinitialized and
                        InkStrokeAttributeType.get_attribute_type_by_sensor(sensor_type)):
                    if sensor_type in (InkSensorType.X, InkSensorType.Y):
                        continue
                    ink_model.reinit_sensor_channel(sensor_type)
                    already_reinitialized.append(sensor_type)

            # Update layout with spline attributes
            attributes_layout = StrokeResamplerInkModelWrapper.__generate_attributes_layout__(sensor_layout, stroke)

            # Convert to strided array
            strided_array = stroke.as_strided_array_extended(ink_model, layout=attributes_layout)

            # Apply resampling
            calculator.reset_state()
            calculator.layout = attributes_layout
            result_strided_array = SplineHandler.process(
                strided_array, attributes_layout, curr_threshold, calculator)
            # Handling not processed stroke
            if result_strided_array is None:
                logger.debug(f"[WARNING] - Stroke with id {stroke.id} was not processed. Keeping it in original form.")
                continue

            # Convert back strided array back to the ink model.
            self.__populate_stroke_with_strided_array__(
                stroke, ink_model, result_strided_array, sensor_layout, attributes_layout)
            
            # Add warning for mapping
            if stroke.sensor_data_mapping and not sensor_warning_given:
                logger.warning("There are strokes in the model, which have sensor_data_mapping - it is not valid "
                               "because of resampling.")
                sensor_warning_given = True

    def __populate_stroke_with_strided_array__(self, stroke: Stroke, ink_model: InkModel,
                                               result_strided_array: List[float], sensor_layout: List[InkSensorType],
                                               attributes_layout: List[InkStrokeAttributeType]):
        """
        Method for populating the stroke with the strided array.

        Parameters
        ----------
        stroke: Stroke
            The stroke to be populated.
        ink_model: InkModel
            The ink model.
        result_strided_array: List[float]
            The strided array.
        sensor_layout: List[InkSensorType]
            The sensor layout.
        attributes_layout: List[InkStrokeAttributeType]
            The attributes layout.
        """
        attribute_layout_list_values = defaultdict(list)

        for strided_point in zip(*[iter(result_strided_array)] * len(attributes_layout)):
            for idx, attribute_type in enumerate(attributes_layout):
                attribute_layout_list_values[attribute_type].append(strided_point[idx])

        # Process sensor data
        if len(sensor_layout) > 0:
            sd = ink_model.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
            for sensor_type in sensor_layout:
                # All sensor channel data is FLOAT32 with precision 2
                curr_values_channel_data = [round(item, 2) for item in
                                            attribute_layout_list_values[InkStrokeAttributeType.
                                            get_attribute_type_by_sensor(sensor_type)]]
                current_channel = ink_model.get_sensor_channel(stroke, sensor_type)
                if sensor_type == InkSensorType.TIMESTAMP:
                    sd.add_timestamp_data(current_channel, curr_values_channel_data)
                else:
                    sd.add_data(current_channel, curr_values_channel_data)

        # Process spline data
        for attribute_type in attributes_layout:
            if attribute_type.value in VALUES_SENSOR_ATTRIBUTES:
                continue

            curr_values = list(attribute_layout_list_values[attribute_type])
            StrokeResamplerInkModelWrapper.__populate_stroke_per_attribute__(stroke, attribute_type, curr_values)

    @staticmethod
    def __populate_stroke_per_attribute__(stroke: Stroke, attribute_type: InkStrokeAttributeType,
                                          curr_values: List[float]):
        """
        Method for populating the stroke per attribute.
        Parameters
        ----------
        stroke: Stroke
            The stroke to be populated.
        attribute_type: InkStrokeAttributeType
            The attribute type.
        curr_values: List[float]
            The current values.
        """
        # Duplicate first and last
        if attribute_type == InkStrokeAttributeType.SPLINE_X:
            stroke.splines_x = [curr_values[0]]
            stroke.splines_x += curr_values
            stroke.splines_x.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_Y:
            stroke.splines_y = [curr_values[0]]
            stroke.splines_y += curr_values
            stroke.splines_y.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_SIZES:
            stroke.sizes = [curr_values[0]]
            stroke.sizes += curr_values
            stroke.sizes.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_ALPHA:
            stroke.alpha = [curr_values[0]]
            stroke.alpha += curr_values
            stroke.alpha.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_RED:
            stroke.red = [curr_values[0]]
            stroke.red += curr_values
            stroke.red.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_GREEN:
            stroke.green = [curr_values[0]]
            stroke.green += curr_values
            stroke.green.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_BLUE:
            stroke.blue = [curr_values[0]]
            stroke.blue += curr_values
            stroke.blue.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_OFFSETS_X:
            stroke.offsets_x = [curr_values[0]]
            stroke.offsets_x += curr_values
            stroke.offsets_x.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_OFFSETS_Y:
            stroke.offsets_y = [curr_values[0]]
            stroke.offsets_y += curr_values
            stroke.offsets_y.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_SCALES_X:
            stroke.scales_x = [curr_values[0]]
            stroke.scales_x += curr_values
            stroke.scales_x.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_SCALES_Y:
            stroke.scales_y = [curr_values[0]]
            stroke.scales_y += curr_values
            stroke.scales_y.append(curr_values[-1])
        elif attribute_type == InkStrokeAttributeType.SPLINE_ROTATIONS:
            stroke.rotations = [curr_values[0]]
            stroke.rotations += curr_values
            stroke.rotations.append(curr_values[-1])

    @staticmethod
    def __generate_attributes_layout__(sensor_layout: List[InkSensorType], stroke: Stroke)\
            -> List[InkStrokeAttributeType]:
        """
        Method for generating the attributes layout.
        Parameters
        ----------
        sensor_layout: List[InkSensorType]
            The sensor layout.
        stroke: Stroke
            The stroke.

        Returns
        -------
        List[InkStrokeAttributeType]
            The attributes layout.
        """
        attributes_layout: List[InkStrokeAttributeType] = []

        # Handle the case where there is no sensor data
        if len(sensor_layout) == 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_X)
            attributes_layout.append(InkStrokeAttributeType.SPLINE_Y)

        # Map default layout to attributes
        for item in sensor_layout:
            attribute_type = InkStrokeAttributeType.get_attribute_type_by_sensor(item)
            if attribute_type:
                attributes_layout.append(attribute_type)

        if len(stroke.sizes) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_SIZES)
        if len(stroke.alpha) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_ALPHA)
        if len(stroke.red) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_RED)
        if len(stroke.blue) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_BLUE)
        if len(stroke.green) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_GREEN)
        if len(stroke.offsets_x) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_OFFSETS_X)
        if len(stroke.offsets_y) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_OFFSETS_Y)
        if len(stroke.scales_x) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_SCALES_X)
        if len(stroke.scales_y) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_SCALES_Y)
        if len(stroke.rotations) > 0:
            attributes_layout.append(InkStrokeAttributeType.SPLINE_ROTATIONS)

        return attributes_layout


class PolynomialCalculator:
    """
    PolynomialCalculator
    ====================
    Class for calculating the polynomials.
    """
    
    dict_piece_polynomials: Dict[int, Any] = {}
    CATMULL_ROM_MATRIX_POLYNOMIAL_COEFFICIENT_MATRIX = np.array(
        [
            [0.0, -0.5, 1.0, -0.5],
            [1.0, 0.0, -2.5, 1.5],
            [0.0, 0.5, 2.0, -1.5],
            [0.0, 0.0, -0.5, 0.5],
        ],
        dtype=np.float32,
    )

    @staticmethod
    def calculate_polynomials(spline: list, path_piece_index: int, path_stride: int) -> np.array:
        """Method for calculating the polynomials based on the concrete piece of the spline

        Args:
            spline (np.array): The strided array of the spline
            path_piece_index (int): The index of the piece (between two consecutive points)
            path_stride (int): Length of of the stride 
        """
        m_polynomials = PolynomialCalculator.dict_piece_polynomials.get(path_piece_index, None)
        if m_polynomials is not None:
            return m_polynomials

        m_polynomials = np.zeros((path_stride, 4), dtype=np.float32)
        c0 = path_stride * path_piece_index
        c1 = c0 + path_stride
        c2 = c1 + path_stride
        c3 = c2 + path_stride

        for i in range(path_stride):
            m_polynomials[i] = np.dot(
                np.array([spline[c0 + i], spline[c1 + i], spline[c2 + i], spline[c3 + i]]),
                PolynomialCalculator.CATMULL_ROM_MATRIX_POLYNOMIAL_COEFFICIENT_MATRIX,
            )
        PolynomialCalculator.dict_piece_polynomials[path_piece_index] = copy.deepcopy(m_polynomials)
        return m_polynomials


class CurvatureBasedInterpolationCalculator:
    """
    CurvatureBasedInterpolationCalculator
    =====================================
    Class for calculating the interpolated points values based on the curvature rate.
    
    Parameters
    ----------
    curvature_rate_threshold : float, optional
        Before reaching this threshold, we interpolate every piece. Defaults to 0.15.
    """
    
    def __init__(self, curvature_rate_threshold: float = 0.15):
        self.__m_polynomials: Optional[np.ndarray] = None
        self.__list_points_attributes: list = []
        self.__layout: Optional[List[InkStrokeAttributeType]] = None

        self.__curvature_rate_threshold: float = curvature_rate_threshold
        self.__curvature_rate_sq: float = self.__curvature_rate_threshold * self.__curvature_rate_threshold
        self.__curvature_rate_10: float = 10.0 * self.__curvature_rate_threshold

        self.__dict_piece_points: Dict[int, list] = defaultdict(list)
        self.__dict_piece_begin_end_points: Dict[Any, Any] = defaultdict(lambda: defaultdict(dict))

    @property
    def layout(self) -> List[InkStrokeAttributeType]:
        """
        Layout of the spline.
        """
        return self.__layout

    @layout.setter
    def layout(self, value: List[InkStrokeAttributeType]):
        self.__layout = value

    def reset_state(self):
        """
        Reset variables after every spline
        """
        PolynomialCalculator.dict_piece_polynomials = {}
        self.__list_points_attributes = []
        self.__dict_piece_points = defaultdict(list)
        self.__dict_piece_begin_end_points = defaultdict(lambda: defaultdict(dict))

    @property
    def m_polynomials(self) -> np.array:
        """
        Polynomials.
        """
        return self.__m_polynomials

    @m_polynomials.setter
    def m_polynomials(self, value: np.array):
        self.__m_polynomials = value

    @property
    def dict_piece_begin_end_points(self) -> dict:
        """
        Dictionary of the start and end points for each piece.
        """
        return self.__dict_piece_begin_end_points

    def process_xy(self, is_first_piece: bool, is_last_piece: bool, ts: float, tf: float, path_piece_index: int):
        """
        Process the spline for x and y values.
        
        |------|------|------|------|
        b      q1     q2     q3     e
        
        Parameters
        ----------
        is_first_piece: bool
            Is the first piece
        is_last_piece: bool
            Is the last piece
        ts: float
            Start time
        tf: float
            End time
        path_piece_index: int
            Path piece index
        """
        begin_t = ts if is_first_piece else 0.0
        end_t = tf if is_last_piece else 1.0

        # Create begin and end point based on begin_t and end_t
        bx, by, bt, ex, ey, et = self.get_begin_end_points(begin_t, end_t)

        # Subdivide and subdivide recursively till threshold is reached
        q2x, q2y, q2t, is_distance_bigger, sq_diff = self.subdivide_xy(bx, by, bt, ex, ey, et)
        # Use the point for fining the start and end points for the current piece
        self.__add_start_end_interpolated_points_per_piece__(path_piece_index, q2x, q2y, q2t)

        # Append to a List[list], where inner list is one interpolated point
        # with the following ordering: [x,y,curvature_rate,path_piece_index,t]
        self.__list_points_attributes.append([q2x, q2y, sq_diff, path_piece_index, q2t])

        if is_distance_bigger:
            self.__subdivide_recursive_xy(bx, by, bt, q2x, q2y, q2t, path_piece_index)
            self.__subdivide_recursive_xy(q2x, q2y, q2t, ex, ey, et, path_piece_index)

    def get_begin_end_points(self, ts: float, tf: float) -> Tuple[float, float, float, float, float, float]:
        """
        Get the begin and end points based on the start and end time.
        Parameters
        ----------
        ts: float
            Start time
        tf: float
            End time

        Returns
        -------
        Tuple[float, float, float, float, float, float]
            Begin and end points
        """
        # Create begin point
        bx = self.__cubic_calc__(self.__m_polynomials[self.__layout.index(InkStrokeAttributeType.SPLINE_X)], ts)
        by = self.__cubic_calc__(self.__m_polynomials[self.__layout.index(InkStrokeAttributeType.SPLINE_Y)], ts)
        bt = ts

        # Create end point
        ex = self.__cubic_calc__(self.__m_polynomials[self.__layout.index(InkStrokeAttributeType.SPLINE_X)], tf)
        ey = self.__cubic_calc__(self.__m_polynomials[self.__layout.index(InkStrokeAttributeType.SPLINE_Y)], tf)
        et = tf

        return bx, by, bt, ex, ey, et

    def get_begin_end_points_pressure(self, ts: float, tf: float) -> Tuple[float, float, float, float]:
        """
        Get the begin and end points based on the start and end time for pressure.
        Parameters
        ----------
        ts: float
            Start time
        tf: float
            End time

        Returns
        -------
        Tuple[float, float, float, float]
            Begin and end points
        """
        # Create begin point
        bp = self.__cubic_calc__(self.__m_polynomials[self.__layout.index(InkStrokeAttributeType.SENSOR_PRESSURE)], ts)
        # Create end point
        ep = self.__cubic_calc__(self.__m_polynomials[self.__layout.index(InkStrokeAttributeType.SENSOR_PRESSURE)], tf)
        return bp, ts, ep, tf

    def subdivide_linear(self, x1_v: float, x1_t: float, x2_v: float, x2_t: float) -> Tuple[float, float]:
        """
        Subdivide linearly between two points.
        Parameters
        ----------
        x1_v: float
            Value of x1
        x1_t: float
            Time of x1
        x2_v: float
            Value of x2
        x2_t: float
            Time of x2

        Returns
        -------
        Tuple[float, float]
            Interpolated point
        """
        result_t = 0.5 * (x1_t + x2_t)
        result_v = CurvatureBasedInterpolationCalculator.__linear_interpolation__(x1_v, x2_v, result_t)
        return result_v, result_t

    def subdivide_xy(self, bx: float, by: float, bt: float, ex: float, ey: float, et: float,
                     calculate_distance: bool = True)\
            -> Union[Tuple[float, float, float, bool, float], Tuple[float, float, float]]:
        """
        Subdivide the spline between two points.

        Parameters
        ----------
        bx: float
            X of begin point
        by: float
            Y of begin point
        bt: float
            Time of begin point
        ex: float
            X of end point
        ey: float
            Y of end point
        et: float
            Time of end point
        calculate_distance: bool, optional
            Calculate distance. Defaults to True.

        Returns
        -------
        Union[Tuple[float, float, float, bool, float], Tuple[float, float, float]]
            Interpolated point
        """
        tm: float = 0.5 * (bt + et)
        result_x: float = self.__cubic_calc__(self.__m_polynomials[self.__layout.index(InkStrokeAttributeType.SPLINE_X)], tm)
        result_y: float = self.__cubic_calc__(self.__m_polynomials[self.__layout.index(InkStrokeAttributeType.SPLINE_Y)], tm)
        result_t: float = tm

        p0_pos_xy: np.ndarray = np.array([bx, by])
        p1_pos_xy: np.ndarray = np.array([ex, ey])
        res_pos_xy: np.ndarray = np.array([result_x, result_y])

        # Calculate distance between the interpolated point and the line between the two points
        if calculate_distance:
            dist_squared: float = CurvatureBasedInterpolationCalculator.min_distance_squared(p0_pos_xy,
                                                                                             p1_pos_xy, res_pos_xy)

            vm_linear: np.ndarray = 0.5 * (p0_pos_xy + p1_pos_xy)
            diff_x: float = np.abs(result_x - vm_linear[0])
            diff_y: float = np.abs(result_y - vm_linear[1])

            return (
                result_x,
                result_y,
                result_t,
                dist_squared > self.__curvature_rate_sq
                or diff_x > self.__curvature_rate_10
                or diff_y > self.__curvature_rate_10,
                dist_squared,
            )

        return (
            result_x,
            result_y,
            result_t,
        )

    def __subdivide_recursive_xy(self, bx: float, by: float, bt: float, ex: float, ey: float, et: float,
                                 path_piece_index: int):
        """
        Subdivide recursively between two points.
        Parameters
        ----------
        bx: float
            X of begin point
        by: float
            Y of begin point
        bt: float
            Time of begin point
        ex: float
            X of end point
        ey: float
            Y of end point
        et: float
            Time of end point
        path_piece_index: int
            Path piece index
        """
        result_x, result_y, result_t, is_distance_bigger, sq_diff = self.subdivide_xy(
            bx,
            by,
            bt,
            ex,
            ey,
            et,
        )
        self.__add_start_end_interpolated_points_per_piece__(path_piece_index, result_x, result_y, result_t)
        self.__list_points_attributes.append([result_x, result_y, sq_diff, path_piece_index, result_t])

        if is_distance_bigger:
            self.__subdivide_recursive_xy(bx, by, bt, result_x, result_y, result_t, path_piece_index)
            self.__subdivide_recursive_xy(result_x, result_y, result_t, ex, ey, et, path_piece_index)

    def __add_start_end_interpolated_points_per_piece__(self, path_piece_idx: int, result_x: float, result_y: float,
                                                        result_t: float):
        """
        Method for saving the first and last interpolated points for a particular piece ordered based on t.
        The self.__dict_piece_begin_end_points is later used for calculating the curvature_rate of the actual points
        in the spline.

        Parameters
        ----------
        path_piece_idx: int
            Index of the particular piece
        result_x: float
            X of interpolated point
        result_y: float
            Y of interpolated point
        result_t: float
            t of interpolated point
        """
        current_piece_data = self.__dict_piece_begin_end_points.get(path_piece_idx, None)
        if not current_piece_data or self.__dict_piece_begin_end_points[path_piece_idx]["start"].get("t", 0) < result_t:
            self.__dict_piece_begin_end_points[path_piece_idx]["start"]["x"] = result_x
            self.__dict_piece_begin_end_points[path_piece_idx]["start"]["y"] = result_y
            self.__dict_piece_begin_end_points[path_piece_idx]["start"]["t"] = result_t

        if not current_piece_data or self.__dict_piece_begin_end_points[path_piece_idx]["end"].get("t", 1) > result_t:
            self.__dict_piece_begin_end_points[path_piece_idx]["end"]["x"] = result_x
            self.__dict_piece_begin_end_points[path_piece_idx]["end"]["y"] = result_y
            self.__dict_piece_begin_end_points[path_piece_idx]["end"]["t"] = result_t

    def subdivide_pressure(self, bt: float, et: float) -> Tuple[float, float]:
        """
        Subdivide the spline for pressure.

        Parameters
        ----------
        bt: float
            Begin time
        et: float
            End time

        Returns
        -------
        Tuple[float, float]
            Interpolated point
        """
        result_t: float = 0.5 * (bt + et)
        result_v = self.__cubic_calc__(
            self.__m_polynomials[self.__layout.index(InkStrokeAttributeType.SENSOR_PRESSURE)],
            result_t)

        return np.clip(result_v, 0, 1), result_t

    def cubic_calc_angle_based(self, t: float, attribute_type: InkStrokeAttributeType) -> float:
        """
        Calculate the cubic value based on the coefficients and time.

        Parameters
        ----------
        t: float
            Time
        attribute_type: InkStrokeAttributeType
            Attribute type

        Returns
        -------
        float
            The calculated value
        """
        result_v: float = self.__cubic_calc__(self.__m_polynomials[self.__layout.index(attribute_type)], t)
        return result_v

    @property
    def reducing_process_result(self) -> list:
        """
        Reducing process result.
        """
        return self.__list_points_attributes
    
    @property
    def increasing_process_result(self) -> dict:
        """
        Increasing process result.
        """
        return self.__dict_piece_points

    @staticmethod
    def __cubic_calc__(coefs: np.array, t: float) -> float:
        """
        Calculate the cubic value based on the coefficients and time.
        
        Parameters
        ----------
        coefs: np.array
            Coefficients
        t: float
            Time
        Returns
        -------
        float
            The calculated value
        """
        return coefs[0] + coefs[1] * t + coefs[2] * t * t + coefs[3] * t * t * t

    @staticmethod
    def __linear_interpolation__(t1: float, t2: float, t: float) -> float:
        """
        Linear interpolation between two points.
        Parameters
        ----------
        t1: float
            Point 1
        t2: float
            Point 2
        t: float
            Time

        Returns
        -------
        float
            Interpolated value
        """
        return (t2 - t1) * t + t1

    @staticmethod
    def __distance_squared__(vec1: Union[np.array, List[float]], vec2: Union[np.array, List[float]]) -> float:
        """
        Calculate the squared distance between two points.
        Parameters
        ----------
        vec1: Union[np.array, List[float]]
            Vector 1
        vec2: Union[np.array, List[float]]
            Vector 2

        Returns
        -------
        float
            Squared distance
        """
        return (vec1[0]-vec2[0])**2 + (vec1[1]-vec2[1])**2

    @staticmethod
    def min_distance_squared(v: Union[np.array, List[float]], w: Union[np.array, List[float]],
                             p: Union[np.array, List[float]]) -> float:
        """
        Calculate the minimum distance squared between two points.
        Parameters
        ----------
        v: : Union[np.array, List[float]]
            Vector 1
        w: Union[np.array, List[float]]
            Vector 2
        p: Union[np.array, List[float]]
            Vector 3

        Returns
        -------
        float
            Squared distance
        """
        len_2 = CurvatureBasedInterpolationCalculator.__distance_squared__(v, w)
        if len_2 == 0:
            return CurvatureBasedInterpolationCalculator.__distance_squared__(p, v)

        dx_pv = p[0]-v[0]
        dy_pv = p[1]-v[1]
        dx_pw = w[0]-v[0]
        dy_pw = w[1]-v[1]

        dot_product = dx_pv * dx_pw + dy_pv * dy_pw

        t = max(0.0, min(1.0, dot_product / len_2))

        projection_x = v[0] + t * (w[0] - v[0])
        projection_y = v[1] + t * (w[1] - v[1])

        return CurvatureBasedInterpolationCalculator.__distance_squared__(p, [projection_x, projection_y])


class SplineHandler:
    """
    SplineHandler
    =============
    Class with static methods for handling a single spline.
    """

    @staticmethod
    def process(spline_strided_array: List[float], layout: List[InkStrokeAttributeType], points_threshold: int,
                calculator: CurvatureBasedInterpolationCalculator,
                reset_calculator: bool = True) -> List[float]:
        """
        The only public method in the class. This is the only method that needs to be called to process a single spline.

        Parameters
        ----------
        spline_strided_array: List[float]
            The original spline as strided array
        layout: List[InkStrokeAttributeType]:
            List containing all attribute types we process
        points_threshold: int
            Number of points in the spline that needs to be reached after running the algorithm.
        calculator: CurvatureBasedInterpolationCalculator
            Instance of class CurvatureBasedInterpolationCalculator
        reset_calculator: bool  [default: True]
            Automatically reset the calculator so that you don't reset it manually

        Returns
        -------
        List[float]:
            The resulted spline as strided array
        """
        path_stride = len(layout)
        original_points_count = int(len(spline_strided_array) / path_stride)
        pieces_count = original_points_count - 3
        last_piece_index = pieces_count - 1
        calculator.layout = layout
        result_strided_array: Optional[List[float]] = None
        # Check if 4 points are available, if less break
        if original_points_count < 4:
            logger.warning("Stroke requires minimum 4 points to perform resampling. "
                           "Stroke is duplicating first and last point till point threshold is reached!")
            alternate = False
            while len(spline_strided_array) / path_stride < points_threshold:
                if alternate:
                    spline_strided_array = spline_strided_array[:path_stride] + spline_strided_array
                else:
                    spline_strided_array += spline_strided_array[len(spline_strided_array) - path_stride:]
                alternate = not alternate
            
            return spline_strided_array

        if original_points_count == points_threshold:
            logger.debug("Stroke skipped. Stroke has equal number of points to points_threshold.")
            return spline_strided_array

        # Logic for reducing points
        # First process XY, because we interpolate (therefore, decrease/increase points), based solely on them.
        if original_points_count > points_threshold:
            # The interpolated points are saved in calculator.reducing_process_result
            for i in range(pieces_count):
                m_polynomials = PolynomialCalculator.calculate_polynomials(spline_strided_array, i, path_stride)
                calculator.m_polynomials = m_polynomials
                calculator.process_xy(i == 0, i == last_piece_index, 0, 1, i)

            # Calculate the error of the actual points in the original spline
            SplineHandler.__calculate_error_real_points__(spline_strided_array, pieces_count, layout, calculator)
            # Add first and last actual points in the calculator.reducing_process_result
            SplineHandler.__add_first_and_last_points_reducing__(spline_strided_array, layout, calculator)
            # Recalculate the curvature_rate on points removal to reach optimal results
            SplineHandler.__choose_points_based_on_recalculating_error__(calculator, points_threshold)

            # calculate for linear - timestamp
            if InkStrokeAttributeType.SENSOR_TIMESTAMP in layout:
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array,
                    calculator,
                    layout,
                    path_stride,
                    InkStrokeAttributeType.SENSOR_TIMESTAMP,
                )
            # calculate for cubic - pressure
            if InkStrokeAttributeType.SENSOR_PRESSURE in layout:
                SplineHandler.__process_pressure_reducing__(
                    spline_strided_array, calculator, path_stride
                )

            # calculate for angle based - azimuth
            if InkStrokeAttributeType.SENSOR_AZIMUTH in layout:
                lower_boundary = 0
                upper_boundary = 360 * (np.pi/180)
                SplineHandler.__process_angle_based_reducing__(
                    spline_strided_array, calculator, path_stride, InkStrokeAttributeType.SENSOR_AZIMUTH, lower_boundary, upper_boundary
                )

            # calculate for angle based - rotation
            if InkStrokeAttributeType.SENSOR_ROTATION in layout:
                lower_boundary = 0
                upper_boundary = 360 * (np.pi/180)
                SplineHandler.__process_angle_based_reducing__(
                    spline_strided_array, calculator, path_stride, InkStrokeAttributeType.SENSOR_ROTATION,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - altitude
            if InkStrokeAttributeType.SENSOR_ALTITUDE in layout:
                lower_boundary = 0
                upper_boundary = 90 * (np.pi/180)
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SENSOR_ALTITUDE,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - radius x
            if InkStrokeAttributeType.SENSOR_RADIUS_X in layout:
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SENSOR_RADIUS_X
                )

            # calculate for linear - radius y
            if InkStrokeAttributeType.SENSOR_RADIUS_Y in layout:
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SENSOR_RADIUS_Y
                )

            # calculate for linear - sizes
            if InkStrokeAttributeType.SPLINE_SIZES in layout:
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_SIZES
                )

            # calculate for linear - alpha
            if InkStrokeAttributeType.SPLINE_ALPHA in layout:
                lower_boundary = 0
                upper_boundary = 1
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_ALPHA,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - red
            if InkStrokeAttributeType.SPLINE_RED in layout:
                lower_boundary = 0
                upper_boundary = 255
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_RED,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - green
            if InkStrokeAttributeType.SPLINE_GREEN in layout:
                lower_boundary = 0
                upper_boundary = 255
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_GREEN,
                    lower_boundary, upper_boundary
                )
            
            # calculate for linear - blue
            if InkStrokeAttributeType.SPLINE_BLUE in layout:
                lower_boundary = 0
                upper_boundary = 255
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_BLUE,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - offsets_x
            if InkStrokeAttributeType.SPLINE_OFFSETS_X in layout:
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_OFFSETS_X
                )

            # calculate for linear - offsets_y
            if InkStrokeAttributeType.SPLINE_OFFSETS_Y in layout:
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_OFFSETS_Y
                )

            # calculate for linear - scales_x
            if InkStrokeAttributeType.SPLINE_SCALES_X in layout:
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_SCALES_X
                )

            # calculate for linear - scales_y
            if InkStrokeAttributeType.SPLINE_SCALES_Y in layout:
                SplineHandler.__process_linear_reducing__(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_SCALES_Y
                )

            # calculate for angle based - spline rotations
            if InkStrokeAttributeType.SPLINE_ROTATIONS in layout:
                lower_boundary = 0
                upper_boundary = 360 * (np.pi/180)
                SplineHandler.__process_angle_based_reducing__(
                    spline_strided_array, calculator, path_stride, InkStrokeAttributeType.SPLINE_ROTATIONS,
                    lower_boundary, upper_boundary
                )

            result_strided_array = SplineHandler.__generate_spline_reduced_points__(
                                                                calculator.reducing_process_result, layout)

        # Logic for increasing points
        elif original_points_count < points_threshold:
            target_increase_with = points_threshold - original_points_count
            count_interpolated_points = 0
            dict_piece_begin_end_points = defaultdict(list)
            while target_increase_with > count_interpolated_points:
                for i in range(pieces_count):
                    # don't calculate everytime but reuse the polynomial matrices
                    m_polynomials = PolynomialCalculator.calculate_polynomials(spline_strided_array, i, path_stride)
                    calculator.m_polynomials = m_polynomials
                    bx, by, bt, ex, ey, et = SplineHandler.__get_current_begin_end_points__(
                        calculator, dict_piece_begin_end_points, i
                    )
                    result_x, result_y, result_t = calculator.subdivide_xy(
                        bx, by, bt, ex, ey, et, calculate_distance=False
                    )

                    # save the new begins and ends, so we can use them in the next subdivide
                    dict_piece_begin_end_points[i].append((bx, by, bt, result_x, result_y, result_t))
                    dict_piece_begin_end_points[i].append((result_x, result_y, result_t, ex, ey, et))

                    # save the interpolated points in dict with key - piece index and value - list
                    calculator.increasing_process_result[i].append([result_x, result_y, result_t, {}])
                    count_interpolated_points += 1

                    if target_increase_with <= count_interpolated_points:
                        break
            
            # calculate for timestamp
            if InkStrokeAttributeType.SENSOR_TIMESTAMP in layout:
                SplineHandler.__process_linear_increasing(
                    spline_strided_array,
                    calculator,
                    layout,
                    path_stride,
                    InkStrokeAttributeType.SENSOR_TIMESTAMP,
                )
            # calculate for pressure
            if InkStrokeAttributeType.SENSOR_PRESSURE in layout:
                SplineHandler.__process_pressure_increasing__(
                    spline_strided_array,
                    calculator,
                    path_stride,
                )

            # calculate for angle based - azimuth
            if InkStrokeAttributeType.SENSOR_AZIMUTH in layout:
                lower_boundary = 0
                upper_boundary = 360 * (np.pi/180)
                SplineHandler.__process_angle_based_increasing__(
                    spline_strided_array, calculator, path_stride, InkStrokeAttributeType.SENSOR_AZIMUTH,
                    lower_boundary, upper_boundary
                )

            # calculate for angle based - rotation
            if InkStrokeAttributeType.SENSOR_ROTATION in layout:
                lower_boundary = 0
                upper_boundary = 360 * (np.pi/180)
                SplineHandler.__process_angle_based_increasing__(
                    spline_strided_array, calculator, path_stride, InkStrokeAttributeType.SENSOR_ROTATION,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - altitude
            if InkStrokeAttributeType.SENSOR_ALTITUDE in layout:
                lower_boundary = 0
                upper_boundary = 90 * (np.pi/180)
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SENSOR_ALTITUDE,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - radius x
            if InkStrokeAttributeType.SENSOR_RADIUS_X in layout:
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SENSOR_RADIUS_X
                )

            # calculate for linear - radius y
            if InkStrokeAttributeType.SENSOR_RADIUS_Y in layout:
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SENSOR_RADIUS_Y
                )

            # calculate for linear - sizes
            if InkStrokeAttributeType.SPLINE_SIZES in layout:
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_SIZES
                )

            # calculate for linear - alpha
            if InkStrokeAttributeType.SPLINE_ALPHA in layout:
                lower_boundary = 0
                upper_boundary = 1
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_ALPHA,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - red
            if InkStrokeAttributeType.SPLINE_RED in layout:
                lower_boundary = 0
                upper_boundary = 255
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_RED,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - green
            if InkStrokeAttributeType.SPLINE_GREEN in layout:
                lower_boundary = 0
                upper_boundary = 255
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_GREEN,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - blue
            if InkStrokeAttributeType.SPLINE_BLUE in layout:
                lower_boundary = 0
                upper_boundary = 255
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_BLUE,
                    lower_boundary, upper_boundary
                )

            # calculate for linear - offsets_x
            if InkStrokeAttributeType.SPLINE_OFFSETS_X in layout:
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_OFFSETS_X
                )

            # calculate for linear - offsets_y
            if InkStrokeAttributeType.SPLINE_OFFSETS_Y in layout:
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_OFFSETS_Y
                )

            # calculate for linear - scales_x
            if InkStrokeAttributeType.SPLINE_SCALES_X in layout:
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_SCALES_X
                )

            # calculate for linear - scales_y
            if InkStrokeAttributeType.SPLINE_SCALES_Y in layout:
                SplineHandler.__process_linear_increasing(
                    spline_strided_array, calculator, layout, path_stride, InkStrokeAttributeType.SPLINE_SCALES_Y
                )

            # calculate for angle based - spline rotations
            if InkStrokeAttributeType.SPLINE_ROTATIONS in layout:
                lower_boundary = 0
                upper_boundary = 360 * (np.pi/180)
                SplineHandler.__process_angle_based_increasing__(
                    spline_strided_array, calculator, path_stride, InkStrokeAttributeType.SPLINE_ROTATIONS,
                    lower_boundary, upper_boundary
                )

            result_strided_array = SplineHandler.__generate_spline_increased_points__(
                spline_strided_array, calculator.increasing_process_result, path_stride, layout
            )
        if result_strided_array:
            result_strided_array = SplineHandler.__np_to_python_types_checker__(result_strided_array)
            if reset_calculator:
                calculator.reset_state()
        return result_strided_array

    @staticmethod
    def __calculate_error_real_points__(spline_strided_array: List[float], pieces_count: int,
                                        layout: List[InkStrokeAttributeType],
                                        calculator: CurvatureBasedInterpolationCalculator):
        """Method for calculating the curvature_rate of the actual points using the created interpolated points
        in calculator.dict_piece_begin_end_points.

        Parameters
        ----------
        spline_strided_array: List[float])
            The original spline as strided array
        pieces_count: int
            Number of pieces in the spline
        layout: List[InkStrokeAttributeType]
            List containing all attribute types we process
        calculator: CurvatureBasedInterpolationCalculator
            Instance of class CurvatureBasedInterpolationCalculator
        """
        x_index = layout.index(InkStrokeAttributeType.SPLINE_X)
        y_index = layout.index(InkStrokeAttributeType.SPLINE_Y)
        
        piece_idx: int = 0
        for strided_items in zip(*[iter(spline_strided_array[len(layout):-len(layout)])] * len(layout)):
            actual_point = np.array([strided_items[x_index], strided_items[y_index]])
            # Case where we are in the first piece index: 
            # Example: begin_point(first point in the original spline) --- actual point ---
            # end_point(first point for first piece index)
            if piece_idx == 0:
                piece_idx_for_point = piece_idx
                t_for_point = 0
                begin_point = np.array([strided_items[x_index], strided_items[y_index]])
                end_point = np.array([calculator.dict_piece_begin_end_points[piece_idx]["start"]["x"],
                                      calculator.dict_piece_begin_end_points[piece_idx]["start"]["y"]])
            # Case where we are in the last piece index:
            # Example: begin_point(last point in for last piece index) --- actual point ---
            # end_point(last point in the original spline)
            elif piece_idx == pieces_count:
                piece_idx_for_point = piece_idx - 1
                t_for_point = 1
                begin_point = np.array([calculator.dict_piece_begin_end_points[piece_idx-1]["end"]["x"],
                                        calculator.dict_piece_begin_end_points[piece_idx-1]["end"]["y"]])
                end_point = np.array([strided_items[x_index], strided_items[y_index]])
            # Rest of the cases:
            # Example: # Example: begin_point(last point in for previous piece index) --- actual point ---
            # end_point(start point in the current piece index)
            else:
                piece_idx_for_point = piece_idx
                t_for_point = 0
                begin_point = np.array([calculator.dict_piece_begin_end_points[piece_idx-1]["end"]["x"],
                                        calculator.dict_piece_begin_end_points[piece_idx-1]["end"]["y"]])
                end_point = np.array([calculator.dict_piece_begin_end_points[piece_idx]["start"]["x"],
                                      calculator.dict_piece_begin_end_points[piece_idx]["start"]["y"]])
            
            dist_squared = calculator.min_distance_squared(begin_point, end_point, actual_point)
            calculator.reducing_process_result.append([strided_items[x_index], strided_items[y_index],
                                                       dist_squared, piece_idx_for_point, t_for_point])
            
            # Add all other attribute values in a dictionary and append it to the calculator.reducing_process_result
            dict_other_attribute_types = {}
            for attribute_type in layout:
                if attribute_type in (InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y):
                    continue
                dict_other_attribute_types[attribute_type] = strided_items[layout.index(attribute_type)]

            calculator.reducing_process_result[-1].append(dict_other_attribute_types)
            piece_idx += 1
    
    @staticmethod
    def __choose_points_based_on_recalculating_error__(calculator: CurvatureBasedInterpolationCalculator,
                                                       points_threshold: int):

        # Sort in-place by order of the points creation based on two factors: path_piece_index and t
        calculator.reducing_process_result.sort(key=lambda x: (x[3], x[4]))

        while points_threshold != len(calculator.reducing_process_result):
            # Sort by descending order based on curvature rate
            sorted_by_error = sorted(calculator.reducing_process_result, key=lambda x: x[2], reverse=True)
            # Get the (total_len - points_threslhold) points with the lowest curvature rate
            for_removal = sorted(sorted_by_error[points_threshold:len(sorted_by_error)], key=lambda x: (x[3], x[4]))

            # Handle the case when there is only one point to remove
            if len(for_removal) == 1:
                calculator.reducing_process_result.remove(for_removal[0])
                break

            # Go through points for removal two by two and drop the one with lower curvature rate,
            # caring not remove two consecutive points: e.g if p2 is with lowest rate:
            # p1---p2(REMOVE)---p3---p4(REMOVE)---p5---p6(REMOVE)---p7.
            # Removing p2 is not going to change the curvature rates of p4, p6, p8, etc.
            # Only rest of the points will be recalculated
            last_removed = None
            for i in range(1, len(for_removal)):
                a = for_removal[i-1]
                if a == last_removed:
                    continue

                b = for_removal[i]

                to_remove = min(a, b, key=lambda x: x[2])

                calculator.reducing_process_result.remove(to_remove)
                last_removed = to_remove

            # Recalculate curvature rate for the rest of the points
            for i in range(1, len(calculator.reducing_process_result)-1):
                prev_point = calculator.reducing_process_result[i-1][0:2]
                curr_point = calculator.reducing_process_result[i][0:2]
                next_point = calculator.reducing_process_result[i+1][0:2]

                current_point_error = calculator.min_distance_squared(prev_point, next_point, curr_point)
                calculator.reducing_process_result[i][2] = current_point_error

    @staticmethod
    def __process_linear_reducing__(spline_strided_array: List[float],
                                    calculator: CurvatureBasedInterpolationCalculator,
                                    layout: List[InkStrokeAttributeType],
                                    path_stride: int,
                                    attribute_type: InkStrokeAttributeType,
                                    lower_boundary: float = None,
                                    upper_boundary: float = None):
        """
        Method for processing the linear for reducing points.

        Parameters
        ----------
        spline_strided_array: List[float]
            The original spline as strided array
        calculator: CurvatureBasedInterpolationCalculator
            The instance of the CurvatureBasedInterpolationCalculator.
        layout: List[InkStrokeAttributeType]
            The layout of the spline
        path_stride: int
            The stride of the path.
        attribute_type: InkStrokeAttributeType
            The attribute type
        lower_boundary: float [default: None]
            The lower_boundary
        upper_boundary: float [default: None]
            The upper_boundary
        """
        # To save begin, end points in the piece
        dict_piece_begin_end_points = defaultdict(list)

        for idx, point_attributes in enumerate(calculator.reducing_process_result):
            # Case if the point is actual and not interpolated
            if point_attributes[4] == 0 or point_attributes[4] == 1:
                continue
            curr_path_piece_idx = point_attributes[3]
            # Get begin and end indexes for the piece to obtain the values for them
            if curr_path_piece_idx == 0:
                attribute_begin_index = layout.index(attribute_type) + path_stride
                attribute_end_index = attribute_begin_index + path_stride
            else:
                attribute_begin_index = (curr_path_piece_idx * path_stride) + layout.index(attribute_type) + path_stride
                attribute_end_index = attribute_begin_index + path_stride

            start_value, ts, end_value, tf = SplineHandler.__get_current_begin_end_points__(
                calculator,
                dict_piece_begin_end_points,
                curr_path_piece_idx,
                attribute_type,
                spline_strided_array[attribute_begin_index],
                spline_strided_array[attribute_end_index],
            )

            result_v, result_t = calculator.subdivide_linear(start_value, ts, end_value, tf)
            result_v = np.clip(result_v, lower_boundary, upper_boundary) if lower_boundary is not None else result_v

            # Save the new begins and ends, so we can use them in the next subdivide
            dict_piece_begin_end_points[curr_path_piece_idx].append((start_value, ts, result_v, result_t))
            dict_piece_begin_end_points[curr_path_piece_idx].append((result_v, result_t, end_value, tf))
            # Append to the list representing the current point, where the last element is a dictionary for
            # everything except XY.
            if len(point_attributes) != 6:
                calculator.reducing_process_result[idx].append({attribute_type: result_v})
            else:
                calculator.reducing_process_result[idx][-1][attribute_type] = result_v

    @staticmethod
    def __process_linear_increasing(spline_strided_array: List[float],
                                    calculator: CurvatureBasedInterpolationCalculator,
                                    layout: List[InkStrokeAttributeType],
                                    path_stride: int,
                                    attribute_type: InkStrokeAttributeType,
                                    lower_boundary: float = None,
                                    upper_boundary: float = None):
        """
        Method for processing the linear for increasing points.

        Parameters
        ----------
        spline_strided_array: List[float]
            The original spline as strided array
        calculator: CurvatureBasedInterpolationCalculator
            The instance of the CurvatureBasedInterpolationCalculator.
        layout: List[InkStrokeAttributeType]
            The layout of the spline
        path_stride: int
            The stride of the path.
        attribute_type: InkStrokeAttributeType
            The attribute type
        lower_boundary: float [default: None]
            The lower_boundary
        upper_boundary: float [default: None]
            The upper_boundary
        """
        dict_piece_begin_end_points = defaultdict(list)
        attribute_begin_index = layout.index(attribute_type) + path_stride
        attribute_end_index = attribute_begin_index + path_stride

        for piece_idx, list_points_attributes in calculator.increasing_process_result.items():
            for idx, _ in enumerate(list_points_attributes):
                start_value, ts, end_value, tf = SplineHandler.__get_current_begin_end_points__(
                    calculator,
                    dict_piece_begin_end_points,
                    piece_idx,
                    attribute_type,
                    spline_strided_array[attribute_begin_index],
                    spline_strided_array[attribute_end_index],
                )

                result_v, result_t = calculator.subdivide_linear(start_value, ts, end_value, tf)
                result_v = np.clip(result_v, lower_boundary, upper_boundary) if lower_boundary is not None else result_v

                # save the new begins and ends, so we can use them in the next subdivide
                dict_piece_begin_end_points[piece_idx].append((start_value, ts, result_v, result_t))
                dict_piece_begin_end_points[piece_idx].append((result_v, result_t, end_value, tf))

                # Append to the list at the index of the point
                list_points_attributes[idx][-1][attribute_type] = result_v

            attribute_begin_index += path_stride
            attribute_end_index += path_stride

    @staticmethod
    def __process_pressure_reducing__(spline_strided_array: List[float],
                                      calculator: CurvatureBasedInterpolationCalculator,
                                      path_stride: int):
        """
        Method for processing the pressure for reducing points.

        Parameters
        ----------
        spline_strided_array: List[float]
            The original spline as strided array
        calculator: CurvatureBasedInterpolationCalculator
            The instance of the CurvatureBasedInterpolationCalculator.
        path_stride: int
            The stride of the path.
        """
        dict_piece_begin_end_points = defaultdict(list)
        for idx, point_attributes in enumerate(calculator.reducing_process_result):
            if point_attributes[4] == 0 or point_attributes[4] == 1:
                continue
            curr_path_piece_idx = point_attributes[3]
            m_polynomials = PolynomialCalculator.calculate_polynomials(
                spline_strided_array, curr_path_piece_idx, path_stride
            )
            calculator.m_polynomials = m_polynomials

            start_p_v, start_t, end_p_v, end_t = SplineHandler.__get_current_begin_end_points__(
                calculator, dict_piece_begin_end_points, curr_path_piece_idx, InkStrokeAttributeType.SENSOR_PRESSURE
            )

            result_v, result_t = calculator.subdivide_pressure(start_t, end_t)

            # save the new begins and ends, so we can use them in the next subdivide
            dict_piece_begin_end_points[curr_path_piece_idx].append((start_p_v, start_t, result_v, result_t))
            dict_piece_begin_end_points[curr_path_piece_idx].append((result_v, result_t, end_p_v, end_t))

            # save the interpolated points in dict with key - piece index and value - list
            if len(point_attributes) != 6:
                calculator.reducing_process_result[idx].append({InkStrokeAttributeType.SENSOR_PRESSURE: result_v})
            else:
                calculator.reducing_process_result[idx][-1][InkStrokeAttributeType.SENSOR_PRESSURE] = result_v

    @staticmethod
    def __process_pressure_increasing__(
        spline_strided_array: List[float],
        calculator: CurvatureBasedInterpolationCalculator,
        path_stride: int,
    ):
        """
        Method for processing the pressure for increasing points.

        Parameters
        ----------
        spline_strided_array: List[float]
            The original spline as strided array
        calculator: CurvatureBasedInterpolationCalculator
            The instance of the CurvatureBasedInterpolationCalculator.
        path_stride: int
            The stride of the path.
        """
        dict_piece_begin_end_points: Dict[int, list] = defaultdict(list)
        for piece_idx, list_points_attributes in calculator.increasing_process_result.items():
            m_polynomials: np.ndarray = PolynomialCalculator.calculate_polynomials(spline_strided_array, piece_idx,
                                                                                   path_stride)
            calculator.m_polynomials = m_polynomials
            for idx, _ in enumerate(list_points_attributes):

                start_p_v, start_t, end_p_v, end_t = SplineHandler.__get_current_begin_end_points__(
                    calculator, dict_piece_begin_end_points, piece_idx, InkStrokeAttributeType.SENSOR_PRESSURE
                )

                result_v, result_t = calculator.subdivide_pressure(start_t, end_t)

                # save the new begins and ends, so we can use them in the next subdivide
                dict_piece_begin_end_points[piece_idx].append((start_p_v, start_t, result_v, result_t))
                dict_piece_begin_end_points[piece_idx].append((result_v, result_t, end_p_v, end_t))

                # save the interpolated points in dict with key - piece index and value - list
                list_points_attributes[idx][-1][InkStrokeAttributeType.SENSOR_PRESSURE] = result_v

    @staticmethod
    def __process_angle_based_increasing__(spline_strided_array: List[float],
                                           calculator: CurvatureBasedInterpolationCalculator,
                                           path_stride: int,
                                           attribute_type: InkStrokeAttributeType,
                                           lower_boundary: float,
                                           upper_boundary: float):
        """
        Method for processing the angle based attribute for increasing points.

        Parameters
        ----------
        spline_strided_array: List[float]
            The original spline as strided array
        calculator: CurvatureBasedInterpolationCalculator
            The instance of the CurvatureBasedInterpolationCalculator.
        path_stride: int
            The stride of the path.
        attribute_type: InkStrokeAttributeType
            The attribute type.
        lower_boundary: float
            The lower_boundary
        upper_boundary: float
            The upper_boundary
        """
        for curr_path_piece_idx, list_points_attributes in calculator.increasing_process_result.items():
            m_polynomials: np.ndarray = PolynomialCalculator.calculate_polynomials(spline_strided_array,
                                                                                   curr_path_piece_idx,
                                                                                   path_stride)
            calculator.m_polynomials = m_polynomials
            for idx, _ in enumerate(list_points_attributes):
                m_polynomials: np.ndarray = PolynomialCalculator.calculate_polynomials(
                    spline_strided_array, curr_path_piece_idx, path_stride
                )
                calculator.m_polynomials = m_polynomials

                result_v = calculator.cubic_calc_angle_based(list_points_attributes[idx][2], attribute_type)

                # save the interpolated points in dict with key - piece index and value - list
                list_points_attributes[idx][-1][attribute_type] = np.clip(result_v, lower_boundary, upper_boundary)

    @staticmethod
    def __process_angle_based_reducing__(spline_strided_array: List[float],
                                         calculator: CurvatureBasedInterpolationCalculator,
                                         path_stride: int,
                                         attribute_type: InkStrokeAttributeType,
                                         lower_boundary: float,
                                         upper_boundary: float):
        """
        Method for processing the angle based attribute for reducing points.
        Parameters
        ----------
        spline_strided_array: List[float]
            The original spline as strided array
        calculator: CurvatureBasedInterpolationCalculator
            The instance of the CurvatureBasedInterpolationCalculator.
        path_stride: int
            The stride of the path.
        attribute_type: InkStrokeAttributeType
            The attribute type.
        lower_boundary: float
            The lower_boundary
        upper_boundary: float
            The upper_boundary
        """
        for idx, point_attributes in enumerate(calculator.reducing_process_result):
            if point_attributes[4] == 0 or point_attributes[4] == 1:
                continue
            curr_path_piece_idx = point_attributes[3]
            
            m_polynomials = PolynomialCalculator.calculate_polynomials(spline_strided_array, curr_path_piece_idx,
                                                                       path_stride)
            calculator.m_polynomials = m_polynomials

            result_v = calculator.cubic_calc_angle_based(calculator.reducing_process_result[idx][4], attribute_type)

            calculator.reducing_process_result[idx][-1][attribute_type] = np.clip(result_v, lower_boundary,
                                                                                  upper_boundary)

    @staticmethod
    def __get_current_begin_end_points__(calculator: CurvatureBasedInterpolationCalculator,
                                         dict_piece_begin_end_points: dict, path_piece_index: int,
                                         attribute_type: Optional[InkStrokeAttributeType] = None,
                                         ts: float = 0, tf: float = 1) -> tuple:
        """
        Method for getting the current begin and end points for the current piece index.

        Parameters
        ----------
        calculator: CurvatureBasedInterpolationCalculator
            The instance of the CurvatureBasedInterpolationCalculator.
        dict_piece_begin_end_points: dict
            The dictionary with the begin and end points for the current piece index.
        path_piece_index: int
            The current piece index.
        attribute_type: Optional[InkStrokeAttributeType]
            The attribute type.
        ts: float
            The start time.
        tf: float
            The end time.

        Returns
        -------
        tuple
            The tuple with the begin and end points.
        """
        begin_end_points_queue = dict_piece_begin_end_points.get(path_piece_index, None)
        if begin_end_points_queue:
            # Get the current begin and end points, use it as FIFO
            return begin_end_points_queue.pop(0)
        # First time, we need to get begin and end points from the piece itself
        if attribute_type in (InkStrokeAttributeType.SENSOR_TIMESTAMP, InkStrokeAttributeType.SENSOR_ALTITUDE,
                              InkStrokeAttributeType.SENSOR_RADIUS_X, InkStrokeAttributeType.SENSOR_RADIUS_Y,
                              InkStrokeAttributeType.SPLINE_SIZES, InkStrokeAttributeType.SPLINE_ALPHA,
                              InkStrokeAttributeType.SPLINE_RED, InkStrokeAttributeType.SPLINE_GREEN,
                              InkStrokeAttributeType.SPLINE_BLUE, InkStrokeAttributeType.SPLINE_OFFSETS_X,
                              InkStrokeAttributeType.SPLINE_OFFSETS_Y, InkStrokeAttributeType.SPLINE_SCALES_X,
                              InkStrokeAttributeType.SPLINE_SCALES_Y):
            return ts, 0, tf, 1
        if attribute_type == InkStrokeAttributeType.SENSOR_PRESSURE:
            return calculator.get_begin_end_points_pressure(ts, tf)
        return calculator.get_begin_end_points(ts, tf)

    @staticmethod
    def __generate_spline_increased_points__(original_strided_array: List[float], dict_piece_interpolated_points: dict,
                                             path_stride: int, layout: List[InkStrokeAttributeType]) -> List[float]:
        """
        Method for generating the strided array with the increased points.

        Parameters
        ----------
        original_strided_array: List[float]
            The original strided array with the interpolated points.
        dict_piece_interpolated_points: dict
            The dictionary with the interpolated points.
        path_stride: int
            The stride of the path.
        layout: List[InkStrokeAttributeType]
            The layout of the strided array.

        Returns
        -------
        List[float]
            The strided array with the increased points.
        """
        # Iterate the strided array excluding 1st and last point, since we want only the points between the pieces
        piece_idx: int = 0
        result_strided_array: List[float] = []
        for strided_point in zip(*[iter(original_strided_array[path_stride:-path_stride])] * path_stride):
            # O = point from the original strided array
            # O - all interpolated points between these points (in the current piece) -> O - all interpolated points ...
            for idx, attribute_type in enumerate(layout):
                if attribute_type in (InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y):
                    result_strided_array.append(strided_point[idx])
                elif attribute_type == InkStrokeAttributeType.SENSOR_TIMESTAMP:
                    result_strided_array.append(int(strided_point[idx]))
                else:
                    result_strided_array.append(strided_point[idx])

            # Sort by t to create the actual order
            for point_attributes in sorted(dict_piece_interpolated_points[piece_idx], key=lambda x: x[2]):
                for idx, attribute_type in enumerate(layout):
                    if attribute_type in (InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y):
                        result_strided_array.append(point_attributes[idx])
                    elif attribute_type == InkStrokeAttributeType.SENSOR_TIMESTAMP:
                        result_strided_array.append(int(point_attributes[-1][attribute_type]))
                    else:
                        result_strided_array.append(point_attributes[-1][attribute_type])

            piece_idx += 1

        first_strided_point, last_strided_point = SplineHandler.__get_first_and_last_points__(
            original_strided_array, path_stride
        )

        if InkStrokeAttributeType.SENSOR_TIMESTAMP in layout:
            timestamp_index = layout.index(InkStrokeAttributeType.SENSOR_TIMESTAMP)
            first_strided_point[timestamp_index] = int(first_strided_point[timestamp_index])
            last_strided_point[timestamp_index] = int(last_strided_point[timestamp_index])

        result_strided_array = SplineHandler.__add_first_and_last_points_increasing__(
            first_strided_point, last_strided_point, result_strided_array
        )
        return result_strided_array

    @staticmethod
    def __generate_spline_reduced_points__(
        list_interpolated_points: List[list],
        layout: List[InkStrokeAttributeType]
    ) -> List[float]:
        """
        Method for generating the strided array with the reduced points.

        Parameters
        ----------
        list_interpolated_points: List[list]
            The list with the interpolated points.
        layout: List[InkStrokeAttributeType]
            The layout of the strided array.

        Returns
        -------
        List[float]
            The strided array with the reduced points.

        """
        result_strided_array: List[float] = []
        for point_attributes in list_interpolated_points:
            strided_point = []
            for idx, attribute_type in enumerate(layout):
                if attribute_type in (InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y):
                    strided_point.append(point_attributes[idx])
                elif attribute_type == InkStrokeAttributeType.SENSOR_TIMESTAMP:
                    strided_point.append(int(point_attributes[-1][attribute_type]))
                else:
                    strided_point.append(point_attributes[-1][attribute_type])
            
            result_strided_array += strided_point

        return result_strided_array

    @staticmethod
    def __np_to_python_types_checker__(strided_array: List[float]) -> List[float]:
        """
        Method for checking if the float values in the strided array are integers or floats and converting them to
        the correct type.

        Parameters
        ----------
        strided_array: List[float]
            The strided array with the interpolated points.

        Returns
        -------
        List[float]
            The strided array with the interpolated points with the correct types.
        """
        for idx, item in enumerate(strided_array):
            if isinstance(item, (np.float64, np.float32)):
                if not item.is_integer():
                    strided_array[idx] = float(item)
                else:
                    strided_array[idx] = int(item)
        return strided_array

    @staticmethod
    def __get_first_and_last_points__(original_strided_array: List[float], path_stride: int) -> Tuple[list, list]:
        """
        Method for getting the first and last points in the strided array.

        Parameters
        ----------
        original_strided_array: List[float]
            The original strided array with the interpolated points.
        path_stride: int
            The stride of the path.

        Returns
        -------
        Tuple[list, list]
            The first and last points in the strided array.
        """
        return original_strided_array[:path_stride], original_strided_array[-path_stride:]

    @staticmethod
    def __add_first_and_last_points_increasing__(first_strided_point: List[float], last_strided_point: List[float],
                                                 result_strided_array: List[float]) -> List[float]:
        """
        Method for adding the first and last points to the strided array.

        Parameters
        ----------
        first_strided_point: List[float]
            The first point in the strided array.
        last_strided_point: List[float]
            The last point in the strided array.
        result_strided_array: List[float]
            The strided array with the interpolated points.

        Returns
        -------
        List[float]
            The strided array with the first and last points.
        """
        result_strided_array = first_strided_point + result_strided_array + last_strided_point
        return result_strided_array

    @staticmethod
    def __add_first_and_last_points_reducing__(spline_strided_array: List[float], layout: List[InkStrokeAttributeType],
                                               calculator: CurvatureBasedInterpolationCalculator):
        """
        Method for adding the first and last points to the strided array.

        Parameters
        ----------
        spline_strided_array: List[float]
            The original strided array with the interpolated points.
        layout: List[InkStrokeAttributeType]
            The layout of the strided array.
        calculator: CurvatureBasedInterpolationCalculator
            Instance of class CurvatureBasedInterpolationCalculator.
        """
        first_strided_array, last_strided_array = SplineHandler.__get_first_and_last_points__(spline_strided_array,
                                                                                              len(layout))
        # Set curvature_rate = inf and path_piece_index = -inf
        first_point = [
            first_strided_array[layout.index(InkStrokeAttributeType.SPLINE_X)],
            first_strided_array[layout.index(InkStrokeAttributeType.SPLINE_Y)],
            float('inf'), float('-inf'), 0, {}
        ]
        # Set curvature_rate = inf and path_piece_index = inf
        last_point = [
            last_strided_array[layout.index(InkStrokeAttributeType.SPLINE_X)],
            last_strided_array[layout.index(InkStrokeAttributeType.SPLINE_Y)],
            float('inf'), float('inf'), 1, {}
        ]
        for idx, attribute_type in enumerate(layout):
            if attribute_type in (InkStrokeAttributeType.SPLINE_X, InkStrokeAttributeType.SPLINE_Y):
                continue
            first_point[-1][attribute_type] = first_strided_array[idx]
            last_point[-1][attribute_type] = last_strided_array[idx]
        calculator.reducing_process_result.append(first_point)
        calculator.reducing_process_result.append(last_point)

    @staticmethod
    def __strided_test__(spline_num: int, points_threshold: int, result_strided_array: List[float],
                         past_results: List[float], layout: List[InkStrokeAttributeType]):
        """
        Method for testing the strided array.
        Parameters
        ----------
        spline_num: int
            Number of the spline.
        points_threshold: int
            The number of points that should be in the strided array.
        result_strided_array: List[float]
            The strided array with the interpolated points.
        past_results: List[float]
            The past results.
        layout: List[InkStrokeAttributeType]
            The layout of the strided array.
        """

        # Remove sizes
        layout.pop(-1)
        path_stride: int = 5
        idx: int = 5
        for curr_idx, item in enumerate(result_strided_array):
            if curr_idx != 0 and curr_idx % idx == 0:
                result_strided_array.pop(curr_idx)
                curr_idx += idx
        # Testing purposes
        if (points_threshold != (len(result_strided_array) / path_stride) or
                points_threshold != (len(past_results) / path_stride)):
            logger.warning(
                f"Spline num: {spline_num}, points threshold: {points_threshold}, "
                f"actual points current: {len(result_strided_array) / path_stride}, "
                f"actual points past: {(len(past_results) / path_stride)}"
            )

        if past_results is not None:
            idx_past_result = 0
            for strided_items in zip(*[iter(result_strided_array)] * path_stride):
                for idx, item in enumerate(layout):
                    if round(strided_items[idx], 4) != round(past_results[idx_past_result + idx], 4):
                        logger.warning(f"Problem with {item} at point: {idx} | {strided_items[idx]} "
                                       f"and {past_results[idx]}")
                idx_past_result += path_stride
               
    @staticmethod
    def __timestamp_test__(result_strided_array: List[float], layout: List[InkStrokeAttributeType]):
        """
        Method for testing the timestamp values in the strided array.
        Parameters
        ----------
        result_strided_array: List[float]:
            The strided array with the interpolated points.
        layout: List[InkStrokeAttributeType]:
            The layout of the strided array.
        """
        # Testing purposes
        past_strided_items: Optional[List[float]] = None
        idx: int = 0
        for strided_items in zip(*[iter(result_strided_array)] * len(layout)):
            if past_strided_items is None:
                past_strided_items = strided_items
                continue
            
            if (strided_items[layout.index(InkStrokeAttributeType.SENSOR_TIMESTAMP)] -
                    past_strided_items[layout.index(InkStrokeAttributeType.SENSOR_TIMESTAMP)] < 0):
                logger.warning(f"Timestamp problem at point: {idx}")
            past_strided_items = strided_items
            idx += 1

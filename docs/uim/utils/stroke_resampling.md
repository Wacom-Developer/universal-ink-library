Module uim.utils.stroke_resampling
==================================

Classes
-------

`CurvatureBasedInterpolationCalculator(curvature_rate_threshold: float = 0.15)`
:   CurvatureBasedInterpolationCalculator
    =====================================
    Class for calculating the interpolated points values based on the curvature rate.
    
    Parameters
    ----------
    curvature_rate_threshold : float, optional
        Before reaching this threshold, we interpolate every piece. Defaults to 0.15.

    ### Static methods

    `min_distance_squared(v: Union[<built-in function array>, List[float]], w: Union[<built-in function array>, List[float]], p: Union[<built-in function array>, List[float]]) ‑> float`
    :   Calculate the minimum distance squared between two points.
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

    ### Instance variables

    `dict_piece_begin_end_points: dict`
    :   Dictionary of the start and end points for each piece.

    `increasing_process_result: dict`
    :   Increasing process result.

    `layout: List[uim.model.inkdata.strokes.InkStrokeAttributeType]`
    :   Layout of the spline.

    `m_polynomials: <built-in function array>`
    :   Polynomials.

    `reducing_process_result: list`
    :   Reducing process result.

    ### Methods

    `cubic_calc_angle_based(self, t: float, attribute_type: uim.model.inkdata.strokes.InkStrokeAttributeType) ‑> float`
    :   Calculate the cubic value based on the coefficients and time.
        
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

    `get_begin_end_points(self, ts: float, tf: float) ‑> Tuple[float, float, float, float, float, float]`
    :   Get the begin and end points based on the start and end time.
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

    `get_begin_end_points_pressure(self, ts: float, tf: float) ‑> Tuple[float, float, float, float]`
    :   Get the begin and end points based on the start and end time for pressure.
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

    `process_xy(self, is_first_piece: bool, is_last_piece: bool, ts: float, tf: float, path_piece_index: int)`
    :   Process the spline for x and y values.
        
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

    `reset_state(self)`
    :   Reset variables after every spline

    `subdivide_linear(self, x1_v: float, x1_t: float, x2_v: float, x2_t: float) ‑> Tuple[float, float]`
    :   Subdivide linearly between two points.
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

    `subdivide_pressure(self, bt: float, et: float) ‑> Tuple[float, float]`
    :   Subdivide the spline for pressure.
        
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

    `subdivide_xy(self, bx: float, by: float, bt: float, ex: float, ey: float, et: float, calculate_distance: bool = True) ‑> Union[Tuple[float, float, float, bool, float], Tuple[float, float, float]]`
    :   Subdivide the spline between two points.
        
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

`PolynomialCalculator()`
:   PolynomialCalculator
    ====================
    Class for calculating the polynomials.

    ### Class variables

    `CATMULL_ROM_MATRIX_POLYNOMIAL_COEFFICIENT_MATRIX`
    :

    `dict_piece_polynomials: Dict[int, Any]`
    :

    ### Static methods

    `calculate_polynomials(spline: list, path_piece_index: int, path_stride: int) ‑> <built-in function array>`
    :   Method for calculating the polynomials based on the concrete piece of the spline
        
        Args:
            spline (np.array): The strided array of the spline
            path_piece_index (int): The index of the piece (between two consecutive points)
            path_stride (int): Length of of the stride

`SplineHandler()`
:   SplineHandler
    =============
    Class with static methods for handling a single spline.

    ### Static methods

    `process(spline_strided_array: List[float], layout: List[uim.model.inkdata.strokes.InkStrokeAttributeType], points_threshold: int, calculator: uim.utils.stroke_resampling.CurvatureBasedInterpolationCalculator, reset_calculator: bool = True) ‑> List[float]`
    :   The only public method in the class. This is the only method that needs to be called to process a single spline.
        
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

`StrokeResamplerInkModelWrapper()`
:   StrokeResamplerInkModelWrapper
    ==============================
    Class for resampling the ink model.

    ### Methods

    `resample_ink_model(self, ink_model: uim.model.ink.InkModel, points_thresholds: Union[int, List[int]] = 20, curvature_rate_threshold: float = 0.15)`
    :   Method for resampling the ink model.
        
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
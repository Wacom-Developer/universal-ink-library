Module uim.model.helpers.spline
===============================
Spline helpers
==============
Helper functions to interpolate list of coordinates.

Functions
---------

    
`catmull_rom(p_x: List[float], p_y: List[float], res: int = 2) ‑> Tuple[List[float], List[float]]`
:   Computes Catmull-Rom Spline for given support points and resolution.
    
    Parameters
    ----------
    p_x: List[float]
        Array of x-coordinates
    p_y: List[float]
        Array of y-coordinates
    res: int (optional) [default: 2]
        Resolution of a segment (including the start point, but not the endpoint of the segment) in the spline
        (default:= 2)
    
    Returns
    -------
    interp_x: List[float]
        List of interpolated x values
    interp_y: List[float]
        List of interpolated y values
    
    References
    ----------
    - [1] Wikipedia article on Catmull-Rom spline
            URL: https://en.wikipedia.org/wiki/Centripetal_Catmull%E2%80%93Rom_spline

    
`catmull_rom_one_point(x: float, v0: float, v1: float, v2: float, v3: float) ‑> float`
:   Computes interpolated x-coord for given x-coord using Catmull-Rom.
    Computes an interpolated y-coordinate for the given x-coordinate between
    the support points v1 and v2. The neighboring support points v0 and v3 are
    used by Catmull-Rom to ensure a smooth transition between the spline
    segments.
    
    Parameters
    ----------
    x: ´float´
        The x-coord, for which the y-coord is needed
    v0: ´float´
        1st support point
    v1: ´float´
        2nd support point
    v2: ´float´
        3rd support point
    v3: ´float´
        4th support point
    
    Returns
    -------
    coord - ´float´
        Point

    
`linear_interpol(p_x: List[float], p_y: List[float]) ‑> Tuple[List[float], List[float]]`
:   Linear interpolation of the first and the last point in array.
    
    Parameters
    ----------
    p_x: List[float]
        array of x-coordinates
    p_y: List[float]
        array of y-coordinates
    
    Returns
    --------
    interp_x: List[float]
        List of linear interpolated x coordinates
    interp_y: List[float]
        List of linear interpolated x coordinates
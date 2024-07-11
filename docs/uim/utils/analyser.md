Module uim.utils.analyser
=========================

Functions
---------

    
`as_strided_array(ink_model: uim.model.ink.InkModel, stroke: uim.model.inkdata.strokes.Stroke, handle_missing_data=HandleMissingDataPolicy.FILL_WITH_ZEROS) ‑> Optional[List[float]]`
:   Convert stroke to strided array.
    
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

    
`get_channel_data_instance(ink_model: uim.model.ink.InkModel, stroke: uim.model.inkdata.strokes.Stroke, ink_sensor_type: uim.model.inkinput.inputdata.InkSensorType) ‑> Optional[uim.model.inkinput.sensordata.ChannelData]`
:   Get channel data instance for a given stroke and sensor type.
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

    
`get_channel_data_values(ink_model: uim.model.ink.InkModel, stroke: uim.model.inkdata.strokes.Stroke, ink_sensor_type: uim.model.inkinput.inputdata.InkSensorType) ‑> List[float]`
:   Get channel data values for a given stroke and sensor type.
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

    
`safe_zero_div(x: float, y: float) ‑> float`
:   Safely divide two numbers. If the denominator is zero, return zero.
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

Classes
-------

`ModelAnalyzer()`
:   Model analyzer
    ==============
    
    Abstract class for model analysis.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * uim.utils.statistics.StatisticsAnalyzer

    ### Class variables

    `KNOWN_TYPE_PREDICATES: List[str]`
    :   Known type predicates

    ### Static methods

    `analyze(model: uim.model.ink.InkModel) ‑> Dict[str, Any]`
    :   Analyze the model.
        Parameters
        ----------
        model: InkModel
            Ink model to analyze
        
        Returns
        -------
        summary: Dict[str, Any]
            Summary of the analysis
# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom Authors. All Rights Reserved.
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
import datetime
import math
import pathlib
import re
import sys
import time
import uuid
from io import BytesIO
from typing import Any, List, Dict, Tuple, Optional, Union
from xml.etree.ElementTree import tostring

import dateutil.parser
from lxml import etree
from lxml.etree import Element

import uim.model.ink as uim
import uim.model.inkinput.inputdata as device
import uim.model.inkinput.sensordata as sensor
import uim.model.semantics.schema as semantics
from uim import logger
from uim.codec.context.decoder import DecoderContext
from uim.codec.parser.base import FormatException, Parser, SupportedFormats
from uim.model import UUIDIdentifier
from uim.model.inkdata.brush import BrushPolygonUri, VectorBrush, Brush
from uim.model.inkdata.strokes import Style, Stroke, PathPointProperties
from uim.model.semantics.node import BoundingBox, StrokeGroupNode, StrokeNode

# InkML Tags
# ---------------------------------- Annotations -----------------------------------------------------------------------
ANNOTATION_NAME: str = 'name'
ANNOTATION_TYPE: str = 'type'
ANNOTATION_VALUE: str = 'value'
# ---------------------------------- InkML standard tags ---------------------------------------------------------------
XML_NAMESPACE_ID: str = '{http://www.w3.org/XML/1998/namespace}ID'
VALUE: str = 'value'
TIME_STRING: str = 'timeString'
NAME: str = 'name'
UNIT: str = 'unit'
UNITS: str = 'units'
RESOLUTION: str = 'resolution'
TIMESTAMP: str = 'timestamp'
RESPECT_TO: str = 'respectTo'
TYPE: str = 'type'
TIME_OFFSET: str = 'timeOffset'
CONTEXT_REF: str = 'contextRef'
PROPERTIES: str = 'properties'
SAMPLE_RATE: str = 'sample-rate'
INPUT_CONTEXT_ID: str = 'input-context-id'
CHANNEL: str = 'channel'
CHANNELS: str = 'channels'
PEN_DOWN: str = 'penDown'
PEN_UP: str = 'penUp'
# ---------------------------------- InkML tags ------------------------------------------------------------------------
DEPTH: str = 'depth'
METRIC: str = 'metric'
CHANNEL_TYPE: str = 'channel_type'
CHANNEL_RESOLUTION: str = 'channel_resolution'
CHANNEL_MIN: str = 'channel_min'
CHANNEL_MAX: str = 'channel_max'
PRECISION: str = 'precision'
INDEX: str = 'index'
CHANNEL_REF: str = 'channel-ref'
TRACE_DATA_REF: str = 'traceDataRef'
SUBTYPES: str = 'subtypes'
MAPPING: str = 'mapping'
PARENT: str = 'parent'
IDENTIFIER: str = 'id'
# ---------------------------------- Parsing elements ------------------------------------------------------------------
STROKE_IDS: str = 'stroke_ids'
SEMANTICS: str = 'semantics'


class InkMLParserException(FormatException):
    """Exception thrown while parsing InkML file."""


def xml_id(element: Element) -> str:
    """Extract XML ID.
    :param element: Element -
        XML element
    :return : extracted xml id as string
    """
    for el, val in element.attrib.items():
        if IDENTIFIER in el.lower():
            return str(val)
    return f'{id(element)}'


def stringify_children(element: Element):
    """Stringify the children of an XML element.
    :param element: Element -
        XML element
    :return : concatenate all children as string
    """
    content: bytes = tostring(element.getchildren()[0])
    return content.decode("utf-8").replace('\n', ' ').replace('\r', '').replace('\t', '').strip()


def reference_id(ref_id: str) -> str:
    """Extracting reference id.

    Parameters
    ----------
    ref_id: str
        Reference id
    Returns
    -------
    str
        Extracted reference id
    """
    return str(ref_id)[1:] if str(ref_id).startswith('#') else str(ref_id)


class InkMLParser(Parser):
    """
    InkML Parser
    ============
    The InkML parser is used to parse InkML files and convert them into the Universal Ink Model.
    The parser is able to parse the following elements:
    - Annotation
    - AnnotationXML
    - Channel
    - Context
    - ContextGroup
    - Ink (traces and trace groups)
    - Mapping


    Note
    ----
    The parser does not support the complete InkML standard.
    The implementation is tested on different examples from different projects.
    Some parameters have been added to compensate for the missing information in the InkML file.
    The parser is not able to parse all InkML files.

    Example
    -------
    The following example shows how to parse an InkML file:
    >>> from uim.codec.parser.inkml import InkMLParser
    >>> from uim.model.ink import InkModel
    >>> from uim.model.semantics.schema import SegmentationSchema
    >>> parser = InkMLParser()
    >>> # Register type
    >>> parser.register_type('type', 'Document', SegmentationSchema.ROOT)
    >>> parser.register_type('type', 'Formula', SegmentationSchema.MATH_BLOCK)
    >>> parser.register_type('type', 'Arrow', SegmentationSchema.CONNECTOR)
    >>> parser.register_type('type', 'Table', SegmentationSchema.TABLE)
    >>> parser.register_type('type', 'Structure', SegmentationSchema.BORDER)
    >>> parser.register_type('type', 'Diagram', SegmentationSchema.DIAGRAM)
    >>> parser.register_type('type', 'Drawing', SegmentationSchema.DRAWING
    >>> # ... and so on
    >>> # Register value
    >>> parser.register_value('transcription', SegmentationSchema.HAS_CONTENT)
    >>> ink_model: InkModel = parser.parse('../ink/inkml/iamondb.inkml')
    """

    """Constants from InkML codec: https://www.w3.org/TR/InkML/"""
    INKML_NAMESPACE: str = '{http://www.w3.org/2003/InkML}'
    EMPTY_MODIFIER: str = " "
    EXPLICIT_VALUE_MODIFIER: str = "!"
    SINGLE_DIFFERENCE_MODIFIER: str = "'"
    SECOND_DIFFERENCE_MODIFIER: str = '"'
    X_CHANNEL_NAME: str = "X"
    Y_CHANNEL_NAME: str = "Y"
    TIMESTAMP_CHANNEL_NAME: str = "T"
    FORCE_CHANNEL_NAME: str = "F"
    WIDTH_CHANNEL_NAME: str = "F"
    SEPARATION_CHAR: str = ','

    """Conversion function for data types"""
    TYPES_CONVERSION_FUNCTIONS: Dict[device.DataType, Union[int, float, bool]] = {
        device.DataType.FLOAT32: float,
        device.DataType.INT32: int,
        device.DataType.INT64: int,
        device.DataType.FLOAT64: float,
        device.DataType.BOOLEAN: lambda x: True if x == 'T' else False
    }

    """Prefix for the node uri."""
    NODE_URI_PREFIX: str = 'uim:node/{}'
    DEFAULT_PRECISION_VALUE: int = 2
    # Sampling rate of 120 Hz
    DEFAULT_TIME_STEP: float = 1 / 120.

    """Mapping of the data types from InkML to WILL 3 internal representation"""
    MAP_DATA_TYPE: Dict[str, device.DataType] = {
        'decimal': device.DataType.FLOAT32,
        'integer': device.DataType.INT64,
        'double': device.DataType.FLOAT64,
        'boolean': device.DataType.BOOLEAN
    }

    """
    Mapping for the channel names:
    https://www.w3.org/TR/InkML/#channel
    channel name	dimension	default unit	interpretation
        X	        length	mm	X coordinate.   This is the horizontal pen position on the writing surface,
                                                 increasing to the right for +ve orientation.
        Y	        length	mm	Y coordinate.   This is the vertical position on the writing surface,
                                                 increasing downward for +ve orientation.
        Z	        length	mm	Z coordinate.   This is the height of pen above the writing surface,
                                                 increasing upward for +ve orientation.
        F	        force	%	pen tip force
        S	 	                            	 tip switch state (touching/not touching the writing surface)
        B1...Bn	 	 	                        side button states
        OA	angle	deg	                        azimuth angle of the pen (yaw)
        OE	angle	deg	                        elevation angle of the pen (pitch)
        OR	angle	deg	                        rotation (counter-clockwise rotation about pen axis )
        C	 	 	                            color value as an RGB octet triple (i.e. #000000 to #FFFFFF).
        CR,CG,CB	 	 	                    color values (Red/Green/Blue)
        CC,CM,CY,CK	 	 	                    color values (Cyan/Magenta/Yellow/Black)
        A	 	 	                            transparency (ink-specific encoding)
        W	length	mm	                        stroke width (orthogonal to stroke)
        BW	length	mm	                        brush width
        BH	length	mm	                        brush height
        T	time	ms	                        time (of the sample point)
    """
    MAP_CHANNEL_TYPE: Dict[str, device.InkSensorType] = {
        'x': device.InkSensorType.X,
        'y': device.InkSensorType.Y,
        'z': device.InkSensorType.Z,
        't': device.InkSensorType.TIMESTAMP,
        'f': device.InkSensorType.PRESSURE,
        'oa': device.InkSensorType.AZIMUTH,
        'oe': device.InkSensorType.ALTITUDE,
        'or': device.InkSensorType.ROTATION,
        'otx': device.InkSensorType.AZIMUTH,
        'oty': device.InkSensorType.ALTITUDE
    }

    # Mapping of default metrics
    DEFAULT_METRIC_TYPE: Dict[device.InkSensorType, device.InkSensorMetricType] = {
        device.InkSensorType.X: device.InkSensorMetricType.LENGTH,
        device.InkSensorType.Y: device.InkSensorMetricType.LENGTH,
        device.InkSensorType.Z: device.InkSensorMetricType.LENGTH,
        device.InkSensorType.TIMESTAMP: device.InkSensorMetricType.TIME,
        device.InkSensorType.PRESSURE: device.InkSensorMetricType.FORCE,
        device.InkSensorType.AZIMUTH: device.InkSensorMetricType.ANGLE,
        device.InkSensorType.ALTITUDE: device.InkSensorMetricType.ANGLE,
        device.InkSensorType.ROTATION: device.InkSensorMetricType.ANGLE
    }

    # Mapping of default resolutions
    DEFAULT_RESOLUTION: Dict[device.InkSensorType, float] = {
        device.InkSensorType.TIMESTAMP: device.virtual_resolution_for_si_unit(device.Unit.MS),
        device.InkSensorType.PRESSURE: 1.,
        device.InkSensorType.X: 1.,
        device.InkSensorType.Y: 1.
    }

    # Mapping of default unit
    DEFAULT_UNIT: Dict[device.InkSensorType, device.Unit] = {
        device.InkSensorType.TIMESTAMP: device.Unit.MS,
        device.InkSensorType.PRESSURE: device.Unit.PERCENTAGE,
        device.InkSensorType.X: device.Unit.DIP,
        device.InkSensorType.Y: device.Unit.DIP
    }

    # Mapping of precision values
    DEFAULT_PRECISION: Dict[device.InkSensorType, int] = {
        device.InkSensorType.X: 3,
        device.InkSensorType.Y: 3,
        device.InkSensorType.Z: 3,
        device.InkSensorType.TIMESTAMP: 0,
        device.InkSensorType.PRESSURE: 0,
        device.InkSensorType.AZIMUTH: 2,
        device.InkSensorType.ALTITUDE: 2,
        device.InkSensorType.ROTATION: 2
    }

    # Mapping unit types
    MAP_UNIT_TYPE: Dict[str, device.Unit] = {
        'undefined': device.Unit.UNDEFINED,
        'm': device.Unit.M,
        'cm': device.Unit.CM,
        'mm': device.Unit.MM,
        'in': device.Unit.IN,
        'pt': device.Unit.PT,
        'pc': device.Unit.PC,
        'em': device.Unit.UNDEFINED,
        'ex': device.Unit.UNDEFINED,
        'dip': device.Unit.DIP,
        's': device.Unit.S,
        'ms': device.Unit.MS,
        'ns': device.Unit.NS,
        'kg': device.Unit.UNDEFINED,
        'g': device.Unit.UNDEFINED,
        'mg': device.Unit.UNDEFINED,
        'n': device.Unit.N,
        'deg': device.Unit.DEG,
        'rad': device.Unit.RAD,
        '%': device.Unit.PERCENTAGE,
        'dev': device.Unit.UNDEFINED
    }

    # Mapping unit types
    MAP_UNIT_METRIC_TYPE: Dict[device.Unit, device.InkSensorMetricType] = {
        device.Unit.M: device.InkSensorMetricType.LENGTH,
        device.Unit.CM: device.InkSensorMetricType.LENGTH,
        device.Unit.MM: device.InkSensorMetricType.LENGTH,
        device.Unit.IN: device.InkSensorMetricType.LENGTH,
        device.Unit.PT: device.InkSensorMetricType.LENGTH,
        device.Unit.PC: device.InkSensorMetricType.LENGTH,
        device.Unit.DIP: device.InkSensorMetricType.LENGTH,
        device.Unit.S: device.InkSensorMetricType.TIME,
        device.Unit.MS: device.InkSensorMetricType.TIME,
        device.Unit.NS: device.InkSensorMetricType.TIME,
        device.Unit.N: device.InkSensorMetricType.FORCE,
        device.Unit.DEG: device.InkSensorMetricType.ANGLE,
        device.Unit.RAD: device.InkSensorMetricType.ANGLE,
        device.Unit.PERCENTAGE: device.InkSensorMetricType.NORMALIZED
    }

    # Channels required
    REQUIRED_CHANNELS: tuple = (device.InkSensorType.X, device.InkSensorType.Y, device.InkSensorType.TIMESTAMP)
    DEFAULT_CHANNELS: tuple = (device.InkSensorType.X, device.InkSensorType.Y, device.InkSensorType.TIMESTAMP)

    # Bounding box
    MIN_X_TAG: str = 'min_x'
    MAX_X_TAG: str = 'max_x'
    MIN_Y_TAG: str = 'min_y'
    MAX_Y_TAG: str = 'max_y'
    # Artificial timestamps
    ARTIFICIAL_TS_TAG: str = 'artificial_ts'
    DEVICE_CONFIGURATION_FOUND = 'device_configuration_found'
    # Context
    CONTEXT_TAG: str = 'context'
    CURRENT_CONTEXT_TAG: str = 'current_context'
    DEFAULT_CONTEXT_TAG: str = 'default_context'
    # Timestamps
    REFERENCE_TIMESTAMP: str = 'reference_timestamp'
    # Channel
    DATA_TYPE: str = 'data_type'
    # Brush
    BRUSH_URI: str = 'will://ink/vector-brush'
    DEFAULT_SAMPLE_RATE: int = 120

    def __init__(self):
        self.__mapping: Dict[str, device.Unit] = self.MAP_UNIT_TYPE
        self.__value_map: dict = {}
        self.__type_map: dict = {}
        self.__cropping_ink: bool = False
        self.__cropping_offset: int = 0
        self.__default_namespace: str = InkMLParser.INKML_NAMESPACE
        self.__default_sample_rate: int = InkMLParser.DEFAULT_SAMPLE_RATE
        self.__default_device_properties: Dict[str, str] = {}
        self.__default_position_precision: int = 2
        self.__default_value_resolution: float = 1.
        self.__default_annotation_type: Optional[str] = None
        self.__use_brush: str = InkMLParser.BRUSH_URI
        self.DEFAULT_UNIT[device.InkSensorType.X] = device.Unit.DIP
        self.DEFAULT_UNIT[device.InkSensorType.Y] = device.Unit.DIP
        self.DEFAULT_RESOLUTION[device.InkSensorType.X] = 1.
        self.DEFAULT_RESOLUTION[device.InkSensorType.Y] = 1.
        self.__configured_brushes: Dict[str, Brush] = {InkMLParser.BRUSH_URI: InkMLParser.default_brush()}
        self.__content_view: str = semantics.CommonViews.CUSTOM_TREE.value
        self.__type_def_pred: str = semantics.IS

    @property
    def default_namespace(self) -> str:
        """Defines the namespace used within the InkML file."""
        return self.__default_namespace

    @default_namespace.setter
    def default_namespace(self, ns: str):
        self.__default_namespace = ns

    @property
    def default_annotation_type(self) -> Optional[str]:
        """Defines the default annotation type."""
        return self.__default_annotation_type

    @default_annotation_type.setter
    def default_annotation_type(self, value: Optional[str]):
        self.__default_annotation_type = value

    @property
    def value_map(self) -> dict:
        """Defines the annotation types that are added to the Universal Ink Model as value annotations."""
        return self.__value_map

    @property
    def type_map(self) -> dict:
        """Defines the annotation types that are added to the Universal Ink Model as ink type annotations."""
        return self.__type_map

    @property
    def cropping_ink(self) -> bool:
        """Flag if the ink strokes are cropped by min x, min y and the defined offset. (bool, Default: False)"""
        return self.__cropping_ink

    @cropping_ink.setter
    def cropping_ink(self, value: bool):
        self.__cropping_ink = value

    @property
    def cropping_offset(self) -> int:
        """Offset defined, if cropping of ink is enabled. (int, Default: 0)"""
        return self.__cropping_offset

    @cropping_offset.setter
    def cropping_offset(self, value: int):
        self.__cropping_offset = value

    @property
    def use_brush(self) -> str:
        """Use brush. (str, Default: will://ink/vector-brush)"""
        return self.__use_brush

    @use_brush.setter
    def use_brush(self, value: str):
        if value not in self.__configured_brushes:
            raise InkMLParserException(f'Brush with name {value} is not registered.')
        self.__use_brush = value

    @property
    def default_position_precision(self) -> int:
        """Defines precision. (int, Default: 2)"""
        return self.__default_position_precision

    @default_position_precision.setter
    def default_position_precision(self, value: int):
        self.__default_position_precision = value

    @property
    def default_xy_unit(self) -> device.Unit:
        """Default unit of the coordinate channel. (Unit)"""
        return self.DEFAULT_UNIT[device.InkSensorType.X]

    @default_xy_unit.setter
    def default_xy_unit(self, unit: device.Unit):
        self.DEFAULT_UNIT[device.InkSensorType.X] = unit
        self.DEFAULT_UNIT[device.InkSensorType.Y] = unit

    @property
    def default_xy_resolution(self) -> float:
        """Default resolution of the coordinates. Conversion factor to metres. (float)"""
        return self.DEFAULT_RESOLUTION[device.InkSensorType.X]

    @default_xy_resolution.setter
    def default_xy_resolution(self, resolution: float):
        self.DEFAULT_RESOLUTION[device.InkSensorType.X] = resolution
        self.DEFAULT_RESOLUTION[device.InkSensorType.Y] = resolution

    @property
    def default_value_resolution(self) -> float:
        """
        Default resolution of the values. (float). This is used to downscale the values, if there is no resolution
        defined in the InkML file device configuration.
        """
        return self.__default_value_resolution

    @default_value_resolution.setter
    def default_value_resolution(self, resolution: float):
        self.__default_value_resolution = resolution

    @property
    def default_device_properties(self) -> Dict[str, str]:
        """Default device properties. (Dict[str, str])"""
        return self.__default_device_properties

    @property
    def configured_brushes(self) -> Dict[str, Brush]:
        """Configured brushes. (dict)"""
        return self.__configured_brushes

    @property
    def content_view(self) -> str:
        """The annotations are added to this view. (str, Default: CommonViews.CUSTOM_TREE)"""
        return self.__content_view

    @content_view.setter
    def content_view(self, value: str):
        self.__content_view = value

    def register_type(self, inkml_type: str, inkml_value: str, mapping_type: Optional[str] = None,
                      subtypes: Optional[List[Tuple[str, str]]] = None):
        """Register ink type.

        For instance a trace group having a type for the ink labeled and its transcription:

            <ns1:traceGroup xml:id="1">
                ...
                <ns1:annotation type="type">Word</ns1:annotation>
                <ns1:annotation type="transcription">hello</ns1:annotation>
            </ns1:traceGroup>

        So, the type can be registered like this:

            parser.register_type('type', 'Word', 'will:seg/0.2/WordOfStrokes')

        Parameters
        ----------
        inkml_type: str
            InkML type, e.g., 'type'
        inkml_value: str
            InkML value seen in file, e.g., 'Word'
        mapping_type: Optional[str] (optional) [default: None]
            Mapping in UIM Ink Schema, e.g., 'will:seg/0.3/WordOfStrokes', if no type is defined the original value is
            used.
        subtypes: Optional[List[Tuple[str, str]]] (optional) [default: None]
            Defined subtypes. E.g., Marking has sub type such as underlining.

            parser.register_type('type', 'Marking_Underline', 'will:seg/0.2/Marking',
                     subtypes=[('markingType', 'underlining')])
        """
        if inkml_type not in self.__type_map:
            self.__type_map[inkml_type] = {}
        self.__type_map[inkml_type][inkml_value] = {MAPPING: mapping_type, SUBTYPES: subtypes}

    def set_typedef_pred(self, type_def_pred: str):
        """Set type definition predicate.

        Parameters
        ----------
        type_def_pred: str
            Type definition predicate
        """
        self.__type_def_pred = type_def_pred

    def register_value(self, inkml_type: str, mapping: str):
        """Register ink value.

       For instance a trace group having a type for the ink labeled and its transcription:
           <ns1:traceGroup xml:id="1">
               ...
               <ns1:annotation type="type">Word</ns1:annotation>
               <ns1:annotation type="transcription">hello</ns1:annotation>
           </ns1:traceGroup>

       So, the transcription can be registered like this:

            parser.register_value('transcription', Semantics.HAS_CONTENT)

        Parameters
        ----------
        inkml_type: str
           InkML type, e.g., 'transcription'
        mapping: str
           InkML value seen in file, e.g., Semantics.HAS_CONTENT
       """
        self.__value_map[inkml_type] = mapping

    def register_brush(self, brush_uri: str, brush: Brush):
        """If a brush is defined in InkML, the equivalent of WILL 3.0 can be registered.

        Parameters
        ----------
        brush_uri: str
            URI configured within the InkML.
        brush: Brush
            Equivalent WILL 3.0 brush configuration.
        """
        self.__configured_brushes[brush_uri] = brush

    @property
    def default_context(self) -> Dict[str, Any]:
        """Default context defined for the parser.

        Returns
        -------
        dict
            Default context
        """
        return {
            PROPERTIES: self.default_device_properties.copy(),
            CHANNELS: self.default_channels.copy(),
            SAMPLE_RATE: self.__default_sample_rate
        }

    def update_default_context(self, serial_number: Optional[str] = None, manufacturer: Optional[str] = None,
                               model: Optional[str] = None,
                               sample_rate: int = 0):
        """Update the meta data for device.

        Parameters
        ----------
        serial_number: str (optional) [default: None]
            Serial number
        manufacturer: str (optional) [default: None]
            Manufacturer
        model: str (optional) [default: None]
            Model of the device
        sample_rate: int (optional) [default: 0]
            Sample rate
        """
        if sample_rate > 0:
            self.__default_sample_rate = sample_rate
        if serial_number:
            self.__default_device_properties[semantics.DEVICE_SERIAL_NUMBER_PROPERTY] = serial_number
        if manufacturer:
            self.__default_device_properties[semantics.DEVICE_MANUFACTURER_PROPERTY] = manufacturer
        if model:
            self.__default_device_properties[semantics.DEVICE_MODEL_PROPERTY] = model

    @staticmethod
    def __cast__(r_type: device.DataType, value: str) -> Any:
        """Cast value to data type.
        Parameters
        ----------
        r_type: DataType
            Type from InkML
        value: str
            Value as string
        Returns
        -------
        value: Any
            Cast to appropriate data codec
        """
        return InkMLParser.TYPES_CONVERSION_FUNCTIONS[r_type](value)

    @classmethod
    def __parse_samples__(cls, context: DecoderContext, tr_id: str, tr_ctx_id: str, trace_data: str,
                          time_offset: int = 0, default_value_resolution: float = 1., hover: bool = False):
        """Parse samples (traces) from InkML file.

        Parameters
        ----------
        context: DecoderContext
            Decoder context
        tr_id: str
            Trace id
        tr_ctx_id: str
            Trace context id
        trace_data: str
            Trace data
        time_offset: int (optional) [default: 0]
            Time offset
        default_value_resolution: float (optional) [default: 1.]
            Default value resolution
        hover: bool
            The trace is hover data
        """
        # Channel indices for x, y coordinate
        # Default: Assumption channel order: x,y,t
        x_index: int = 0
        y_index: int = 1
        t_index: int = 2
        f_index: int = 0
        z_index: int = 0
        azimuth_index: int = 0
        altitude_index: int = 0
        xs: List[float] = []
        ys: List[float] = []
        spline_x: List[float] = []
        spline_y: List[float] = []
        fs: List[float] = []
        ts: List[float] = []
        zs: List[float] = []
        azimuth: List[float] = []
        altitude: List[float] = []

        regex: re.Pattern[str] = re.compile(r"-?\d+(?:\.\d+)?|'[^']*'|\"[^\"]*\"")

        # Current context
        current: str = context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG]
        # If there is a reference timestamp set
        reference_timestamp = 0
        if tr_ctx_id:
            context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG] = str(tr_ctx_id)[1:] \
                if str(tr_ctx_id).startswith('#') else str(tr_ctx_id)
        if context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG] \
                in context.decoder_map[InkMLParser.CONTEXT_TAG]:
            ctx: dict = context.decoder_map[InkMLParser.CONTEXT_TAG][current]
        else:
            ctx: dict = context.decoder_map[InkMLParser.CONTEXT_TAG][InkMLParser.DEFAULT_CONTEXT_TAG]
        # Timestamp
        channel_timestamp: dict = InkMLParser.__context_get__(ctx[CHANNELS], device.InkSensorType.TIMESTAMP)
        # Pen Orientation
        channel_azimuth: dict = InkMLParser.__context_get__(ctx[CHANNELS], device.InkSensorType.AZIMUTH)
        channel_altitude: dict = InkMLParser.__context_get__(ctx[CHANNELS], device.InkSensorType.ALTITUDE)
        # At minimum we have two channels: x,y coordinates
        num_channels: int = 2
        if channel_timestamp:
            t_index = channel_timestamp[INDEX]
            # Relative timestamp with respect to reference timestamp
            if RESPECT_TO in channel_timestamp:
                # get reference id from timestamp
                ref: str = reference_id(channel_timestamp[RESPECT_TO])
                if InkMLParser.REFERENCE_TIMESTAMP in ctx:
                    reference_timestamp = ctx[InkMLParser.REFERENCE_TIMESTAMP][ref]
            num_channels += 1
        channel_force = InkMLParser.__context_get__(ctx[CHANNELS], device.InkSensorType.PRESSURE)
        # Handle force, if available
        if channel_force:
            f_index = channel_force[INDEX]
            num_channels += 1
        # Handle z, if available
        channel_z: dict = InkMLParser.__context_get__(ctx[CHANNELS], device.InkSensorType.Z)
        if channel_z:
            z_index = channel_z[INDEX]
            num_channels += 1
        # Handle azimuth, if available
        if channel_azimuth:
            azimuth_index = channel_azimuth[INDEX]
            num_channels += 1
        # Handle altitude, if available
        if channel_altitude:
            altitude_index = channel_altitude[INDEX]
            num_channels += 1
        # Strip data
        points_data: List[str] = InkMLParser.__clean__(trace_data).split(InkMLParser.SEPARATION_CHAR)
        modifier: str = InkMLParser.EMPTY_MODIFIER
        last_values: List[float] = []
        difference_vector: List[float] = [0 for _ in range(num_channels)]
        last_differences: list = difference_vector[:]
        last_modifier = modifier
        point_index: int = 1
        channel_x: dict = InkMLParser.__context_get__(ctx[CHANNELS], device.InkSensorType.X)
        channel_y: dict = InkMLParser.__context_get__(ctx[CHANNELS], device.InkSensorType.Y)
        # Delta encoded data
        # From specification:
        # Regular channels may be reported as explicit values, differences, or second differences: Prefix symbols are
        # used to indicate the interpretation of a value: a preceding exclamation point (!) indicates an explicit value,
        # a single quote (') indicates a single difference, and a double quote prefix (") indicates a second difference.
        # If there is no prefix, then the channel value is interpreted as explicit, difference, or second difference
        # based on the last prefix for the channel. If there is no last prefix, the value is interpreted as explicit.
        for segment in points_data:
            channels_values: list = []
            modifier: str = InkMLParser.EMPTY_MODIFIER
            # Find all matches in the current segment
            matches = regex.findall(segment)
            # only the first match contains the modifier
            for point in matches:
                if point.find(InkMLParser.EXPLICIT_VALUE_MODIFIER) == 0:
                    modifier = InkMLParser.EXPLICIT_VALUE_MODIFIER
                    break
                elif point.find(InkMLParser.SINGLE_DIFFERENCE_MODIFIER) == 0:
                    modifier = InkMLParser.SINGLE_DIFFERENCE_MODIFIER
                    break
                elif point.find(InkMLParser.SECOND_DIFFERENCE_MODIFIER) == 0:
                    modifier = InkMLParser.SECOND_DIFFERENCE_MODIFIER
                    break
                else:
                    modifier = last_modifier
            channels_values = [InkMLParser.__remove_modifier__(v) for v in matches]
            values: List[float] = []
            # Iterate over channel values
            for i, channel_value_str in enumerate(channels_values):
                if i in ctx[CHANNELS]:
                    sensor_channel: Dict[str, Any] = ctx[CHANNELS][i]
                    if context.decoder_map[InkMLParser.DEVICE_CONFIGURATION_FOUND]:
                        # In InkML the resolution is the conversion factor to unit that is defined in
                        # device configuration
                        # For instance, if the unit is mm for the channel is defined and a resolution of 100 is defined:
                        # <inkml:channelProperty channel = "X" name = "resolution" value = "100" units = "1/mm" />
                        # then the value is converted to mm by dividing by 100
                        if RESOLUTION in sensor_channel:
                            resolution = sensor_channel[RESOLUTION]
                        else:
                            # If the device configuration is not found, then the default resolution is used
                            resolution = default_value_resolution
                    else:
                        # If the device configuration is not found, then the default resolution is used
                        resolution = default_value_resolution
                    channel_value = InkMLParser.__cast__(sensor_channel[InkMLParser.DATA_TYPE],
                                                         InkMLParser.__remove_modifier__(channel_value_str))
                    # Convert to SI unit by dividing by resolution value
                    # The resolution value is the conversion factor to the SI unit
                    channel_value /= resolution   # Normalize to unit of the channel
                    # Now, convert to the unit defined in the channel to SI unit
                    channel_value = device.unit2unit(sensor_channel[UNIT], device.si_unit(sensor_channel[UNIT]),
                                                     channel_value)
                    # Single difference modifier is the difference between the current and the last value
                    if modifier == InkMLParser.SINGLE_DIFFERENCE_MODIFIER:
                        value = last_values[i] + channel_value
                        last_differences[i] += channel_value
                    # Second difference modifier is the difference between the current and the last difference
                    elif modifier == InkMLParser.SECOND_DIFFERENCE_MODIFIER:
                        value = last_values[i] + (last_differences[i] + channel_value)
                        last_differences[i] += channel_value
                    else:
                        value = channel_value
                        last_differences = difference_vector[:]

                    last_modifier = modifier
                    values.append(value)
                else:
                    values.append(0)

            last_values = values
            # Concatenate x and y values
            xs.append(values[x_index])
            ys.append(values[y_index])
            if channel_z:
                zs.append(values[z_index])
            # Based on the specification of UIM the values are in SI unit in memory and are serialized original unit
            # The splines coordinates are in DIP unit
            spline_x.append(device.unit2unit(device.Unit.M, device.Unit.DIP, values[x_index]))
            spline_y.append(device.unit2unit(device.Unit.M, device.Unit.DIP, values[y_index]))

            # Optional channels which are not provided in all cases
            if channel_force:
                value = values[f_index]
                fs.append(value)
            if channel_azimuth:
                azimuth.append(values[azimuth_index])
            if channel_altitude:
                altitude.append(values[altitude_index])

            if channel_timestamp:
                if context.decoder_map[InkMLParser.ARTIFICIAL_TS_TAG] or t_index >= len(values):
                    ts.append(int(time_offset + point_index * InkMLParser.DEFAULT_TIME_STEP * 1000))
                else:
                    try:
                        ts.append(reference_timestamp + time_offset + values[t_index])
                    except Exception as e:
                        logger.error(f'Error in parsing timestamp: {e}')
                point_index += 1

        # Length of spline must be at least 4
        if len(spline_x) == 1:
            spline_x.append(spline_x[0] + 1.)
            spline_y.append(spline_y[0] + 1.)
        # Update bounding box
        context.decoder_map[InkMLParser.MAX_X_TAG] = max(context.decoder_map[InkMLParser.MAX_X_TAG], max(spline_x))
        context.decoder_map[InkMLParser.MAX_Y_TAG] = max(context.decoder_map[InkMLParser.MAX_Y_TAG], max(spline_y))
        context.decoder_map[InkMLParser.MIN_X_TAG] = min(context.decoder_map[InkMLParser.MIN_X_TAG], min(spline_x))
        context.decoder_map[InkMLParser.MIN_Y_TAG] = min(context.decoder_map[InkMLParser.MIN_Y_TAG], min(spline_y))
        # Add extract control point in the beginning
        spline_x.insert(0, spline_x[0])
        spline_y.insert(0, spline_y[0])
        # and at the end
        spline_x.append(spline_x[-1])
        spline_y.append(spline_y[-1])
        # Adding sensor data
        if hover:
            sensor_data: sensor.SensorData = sensor.SensorData(input_context_id=ctx[INPUT_CONTEXT_ID],
                                                               state=sensor.InkState.HOVERING)
        else:
            sensor_data: sensor.SensorData = sensor.SensorData(input_context_id=ctx[INPUT_CONTEXT_ID],
                                                               state=sensor.InkState.PLANE)

        stroke_data: Stroke = Stroke(sensor_data_id=sensor_data.id, style=InkMLParser.style())
        # Spline data
        stroke_data.splines_x = spline_x
        stroke_data.splines_y = spline_y
        stroke_data.end_parameter = 1.
        stroke_data.sizes = [1.] * len(spline_x)
        stroke_data.offset_x = [1.] * len(spline_x)
        stroke_data.offset_y = [1.] * len(spline_x)
        # Adding sensor data channels
        sensor_data.add_data(channel_x[CHANNEL_REF], xs)
        sensor_data.add_data(channel_y[CHANNEL_REF], ys)
        if channel_timestamp:
            sensor_data.add_timestamp_data(channel_timestamp[CHANNEL_REF], ts)
        if channel_z:
            sensor_data.add_data(channel_z[CHANNEL_REF], zs)
        if channel_force:
            sensor_data.add_data(channel_force[CHANNEL_REF], fs)
        if channel_azimuth:
            sensor_data.add_data(channel_azimuth[CHANNEL_REF], azimuth)
        if channel_altitude:
            sensor_data.add_data(channel_altitude[CHANNEL_REF], altitude)
        # Adding sensor data
        context.ink_model.sensor_data.add(sensor_data)
        if not hover:
            context.register_stroke(stroke_data, tr_id)

    @classmethod
    def __trace_view__(cls, context: DecoderContext, trace_view: Element, namespace: str):
        """
        Parse trace view.

        Parameters
        ----------
        context: DecoderContext
            Decoder context
        trace_view: Element
            Trace view element
        namespace: str
            Namespace
        """
        path_ids: List[str] = []
        annotations: list = []
        for tv in trace_view.findall(f'./{namespace}traceView'):
            if TRACE_DATA_REF in tv.attrib:
                trace_id_ref: str = tv.attrib[TRACE_DATA_REF]
                ref: str = reference_id(trace_id_ref)
                if context.is_stroke_registered(ref):
                    if ref in path_ids:
                        raise InkMLParserException('Element already exists.')
                    path_ids.append(ref)

        for a in trace_view.findall(f'./{namespace}annotation'):
            a_type: str = a.attrib[ANNOTATION_TYPE]
            a_value: str = a.text.strip()
            annotations.append({ANNOTATION_TYPE: a_type, ANNOTATION_VALUE: a_value})
        context.decoder_map[SEMANTICS].append(
            {
                IDENTIFIER: 'df', PARENT: None, SEMANTICS: annotations, STROKE_IDS: path_ids,
                DEPTH: 1, INDEX: 1
            })

    @classmethod
    def __trace_group__(cls, context: DecoderContext, trace_group: Element, trace_counter: int = 0,
                        tg_counter: int = 0, parent_id: Optional[str] = None, depth: int = 0,
                        namespace: str = '{http://www.w3.org/2003/InkML}', default_value_resolution: float = 1.):
        """
        Parse trace group.

        Parameters
        ----------
        context: DecoderContext
            Decoder context
        trace_group: Element
            Trace group element
        trace_counter: int (optional) [default: 0]
            Trace counter
        tg_counter: int (optional) [default: 0]
            Trace group counter
        parent_id: Optional[str] (optional) [default: None]
            Parent id
        depth: int (optional) [default: 0]
            Depth
        namespace: str (optional) [default: '{http://www.w3.org/2003/InkML}']
            Namespace used by parser
        default_value_resolution: float (optional) [default: 1.]
            Default value resolution
        """
        trace_ids: List[str] = []
        path_ids: List[str] = []
        # Check if context is set
        if CONTEXT_REF in trace_group.attrib:
            context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG] = trace_group.attrib[CONTEXT_REF]

        tg_id: str = xml_id(trace_group)
        for tv in trace_group.findall(f'./{namespace}traceView'):
            if TRACE_DATA_REF in tv.attrib:
                ref: str = tv.attrib[TRACE_DATA_REF]

                if ref in path_ids:
                    raise Exception('Element already exists.')

                path_ids.append(reference_id(ref))

        # Iterate over traces
        for tr in trace_group.findall(f'./{namespace}trace'):
            tr_id: str = xml_id(tr)

            if tr_id in trace_ids:
                raise Exception('Element already exists.')

            trace_ids.append(tr_id)

            ctx_id: str = tr.attrib[CONTEXT_REF] if CONTEXT_REF in tr.attrib \
                else context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG]
            InkMLParser.__parse_samples__(context, tr_id, ctx_id, tr.text,
                                          default_value_resolution=default_value_resolution)
            trace_counter += 1

        annotations: list = []
        # Iterate over annotations
        for a in trace_group.findall(f'./{namespace}annotation'):
            a_type: str = a.attrib[ANNOTATION_TYPE]
            a_value: str = a.text.strip()
            annotations.append({ANNOTATION_TYPE: a_type, ANNOTATION_VALUE: a_value})

        context.decoder_map[SEMANTICS].append(
            {
                IDENTIFIER: tg_id, PARENT: parent_id, SEMANTICS: annotations, STROKE_IDS: trace_ids, DEPTH: depth,
                INDEX: tg_counter
            }
        )
        # Iterate over sub-nodes
        for tg in trace_group.findall(f'./{namespace}traceGroup'):
            trace_counter = InkMLParser.__trace_group__(context, tg, trace_counter, tg_counter, tg_id, depth=depth + 1)
            tg_counter += 1
        return tg_counter

    @classmethod
    def __handle_ink_source__(cls, context: DecoderContext, ink_source: Element, ctx_id: str,
                              namespace: str = '{http://www.w3.org/2003/InkML}'):
        """
        Handle the ink source configuration.

        Parameters
        ----------
        context: DecoderContext
            Decoder context containing the current parsing state.
        ink_source: Element
            Ink source element
        ctx_id: str
            Context id
        namespace: str (optional) [default: '{http://www.w3.org/2003/InkML}']
            Namespace used by parser
        """
        sample_rate: int = InkMLParser.DEFAULT_SAMPLE_RATE
        sample_rate_obj: Element = ink_source.find(f'{namespace}sampleRate')
        # Get sample rate
        if sample_rate_obj is not None:
            if VALUE in sample_rate_obj.attrib:
                sample_rate = int(float(sample_rate_obj.attrib[VALUE]))
        try:
            if ctx_id in context.decoder_map[InkMLParser.CONTEXT_TAG]:
                props: dict = {}
                if 'serialNo' in ink_source.attrib:
                    # Adding properties
                    props[semantics.DEVICE_SERIAL_NUMBER_PROPERTY] = ink_source.attrib['serialNo']
                if 'manufacturer' in ink_source.attrib:
                    props[semantics.DEVICE_MANUFACTURER_PROPERTY] = ink_source.attrib['manufacturer']
                if 'model' in ink_source.attrib:
                    props[semantics.DEVICE_MODEL_PROPERTY] = ink_source.attrib['model']

                context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id][PROPERTIES] = props
                context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id][SAMPLE_RATE] = sample_rate
                context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id][CHANNELS] = {}
                # Iterate the channels
                trace_format: Element = ink_source.find(f'./{namespace}traceFormat')
                if trace_format is not None:
                    InkMLParser.__trace_format__(context, ctx_id, trace_format, namespace)
                # Iterate over properties
                channel_properties: Element = ink_source.find(f'./{namespace}channelProperties')
                if channel_properties is not None:
                    InkMLParser.__channel_properties__(context, ctx_id, channel_properties, namespace)
            else:
                logger.warning(f"Context with id:={ctx_id} does not exist.")

        except Exception as e:
            logger.error(e)

    @classmethod
    def __collect_channels__(cls, context: DecoderContext, root: Element, namespace: str, default_sample_rate: int):
        """Collects channel information.

        Parameters
        ----------
        root: Element
            Root element of InkMLObject
        namespace: str
            Namespace used by parser
        """
        for c in root.findall(f'.//{namespace}context'):
            ctx_id: str = xml_id(c)
            # Set current context
            context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG] = ctx_id
            context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id] = {}
            context_timestamp = c.find(f'.//{namespace}timestamp')
            if context_timestamp is not None:
                # Respective timestamp
                ts_id: str = xml_id(context_timestamp)

                if TIME_STRING in context_timestamp.attrib:
                    ts: datetime = dateutil.parser.parse(context_timestamp.attrib[TIME_STRING])
                    if InkMLParser.REFERENCE_TIMESTAMP not in context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id]:
                        context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id][InkMLParser.REFERENCE_TIMESTAMP] = {}
                    context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id][InkMLParser.REFERENCE_TIMESTAMP][ts_id] \
                        = ts.timestamp()
            # Ink source
            ink_source: Element = c.find(f'{namespace}inkSource')
            if ink_source is not None:
                context.decoder_map[InkMLParser.DEVICE_CONFIGURATION_FOUND] = True
                InkMLParser.__handle_ink_source__(context, ink_source, ctx_id)
        # Handle the devices
        for ink_source in root.findall(f'.//{namespace}inkSource'):
            context.decoder_map['device_configuration_found'] = True
            InkMLParser.__handle_ink_source__(context, ink_source,
                                              context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG])
        # Finally check for trace codec
        if len(context.decoder_map) == 0:
            trace_format: Element = root.find(f'.{namespace}traceFormat')
            if trace_format is not None:
                context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG] = InkMLParser.DEFAULT_CONTEXT_TAG
                context.decoder_map[InkMLParser.CONTEXT_TAG][context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG]] = \
                    {
                        CHANNELS: {}, PROPERTIES: {}, SAMPLE_RATE: default_sample_rate
                    }
                InkMLParser.__trace_format__(context, context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG],
                                             trace_format, namespace)

    @classmethod
    def __collect_ink__(cls, context: DecoderContext, inkml_obj: Element, namespace: str, brush: Brush,
                        cropping: bool = False, cropping_offset: int = 0, default_value_resolution: float = 1.,
                        type_def_pred: str = semantics.IS):
        """Collect input data from InkML object.
        Parameters
        ----------
        context: DecoderContext
            Decoder context containing the current parsing state.
        inkml_obj: Element
            InkML object
        namespace: str
            Namespace used by parser
        brush: Brush
            The brush configuration
        cropping: bool (optional) [default: False]
            Flag if cropping is enabled
        cropping_offset: int (optional) [default: 0]
            Offset for cropping
        default_value_resolution: float (optional) [default: 1.]
            The default value resolution
        """
        start: float = time.time()
        traces: int = 0
        # --------------------------------------------------------------------------------------------------------------
        for tr in inkml_obj.findall(f'./{namespace}trace'):
            tr_id: str = xml_id(tr)
            time_offset: int = 0
            context_id: str = context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG]
            event_type: str = PEN_DOWN
            if TYPE in tr.attrib:
                event_type = tr.attrib[TYPE]
            if TIME_OFFSET in tr.attrib:
                time_offset = int(tr.attrib[TIME_OFFSET])
            if InkMLParser.ARTIFICIAL_TS_TAG in context.decoder_map \
                    and context.decoder_map[InkMLParser.ARTIFICIAL_TS_TAG]:
                time_offset: int = int(start + traces * 2)
            if CONTEXT_REF in tr.attrib:
                context_id = tr.attrib[CONTEXT_REF]
            try:
                if event_type == PEN_DOWN:
                    # There might be annotation within the trace, then tr.text is missing content
                    text: str = tr.text
                    for t in tr:
                        text += t.tail
                    text = text.strip()
                    InkMLParser.__parse_samples__(context, tr_id, context_id, text, time_offset,
                                                  default_value_resolution)
                    traces += 1
                elif event_type == PEN_UP:
                    # There might be annotation within the trace, then tr.text is missing content
                    text: str = tr.text
                    for t in tr:
                        text += t.tail
                    text = text.strip()
                    InkMLParser.__parse_samples__(context, tr_id, context_id, text, time_offset,
                                                  default_value_resolution, hover=True)
                    traces += 1

            except InkMLParserException as e:
                logger.warning(e)
        # Collect hierarchical tree for trace groups
        for tg in inkml_obj.findall(f'./{namespace}traceGroup'):
            InkMLParser.__trace_group__(context, tg, depth=0)
        # Trace view as alternative for ground truth
        for tv in inkml_obj.findall(f'./{namespace}traceView'):
            InkMLParser.__trace_view__(context, tv, namespace=namespace)

        context.ink_model.brushes.add_vector_brush(brush)
        # --------------------------------------------------------------------------------------------------------------
        # First you need a root group to contain the strokes
        root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
        # Assign the group as the root of the main ink tree
        context.ink_model.ink_tree.root = root

        x_min: float = sys.float_info.max
        y_min: float = sys.float_info.max
        x_max: float = 0.
        y_max: float = 0.
        # Crop ink if configured
        if cropping:
            for p in context.strokes:
                p.splines_x = [s - context.decoder_map[InkMLParser.MIN_X_TAG] + cropping_offset for s in p.splines_x]
                p.splines_y = [s - context.decoder_map[InkMLParser.MIN_Y_TAG] + cropping_offset for s in p.splines_y]

        # Add the children of root node
        for stroke in context.strokes:
            x_min = min(stroke.spline_min_x, x_min)
            x_max = max(stroke.spline_max_x, x_max)
            y_min = min(stroke.spline_min_y, y_min)
            y_max = max(stroke.spline_max_y, y_max)
            root.add(StrokeNode(stroke))
        # Set the bounding box
        context.ink_model.ink_tree.root.group_bounding_box = BoundingBox(x=x_min, y=y_min, width=x_max - x_min,
                                                                         height=y_max - y_min)
        context.ink_model.knowledge_graph.add_semantic_triple(root.uri, type_def_pred, 'InkML Importer')

    @staticmethod
    def __collect_meta_data__(context: DecoderContext, inkml_obj: Element,
                              namespace: str = '{http://www.w3.org/2003/InkML}'):
        """Collecting document based annotations.

        Parameters
        ----------
        context: DecoderContext
            Decoder context containing the current parsing state.
        inkml_obj: Element
            InkML object
        namespace: str (optional) [default: '{http://www.w3.org/2003/InkML}']
            Namespace used by parser
        """
        for a in inkml_obj.findall(f'./{namespace}annotation'):
            if 'type' in a.attrib:
                context.ink_model.add_property(a.attrib['type'], a.text)
            else:
                logger.warning(a.attrib)

    def __build_object__(self, inkml_obj: Element) -> uim.InkModel:
        """Build input data document.

        Parameters
        ----------
        inkml_obj: Element
            InkML object

        Returns
        -------
        uim.InkModel
            Universal Ink Model
        """
        # Defining parser context
        context: DecoderContext = DecoderContext(version=SupportedFormats.INKML_VERSION.value,
                                                 ink_model=uim.InkModel(
                                                     version=SupportedFormats.UIM_VERSION_3_1_0.value))
        context.ink_model.ink_tree = uim.InkTree()
        context.decoder_map[InkMLParser.CONTEXT_TAG] = {}
        # Set boundary
        context.decoder_map[InkMLParser.MIN_X_TAG] = sys.maxsize
        context.decoder_map[InkMLParser.MIN_Y_TAG] = sys.maxsize
        context.decoder_map[InkMLParser.MAX_X_TAG] = 0.
        context.decoder_map[InkMLParser.MAX_Y_TAG] = 0.
        context.decoder_map[InkMLParser.ARTIFICIAL_TS_TAG] = False
        context.decoder_map[InkMLParser.DEVICE_CONFIGURATION_FOUND] = False
        context.decoder_map[SEMANTICS] = []
        # Reset channel and context
        InkMLParser.__collect_meta_data__(context, inkml_obj, namespace=self.default_namespace)
        # Collect data
        InkMLParser.__collect_channels__(context, inkml_obj, namespace=self.default_namespace,
                                         default_sample_rate=self.__default_sample_rate)
        # Build the device configuration from the collected data
        self.__build_device_configuration__(context)
        # Collect the ink strokes
        InkMLParser.__collect_ink__(context, inkml_obj, namespace=self.default_namespace,
                                    brush=self.configured_brushes[self.use_brush],
                                    cropping=self.cropping_ink, cropping_offset=self.__cropping_offset,
                                    default_value_resolution=self.default_value_resolution,
                                    type_def_pred=self.__type_def_pred)
        # Finally build views
        self.__build_views__(context, inkml_obj, namespace=self.default_namespace, view=self.content_view)
        return context.ink_model

    @staticmethod
    def __parse_empty_modifier_point__(point: str) -> list:
        """Parses empty modifier points.

        Parameters
        ----------
        point: str
            Point data

        Returns
        -------
        list
            List of values
        """
        return re.sub(' +', ' ', point.replace('\n', ' ').replace('\r', '')).split(' ')

    @staticmethod
    def __clean__(trace_data: str) -> str:
        """
        Clean the trace data.
        Parameters
        ----------
        trace_data: str
            Trace data

        Returns
        -------
        str
            Cleaned trace data
        """
        return re.sub(', ', ',', trace_data.replace('\n', ' ').replace('\r', '').strip())

    @staticmethod
    def default_brush() -> VectorBrush:
        """Default brush configuration.

        Returns
        -------
        VectorBrush
            Default brush configuration
        """

        # Add a brush specified with shape Uris
        poly_uris: list = [
            BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=0.5", 0.),
            BrushPolygonUri("will://brush/3.0/shape/Ellipse?precision=20&radiusX=0.5&radiusY=0.25", 4.0)
        ]
        return VectorBrush(
            InkMLParser.BRUSH_URI,
            poly_uris)

    @staticmethod
    def default_input_provider() -> device.InkInputProvider:
        """
        De
        Returns
        -------

        """
        return device.InkInputProvider(input_type=device.InkInputType.PEN,
                                       properties=[('input_provider_generator', 'inkml')])

    @staticmethod
    def default_environment() -> device.Environment:
        return device.Environment()

    def __build_device_configuration__(self, context: DecoderContext):
        """
        Build the device configuration from the collected data.

        Parameters
        ----------
        context: DecoderContext
            Decoder context containing the current parsing state.
        """
        input_provider: device.InkInputProvider = InkMLParser.default_input_provider()
        i_p_id: uuid.UUID = input_provider.id

        context.ink_model.input_configuration.add_environment(InkMLParser.default_environment())
        context.ink_model.input_configuration.add_input_provider(input_provider)

        # Add default context if needed
        if len(context.decoder_map[InkMLParser.CONTEXT_TAG]) == 0:
            context.decoder_map[InkMLParser.CONTEXT_TAG][InkMLParser.DEFAULT_CONTEXT_TAG] = self.default_context
            context.decoder_map[InkMLParser.CURRENT_CONTEXT_TAG] = InkMLParser.DEFAULT_CONTEXT_TAG
        # Iterate over different contexts
        for k in context.decoder_map[InkMLParser.CONTEXT_TAG].keys():
            context_map: dict = context.decoder_map[InkMLParser.CONTEXT_TAG][k]
            ink_device: device.InputDevice = device.InputDevice()
            if PROPERTIES in context_map:
                for ke, v in context_map[PROPERTIES].items():
                    ink_device.add_property(ke, v)
            channels: List[device.SensorChannel] = []
            channel_check_list: dict = dict([(c, False) for c in InkMLParser.REQUIRED_CHANNELS])
            for c in context_map[CHANNELS].values():
                ch: device.SensorChannel = device.SensorChannel(channel_type=c[CHANNEL_TYPE], metric=c[METRIC],
                                                                resolution=c[CHANNEL_RESOLUTION],
                                                                channel_min=c[CHANNEL_MIN],
                                                                channel_max=c[CHANNEL_MAX],
                                                                precision=c[PRECISION],
                                                                index=c[INDEX], name=c[NAME],
                                                                data_type=c[InkMLParser.DATA_TYPE],
                                                                ink_input_provider_id=InkMLParser.
                                                                default_input_provider().id,
                                                                input_device_id=ink_device.id)
                if c[CHANNEL_TYPE] in channel_check_list:
                    channel_check_list[c[CHANNEL_TYPE]] = True
                channels.append(ch)
                c[CHANNEL_REF] = ch
            # Check required channels
            for v, checked in channel_check_list.items():
                if not checked:
                    if v == device.InkSensorType.TIMESTAMP:
                        # Timestamp must be emulated
                        context.decoder_map[InkMLParser.ARTIFICIAL_TS_TAG] = True
                    else:
                        raise InkMLParserException(f"Required channel: {v} not found.")
            if InkMLParser.ARTIFICIAL_TS_TAG in context.decoder_map \
                    and context.decoder_map[InkMLParser.ARTIFICIAL_TS_TAG]:
                channel: device.SensorChannel = InkMLParser.__default_timestamp_channel__(i_p_id,
                                                                                          ink_device.id,
                                                                                          index=len(channels))
                context_map[CHANNELS][len(context_map[CHANNELS])] = {
                    CHANNEL_TYPE: channel.type, METRIC: channel.metric,
                    CHANNEL_RESOLUTION: channel.resolution, PRECISION: channel.precision,
                    CHANNEL_MIN: channel.min, CHANNEL_MAX: channel.max, UNIT: device.Unit.S,
                    INDEX: channel.index, NAME: channel.name, InkMLParser.DATA_TYPE: channel.data_type,
                    CHANNEL_REF: channel
                }
                channels.append(channel)
            # Sensor channel context
            sensor_channels_context = device.SensorChannelsContext(channels=channels,
                                                                   sampling_rate_hint=context_map[SAMPLE_RATE],
                                                                   ink_input_provider_id=i_p_id,
                                                                   input_device_id=ink_device.id)

            sensor_ctx = device.SensorContext(sensor_channels_contexts=[sensor_channels_context])
            input_context = device.InputContext(environment_id=InkMLParser.default_environment().id,
                                                sensor_context_id=sensor_ctx.id)
            context_map[INPUT_CONTEXT_ID] = input_context.id
            # Add ink device
            context.ink_model.input_configuration.add_ink_device(ink_device)
            # Adding the context
            context.ink_model.input_configuration.add_sensor_context(sensor_ctx)
            # Adding input context
            context.ink_model.input_configuration.add_input_context(input_context)

    @staticmethod
    def __context_get__(channels: dict, channel_type: device.InkSensorType) -> Optional[Dict[str, Any]]:
        """
        Get context for channel type.

        Parameters
        ----------
        channels: dict
            Channel dictionary if it exists, otherwise None
        """
        for c in channels.values():
            if c[CHANNEL_TYPE] == channel_type:
                return c
        return None

    def parse(self, path_or_stream: Union[str, bytes, memoryview, BytesIO, pathlib.Path], *args, **kwargs) \
            -> uim.InkModel:
        """Parsing the InkML file.

        Parameters
        ----------
        path_or_stream: Union[str, bytes, memoryview, BytesIO, pathlib.Path]
            Path to InkML file or io.BytesIO
        args: list
            Additional arguments
        kwargs: dict
            Additional keyword arguments
        """
        if isinstance(path_or_stream, (str, pathlib.Path)):
            # It's a file path
            with open(path_or_stream, 'r') as inkml_file:
                buffer = inkml_file.read()
        else:
            # It's a buffer
            if isinstance(path_or_stream, (bytes, memoryview)):
                path_or_stream = BytesIO(path_or_stream)

            buffer = path_or_stream.read()
        parser: etree.XMLParser = etree.XMLParser(recover=True)
        if isinstance(buffer, str):
            root: Element = etree.fromstring(buffer.encode(), parser)
        else:
            root: Element = etree.fromstring(buffer, parser)
        # Set correct namespace
        for s, ns in root.nsmap.items():
            if ns == 'http://www.w3.org/2003/InkML':
                self.__default_namespace = '{http://www.w3.org/2003/InkML}'
        return self.__build_object__(root)

    @staticmethod
    def guess_parameters(path_or_stream: Union[str, bytes, memoryview, BytesIO, pathlib.Path]) \
            -> Tuple[bool, float, float, float]:
        """Parsing the InkML file.

        Parameters
        ----------
        path_or_stream: Any
            Path to InkML file or io.BytesIO

        Returns
        -------
        Tuple[bool, float, float, float]
            Tuple containing the device configuration flag, resolution, min x, and max x
        """
        contains_device_configuration: bool = False
        namespace: str = ''
        if isinstance(path_or_stream, (str, pathlib.Path)):
            # It's a file path
            with open(path_or_stream, 'r') as inkml_file:
                buffer = inkml_file.read()
        else:
            # It's a buffer
            if isinstance(path_or_stream, (bytes, memoryview)):
                path_or_stream = BytesIO(path_or_stream)

            buffer = path_or_stream.read()
        parser = etree.XMLParser(recover=True)
        if isinstance(buffer, str):
            root: Element = etree.fromstring(buffer.encode(), parser)
        else:
            root: Element = (etree.fromstring(buffer, parser))
        # Set correct namespace
        for _, ns in root.nsmap.items():
            if ns == 'http://www.w3.org/2003/InkML':
                namespace = '{http://www.w3.org/2003/InkML}'
        source: list = root.findall(f'.//{namespace}inkSource')
        if len(source) > 0:
            contains_device_configuration = True
        xs: list = [float(coord[0].split(' ')[0]) for coord in
                    [InkMLParser.__clean__(trace_tag.text).split(InkMLParser.SEPARATION_CHAR)
                     for trace_tag in root.findall(f'.//{namespace}trace')]]
        max_x: float = max(xs)
        min_x: float = min(xs)
        digits: int = int(math.log10(max_x - min_x)) + 1
        resolution: float = max(1., 10. ** (digits - 3))
        return contains_device_configuration, resolution, min_x, max_x

    @classmethod
    def __trace_format__(cls, context: DecoderContext, ctx_id: str, trace_format: Element,
                         namespace: str = '{http://www.w3.org/2003/InkML}'):
        """
        Parse trace format.

        Parameters
        ----------
        context: DecoderContext
            Decoder context containing the current parsing state.
        ctx_id: str
            Context id
        trace_format: Element
            Trace format element
        namespace: str (optional) [default: '{http://www.w3.org/2003/InkML}']
            Namespace used by parser
        """
        idx: int = 0
        for ch in trace_format.findall(f'./{namespace}channel'):
            name: str = ch.attrib[NAME]
            if name.lower() in InkMLParser.MAP_CHANNEL_TYPE:
                sensor_type: device.InkSensorType = InkMLParser.MAP_CHANNEL_TYPE[name.lower()]
                unit_type: Optional[device.Unit] = None
                channel_resolution: float = 1.
                precision: int = InkMLParser.DEFAULT_PRECISION[sensor_type]
                if UNITS in ch.attrib:
                    units: str = ch.attrib[UNITS]
                    unit_type: device.Unit = InkMLParser.MAP_UNIT_TYPE[str(units).lower()]
                    channel_resolution = device.virtual_resolution_for_si_unit(unit_type)
                if unit_type in InkMLParser.MAP_UNIT_METRIC_TYPE:
                    metric = InkMLParser.MAP_UNIT_METRIC_TYPE[unit_type]
                else:
                    metric = InkMLParser.DEFAULT_METRIC_TYPE[sensor_type]
                    channel_resolution = InkMLParser.DEFAULT_RESOLUTION[sensor_type]
                    unit_type = InkMLParser.DEFAULT_UNIT[sensor_type]
                channel_min: float = float(ch.attrib['min']) if 'min' in ch.attrib else 0.
                channel_max: float = float(ch.attrib['max']) if 'max' in ch.attrib else 0.
                # Find data type
                type_str: str = str(ch.attrib['type']).lower() if 'type' in ch.attrib else 'decimal'
                data_type: device.DataType = InkMLParser.MAP_DATA_TYPE[type_str]

                context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id][CHANNELS][idx] = {
                    CHANNEL_TYPE: sensor_type, METRIC: metric, CHANNEL_RESOLUTION: channel_resolution,
                    PRECISION: precision, CHANNEL_MIN: channel_min, CHANNEL_MAX: channel_max, UNIT: unit_type,
                    INDEX: idx, NAME: name, InkMLParser.DATA_TYPE: data_type
                }
                if RESPECT_TO in ch.attrib:
                    context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id][CHANNELS][idx][RESPECT_TO] = \
                        ch.attrib[RESPECT_TO]
            else:
                logger.warning(f"Channel type:={name} not supported.")
            idx += 1

    @classmethod
    def __channel_properties__(cls, context: DecoderContext, ctx_id: str, channel_properties: Element, namespace: str):
        """
        Parse channel properties.

        Parameters
        ----------
        context: DecoderContext
            Decoder context containing the current parsing state.
        ctx_id: str
            Context id
        channel_properties: Element
            Channel properties element
        namespace: str
            Namespace used by parser
        """
        for ch in channel_properties.findall(f'./{namespace}channelProperty'):
            channel: str = ch.attrib[CHANNEL]
            if NAME in ch.attrib:
                name: str = ch.attrib[ANNOTATION_NAME]
                value: str = ch.attrib[ANNOTATION_VALUE]
                for c in context.decoder_map[InkMLParser.CONTEXT_TAG][ctx_id][CHANNELS].values():
                    if c[NAME] == channel:
                        if name == RESOLUTION:
                            resolution_value: float = float(value)
                            if resolution_value <= 0.:
                                logger.warning(f"Resolution value:={resolution_value} is invalid. Setting value to 1.")
                                resolution_value = 1.
                            c[name] = resolution_value
                        else:
                            c[name] = value

    @staticmethod
    def __default_timestamp_channel__(input_provider_id: uuid.UUID, input_device_id: uuid.UUID, index: int,
                                      time_unit: device.Unit = device.Unit.S) -> device.SensorChannel:
        """
        Create a default timestamp channel.

        Parameters
        ----------
        input_provider_id: uuid.UUID
            Input provider id
        input_device_id: uuid.UUID
            Input device id
        index: int
            Channel index
        time_unit: device.Unit (optional) [default: device.Unit.S]
            Time unit
        """
        return device.SensorChannel(channel_type=device.InkSensorType.TIMESTAMP,
                                    name=InkMLParser.TIMESTAMP_CHANNEL_NAME, index=index,
                                    metric=device.InkSensorMetricType.TIME,
                                    resolution=device.virtual_resolution_for_si_unit(time_unit),
                                    channel_min=0., channel_max=0., precision=InkMLParser.DEFAULT_PRECISION_VALUE,
                                    data_type=device.DataType.INT64,
                                    ink_input_provider_id=input_provider_id, input_device_id=input_device_id)

    @classmethod
    def style(cls) -> Style:
        """
        Default style configuration.

        Returns
        -------
        Style
            Default style configuration
        """
        prop: PathPointProperties = PathPointProperties(size=1.,
                                                        red=0.29, green=0.29, blue=0.29, alpha=1.,
                                                        rotation=0., scale_x=0., scale_y=0., scale_z=0.,
                                                        offset_x=0., offset_y=0., offset_z=0.)
        return Style(properties=prop, brush_uri=InkMLParser.BRUSH_URI, particles_random_seed=0)

    @property
    def default_channels(self) -> Dict[int, Dict[str, Any]]:
        """
        Default channel configuration.

        Returns
        -------
        Dict[int, Dict[str, Any]]
            Default channel configuration
        """
        return {
            0: {
                CHANNEL_TYPE: device.InkSensorType.X, METRIC: device.InkSensorMetricType.LENGTH,
                CHANNEL_RESOLUTION: InkMLParser.DEFAULT_RESOLUTION[device.InkSensorType.X],
                PRECISION: self.default_position_precision,
                CHANNEL_MIN: 0.0, CHANNEL_MAX: 0,
                UNIT: self.default_xy_unit, INDEX: 0, NAME: InkMLParser.X_CHANNEL_NAME,
                InkMLParser.DATA_TYPE: device.DataType.FLOAT32
            }, 1: {
                CHANNEL_TYPE: device.InkSensorType.Y, METRIC: device.InkSensorMetricType.LENGTH,
                CHANNEL_RESOLUTION: InkMLParser.DEFAULT_RESOLUTION[device.InkSensorType.X],
                PRECISION: self.default_position_precision,
                CHANNEL_MIN: 0.0, CHANNEL_MAX: 0,
                UNIT: self.default_xy_unit, INDEX: 1, NAME: InkMLParser.Y_CHANNEL_NAME,
                InkMLParser.DATA_TYPE: device.DataType.FLOAT32
            }, 2: {
                CHANNEL_TYPE: device.InkSensorType.TIMESTAMP, METRIC: device.InkSensorMetricType.TIME,
                CHANNEL_RESOLUTION: InkMLParser.DEFAULT_RESOLUTION[device.InkSensorType.TIMESTAMP], PRECISION: 0,
                CHANNEL_MIN: 0.0, CHANNEL_MAX: 0.0,
                UNIT: device.Unit.MS, INDEX: 2, NAME: 'T', InkMLParser.DATA_TYPE: device.DataType.INT64
            }
        }

    def __build_views__(self, context: DecoderContext, inkml_obj: Element, namespace: str, view: str):
        """
        Build views for Universal Ink Model with Wacom Ontology Definition Language (WODL) semantics,
        that are configured with register_types and register_values.

        Parameters
        ----------
        context: DecoderContext
            Decoder context containing the current parsing state.
        inkml_obj: Element
            InkML object
        namespace: str
            Namespace used by parser
        view: str
            View name for Universal Ink Model.
        """
        semantic_entities: Dict[dict] = context.decoder_map[SEMANTICS]
        if len(semantic_entities) > 0:
            # Create a view on data
            content_view: uim.ViewTree = uim.ViewTree(view)
            content_view.root = StrokeGroupNode(UUIDIdentifier.id_generator())
            # Adding root node
            context.ink_model.knowledge_graph.add_semantic_triple(content_view.root.uri, self.__type_def_pred,
                                                                  'Semantics')
            context.ink_model.add_view(content_view)
            xml_annotation: Element = inkml_obj.find(f'./{namespace}annotationXML')
            if xml_annotation is not None:
                predicate: str = semantics.IS
                if 'encoding' in xml_annotation.attrib:
                    if xml_annotation.attrib['encoding'] == 'Content-MathML':
                        predicate = semantics.MathStructureSchema.HAS_MATHML
                context.ink_model.knowledge_graph.add_semantic_triple(content_view.root.uri, predicate,
                                                                      stringify_children(xml_annotation))
            # Remember stroke group nodes
            map_groups: Dict[str, StrokeGroupNode] = {}
            for element in sorted(context.decoder_map[SEMANTICS],
                                  key=lambda x: (x[DEPTH], x[INDEX])):
                # Id handling
                stroke_group: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
                map_groups[element[IDENTIFIER]] = stroke_group

                for s in element[STROKE_IDS]:
                    stroke: Stroke = context.stroke_by_identifier(s)
                    stroke_node: StrokeNode = StrokeNode(stroke=stroke)
                    stroke_group.add(stroke_node)

                if element[PARENT] in map_groups:
                    map_groups[element[PARENT]].add(stroke_group)
                else:
                    content_view.root.add(stroke_group)
                type_classes: Optional[str] = None
                for a in element[SEMANTICS]:
                    obj: Optional[str] = None
                    predicate: Optional[str] = None
                    # First check for value
                    if a[ANNOTATION_TYPE] in self.__value_map:
                        predicate = self.__value_map.get(a[ANNOTATION_TYPE])
                        obj = a[ANNOTATION_VALUE]
                    # Check if annotation is a type mapping
                    elif a[ANNOTATION_TYPE] in self.__type_map:
                        type_dict: Dict[str, Any] = self.__type_map.get(a[ANNOTATION_TYPE])
                        if a[ANNOTATION_VALUE] in type_dict:
                            obj_dict: Dict[str, Any] = type_dict[a[ANNOTATION_VALUE]]
                            obj = obj_dict[MAPPING]
                            if SUBTYPES in obj_dict and obj_dict[SUBTYPES]:
                                for sub_predicate, sub_value in obj_dict[SUBTYPES]:
                                    context.ink_model.add_semantic_triple(subject=stroke_group.uri,
                                                                          predicate=sub_predicate,
                                                                          obj=sub_value)
                            else:
                                type_classes = obj
                        else:
                            logger.warning(f"Type mapping for:={a[ANNOTATION_VALUE]} not found.")
                    else:
                        logger.warning(f"Annotation type:={a[ANNOTATION_TYPE]} not supported. "
                                       f"Value:={a[ANNOTATION_VALUE]}")

                    if predicate and obj:
                        context.ink_model.add_semantic_triple(subject=stroke_group.uri,
                                                              predicate=predicate,
                                                              obj=obj)
                # Add type definition if available, otherwise use default annotation type (if available)
                if type_classes:
                    context.ink_model.add_semantic_triple(subject=stroke_group.uri,
                                                          predicate=self.__type_def_pred,
                                                          obj=type_classes)
                elif self.default_annotation_type:
                    context.ink_model.add_semantic_triple(subject=stroke_group.uri,
                                                          predicate=self.__type_def_pred,
                                                          obj=self.default_annotation_type)

    @classmethod
    def __remove_modifier__(cls, channel_value_str):
        """
        Remove modifier from channel value.

        Parameters
        ----------
        channel_value_str: str
            Channel value string
        """
        return (channel_value_str.replace(InkMLParser.SINGLE_DIFFERENCE_MODIFIER, '')
                .replace(InkMLParser.SECOND_DIFFERENCE_MODIFIER, ''))

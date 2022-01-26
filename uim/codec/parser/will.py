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
import os
import pathlib
import struct
import time
import uuid
import zipfile
from chunk import Chunk
from io import BytesIO
from typing import Any, Tuple, Dict, List, Optional

import numpy as np
import varint
from bitstring import BitArray, Bits
from lxml import etree

import uim.model.ink as uim
from uim.codec.base import WILL_PROTOBUF_ENCODING, RIFF_HEADER
from uim.codec.format.WILL_2_0_0_pb2 import Path
from uim.codec.context.version import Version
from uim.codec.parser.base import Parser, FormatException, SupportedFormats
from uim.codec.parser.base import Stream, EndOfStream
from uim.model.base import UUIDIdentifier
from uim.model.ink import InkModel
from uim.model.inkdata import brush
from uim.model.inkdata.strokes import Stroke, PathPointProperties
from uim.model.inkdata.strokes import Style
from uim.model.inkinput import inputdata as device
from uim.model.inkinput import sensordata as sensor
from uim.model.semantics import syntax
from uim.model.semantics.node import StrokeGroupNode, StrokeNode
from uim.model.semantics.syntax import CommonViews


class WILL2Parser(Parser):
    """
    Parser for Wacom Ink Layer Language - Data and File format.

    Examples
    --------
    >>> from uim.codec.parser.will import WILL2Parser
    >>> from uim.model.ink import InkModel
    >>> parser: WILL2Parser = WILL2Parser()
    >>> ink_model: InkModel = parser.parse('../ink/will/apple.will')

    See also
    --------
    ´UIMParser´ - Parser for UIM files
    """
    # Constants for meta data WILL File format
    APP_VERSION: str = '{http://schemas.willfileformat.org/2015/relationships/extended-properties}AppVersion'
    """App version property tag."""
    APPLICATION: str = '{http://schemas.willfileformat.org/2015/relationships/extended-properties}Application'
    """Application property tag."""

    # Prefix for the node uri.
    NODE_URI_PREFIX: str = 'uim:node/{}'

    DEFAULT_WRITE_FORMAT: str = 'will'

    DEFAULT_APPLICATION_NAME: str = 'Universal Ink Model - Converter'
    DEFAULT_APPLICATION_VERSION: float = 0.1

    DEFAULT_PATH_WIDTH: int = 100
    DEFAULT_DECIMAL_PRECISION: int = 2
    SOURCE_OVER: int = 2
    DEFAULT_DATETIME_FORMAT: str = '%Y-%m-%dT%H:%M:%SZ'

    INK_DEVICE_BAMBOO_SLATE: str = 'Bamboo Slate/Folio'
    INK_DEVICE_BAMBOO_SPARK: str = 'Bamboo Spark'

    BRUSH: Dict[str, Any] = {
        "name": "app://will/vector-brush/Circle",
        "prototype": [
            {
                "shapeURI": "will://brush/3.0/shape/Circle?precision=4&radius="
            }, {
                "shapeURI": "will://brush/3.0/shape/Circle?precision=8&radius=", "size": 2.0
            }, {
                "shapeURI": "will://brush/3.0/shape/Circle?precision=16&radius=", "size": 6.0
            }, {
                "shapeURI": "will://brush/3.0/shape/Circle?precision=32&radius=", "size": 18.0
            }
        ], "spacing": 1.0
    }
    """Default brush configuration."""

    DEFAULT_TIME_STEP: float = 8
    """ Sampling rate of 120 Hz roughly 8 ms."""

    def __init__(self):
        self.__version: Optional[str] = None
        self.__paths: list = []
        self.__protobuf = None
        self.__source: str = ''

        self.__document_application: str = WILL2Parser.DEFAULT_APPLICATION_NAME
        self.__document_application_version: str = str(WILL2Parser.DEFAULT_APPLICATION_VERSION)
        self.__viewport_x: float = 0.0
        self.__viewport_y: float = 0.0
        self.__viewport_width: float = 640.0
        self.__viewport_height: float = 480.0
        self.__document_title: str = ''
        self.__document_creation_datetime: str = ''
        self.__ink_device_model_guess: str = WILL2Parser.INK_DEVICE_BAMBOO_SLATE
        self.__matrix = np.identity(3)
        self.__default_input_provider: device.InkInputProvider = WILL2Parser.__default_input_provider__()
        self.__default_environment: device.Environment = WILL2Parser.__default_environment__()
        self.__default_input_device: device.InputDevice = WILL2Parser.__default_input_device__()
        self.__default_input_context: Optional[device.InputContext] = None
        self.__default_sensors_context: Optional[device.SensorContext] = None
        self.__x_channel: Optional[device.SensorChannel] = None
        self.__y_channel: Optional[device.SensorChannel] = None
        self.__t_channel: Optional[device.SensorChannel] = None

    def parse(self, path_or_stream: Any) -> InkModel:
        """
        Parse the content of a WILL data or file format encoded ink file to the Universal Ink memory model.

        Parameters
        ----------
        path_or_stream: Any
            `Path` of file, path as str, stream, or byte array.

        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream
        """
        # Read the file if path_or_stream is a file path
        if isinstance(path_or_stream, (str, pathlib.Path)):
            with open(path_or_stream, mode='rb') as fp:
                stream: BytesIO = BytesIO(fp.read())
        elif isinstance(path_or_stream, (bytes, memoryview)):
            stream: BytesIO = BytesIO(path_or_stream)
        elif isinstance(path_or_stream, BytesIO):
            stream: BytesIO = path_or_stream
        else:
            raise TypeError(
                'parse() accepts Path, path (str) or stream (bytes, BytesIO), got {}'.format(type(path_or_stream)))

        version: Version = WILL2Parser.__get_version_from_stream__(stream)
        if version == SupportedFormats.WILL_DATA_VERSION_2_0_0:  # Data format
            paths: List = self.__parse_will_data__(stream)
        else:  # File codec (OPC)
            paths = self.__parse_will_file__(stream)

        self.__paths = self.__ensure_unique_path_ids__(paths)
        return self.__build_object__()

    def __parse_will_data__(self, stream: BytesIO) -> List[Path]:
        paths: list = []
        riff_chunk: Chunk = Chunk(stream, bigendian=False)
        riff_chunk.read(4)  # skip the WILL chunk name
        head_chunk: Chunk = Chunk(riff_chunk, bigendian=False)
        _ = head_chunk.read()
        ink_chunk: Chunk = Chunk(riff_chunk, bigendian=False)
        ink_data: bytes = ink_chunk.read()
        self.__protobuf = ink_data
        try:
            for path in self.__parse_protobuf__(Stream(ink_data)):
                paths.append(path)
        except EndOfStream:
            pass
        return paths

    def __parse_will_file__(self, stream: BytesIO) -> List[Path]:
        paths: list = []
        try:
            with zipfile.ZipFile(stream) as f:
                for fname in f.namelist():
                    if fname.endswith('.protobuf') and not fname.startswith("style"):
                        with f.open(fname) as fp:
                            self.__protobuf = fp.read()

                    if fname == 'props/app.xml':
                        with f.open(fname) as fp:
                            root = etree.fromstring(fp.read())
                            self.__document_application = root.find(WILL2Parser.APPLICATION).text
                            # WILL files created with Bamboo Spark generation sometimes have Bamboo Spark added as
                            # document application
                            if self.__document_application == WILL2Parser.INK_DEVICE_BAMBOO_SPARK:
                                self.__ink_device_model_guess = WILL2Parser.INK_DEVICE_BAMBOO_SPARK
                            self.__document_application_version = root.find(WILL2Parser.APP_VERSION).text

                    if fname == 'props/core.xml':
                        with f.open(fname) as fp:
                            root = etree.fromstring(fp.read())

                            title = root.find('{http://purl.org/dc/elements/1.1/}title')
                            if title is not None:
                                self.__document_title = title.text

                            created = root.find('{http://purl.org/dc/terms/}created')
                            if created is not None:
                                self.__document_creation_datetime = created.text

                    if fname == 'sections/section0.svg' or fname == 'sections/section.svg':
                        with f.open(fname) as fp:
                            root = etree.fromstring(fp.read())
                            view = root.find('{http://www.w3.org/2000/svg}view')
                            if view is not None:
                                view_box = view.attrib['viewBox']
                                x, y, width, height = view_box.split(' ')
                                self.__viewport_x = float(x)
                                self.__viewport_y = float(y)
                                self.__viewport_width = float(width)
                                self.__viewport_height = float(height)
                            else:
                                self.__viewport_x = 0
                                self.__viewport_y = 0
                                self.__viewport_width = float(root.attrib['width'])
                                self.__viewport_height = float(root.attrib['height'])

                            matrix = root.find('{http://www.w3.org/2000/svg}g')
                            if matrix is not None and 'transform' in matrix.attrib:
                                matrix_array = matrix.attrib['transform'][7:-1].split(' ')
                                '''
                                The matrix(<a> <b> <c> <d> <e> <f>) transform function specifies a transformation
                                in the form of a  transformation matrix of six values. matrix(a,b,c,d,e,f) is
                                equivalent to applying the transformation matrix:
                                ( a	 c	e
                                  b	 d	f
                                  0	 0	1 )'''
                                rotmatrix: np.array = np.array(
                                    ((float(matrix_array[0]), float(matrix_array[2]), float(matrix_array[4])),
                                     (float(matrix_array[1]), float(matrix_array[3]), float(matrix_array[5])),
                                     (0., 0., 1.)))

                                sub = matrix.find('{http://www.w3.org/2000/svg}g')
                                if sub is not None and 'transform' in sub.attrib:
                                    matrix_array = sub.attrib['transform'][7:-1].split(' ')
                                    rotmatrix2: np.array = np.array(
                                        ((float(matrix_array[0]), float(matrix_array[2]), float(matrix_array[4])),
                                         (float(matrix_array[1]), float(matrix_array[3]), float(matrix_array[5])),
                                         (0., 0., 1.)))
                                else:
                                    rotmatrix2: np.array = np.identity(3)
                            scale: np.array = device.unit2unit_matrix(device.Unit.DIP, device.Unit.M)
                            self.__matrix = scale.dot(rotmatrix.dot(rotmatrix2))

        except zipfile.BadZipFile as e:
            raise FormatException(e)
        try:
            for path in self.__parse_protobuf__(Stream(self.__protobuf)):
                paths.append(path)
        except EndOfStream:
            pass
        if len(paths) == 0:
            raise FormatException('No path data found in the WILL file.')
        return paths

    @staticmethod
    def __default_style__(red: float, green: float, blue: float, alpha: float) -> Style:
        prop: PathPointProperties = PathPointProperties(size=0.3,
                                                        red=red, green=green, blue=blue,
                                                        alpha=alpha, rotation=0.,
                                                        scale_x=0., scale_y=0., scale_z=0.,
                                                        offset_x=0., offset_y=0., offset_z=0.)
        style: Style = Style(properties=prop, brush_uri=WILL2Parser.BRUSH['name'], particles_random_seed=234,
                             render_mode_uri='')
        return style

    def __collect_ink__(self, ink_model: InkModel):
        sensor_ctx = self.__default_sensors_context
        # Build generic ink tree
        # Build generic ink tree
        root_node_id: uuid.UUID = UUIDIdentifier.id_generator()
        ink_model.ink_tree = uim.InkTree(CommonViews.MAIN_INK_TREE.value)
        # Root tree element
        ink_model.ink_tree.root = StrokeGroupNode(uim_id=root_node_id)
        start_time: int = round(time.time() * 1000)
        last_time: int = start_time
        for path in self.__paths:
            stroke_time: int = last_time + 100
            xs: list = []
            ys: list = []
            spline_x: list = []
            spline_y: list = []
            ts: list = []
            points, point_widths, points_color = self.__decode_path_to_stroke__(path)
            points: list = list(points)
            point_widths: list = list(point_widths)

            # create an array of len(points) with the same value repeated
            if len(point_widths) == 1:
                point_widths = (len(points) // 2) * point_widths

            samples: sensor.SensorData = sensor.SensorData(sid=UUIDIdentifier.id_generator(),
                                                           input_context_id=self.__default_input_context.id,
                                                           state=sensor.InkState.PLANE, timestamp=0)
            path_obj: Stroke = Stroke(sensor_data_offset=0, sensor_data_id=samples.id,
                                      style=WILL2Parser.__default_style__(points_color['r'][0],
                                                                          points_color['g'][0],
                                                                          points_color['b'][0],
                                                                          points_color['a'][0]))
            path_obj.start_parameter = path.startParameter
            path_obj.end_parameter = path.endParameter
            for i in range(0, len(points) - 1, 2):
                spline_x.append(points[i])
                spline_y.append(points[i + 1])
                trans: np.ndarray = self.__matrix.dot((points[i], points[i + 1], 1.))
                xs.append(trans[0])
                ys.append(trans[1])
                ts.append(stroke_time + WILL2Parser.DEFAULT_TIME_STEP)

            path_obj.splines_x = spline_x
            path_obj.splines_y = spline_y
            path_obj.sizes = point_widths

            samples.add_data(sensor_ctx.get_channel_by_type(device.InkSensorType.X), xs)
            samples.add_data(sensor_ctx.get_channel_by_type(device.InkSensorType.Y), ys)
            samples.add_timestamp_data(sensor_ctx.get_channel_by_type(device.InkSensorType.TIMESTAMP), ts)
            # Adding the sensor sequence
            ink_model.sensor_data.add(samples)
            ink_model.ink_tree.root.add(StrokeNode(path_obj))

        ink_model.knowledge_graph.add_semantic_triple(WILL2Parser.NODE_URI_PREFIX.format(root_node_id),
                                                      syntax.CommonRDF.PRED_RDF_HAS_TYPE, 'WILL 2.0 - File')
        ink_model.brushes.add_vector_brush(self.__default_brush__())

    def __setup_document_properties__(self, ink_model: InkModel):
        statements: list = [
            (syntax.DOCUMENT_TITLE_OBJECT, self.__document_title),
            (syntax.DOCUMENT_CREATION_DATE_OBJECT, self.__document_creation_datetime),
            (syntax.DOCUMENT_X_MIN_PROPERTY, str(self.__viewport_x)),
            (syntax.DOCUMENT_Y_MIN_PROPERTY, str(self.__viewport_y)),
            (syntax.DOCUMENT_WIDTH_PROPERTY, str(self.__viewport_width)),
            (syntax.DOCUMENT_HEIGHT_PROPERTY, str(self.__viewport_height))
        ]
        ink_model.properties = statements

    @staticmethod
    def __default_brush__() -> brush.VectorBrush:
        prototypes = []
        for p in WILL2Parser.BRUSH['prototype']:
            brush_prototype: brush.BrushPolygonUri = brush.BrushPolygonUri(
                uri=p['shapeURI'], min_scale=p.get('size', 1)
            )
            prototypes.append(brush_prototype)
        return brush.VectorBrush(name=WILL2Parser.BRUSH['name'], prototypes=prototypes, spacing=0.5)

    def __build_object__(self):
        ink_model: InkModel = InkModel(Version(2, 0, 0, "WILL"))
        self.__build_device_configuration__(ink_model)
        self.__collect_ink__(ink_model)
        self.__setup_document_properties__(ink_model)
        return ink_model

    def __paths_to_protobuf__(self):
        string_messages: List[str] = []
        for path in self.__paths:
            message = path.SerializeToString()
            message_length = varint.encode(len(message))
            string_messages.append(
                ''.join([message_length.decode(WILL_PROTOBUF_ENCODING), message.decode(WILL_PROTOBUF_ENCODING)]))
        protobuf_stream = ''.join(string_messages)
        return protobuf_stream

    @staticmethod
    def __get_version_from_stream__(stream: BytesIO) -> Version:
        header: bytes = stream.read(4)
        stream.seek(0)
        if header == RIFF_HEADER:
            return SupportedFormats.WILL_DATA_VERSION_2_0_0
        return SupportedFormats.WILL_FILE_VERSION_2_0_0

    @staticmethod
    def __get_format_from_filename__(filename: str):
        filename: str = filename.lower()
        return os.path.splitext(filename)[-1].replace('.', '')

    @staticmethod
    def unpack_will(filename_or_stream: Any, target_dir_name=None):
        """
        Unpack the WILL file codec (OPC).

        Parameters
        ----------
        filename_or_stream: Any
            File or stream
        target_dir_name: str
            Target directory for unpacking
        """
        stream = filename_or_stream
        if isinstance(filename_or_stream, str):
            target_dir_name = target_dir_name or filename_or_stream
            target_dir_name = target_dir_name.replace('.will', '_will')
            stream = open(filename_or_stream, 'rb')

        with zipfile.ZipFile(stream, 'r') as zf:
            zf.extractall(path=target_dir_name)

    @staticmethod
    def __ensure_unique_path_ids__(paths):
        """
        Make sure every path has unique id.

        The function tries to preserve the existing IDs of the paths.
        It checks for duplicating IDs and assigns new IDs which start at
        the `max_id + 1` of the existing IDs.
        """
        unique_ids = set()
        to_be_fixed = []

        for idx, path in enumerate(paths):
            if path.id not in unique_ids:
                unique_ids.add(path.id)
            else:
                # Add the index of the path to the list of to-be-fixed ids
                to_be_fixed.append(idx)

        # Assign new id to the paths that didn't have one before
        if unique_ids:
            max_unique_id = max(unique_ids) + 1
            for idx in to_be_fixed:
                paths[idx].id = max_unique_id
                max_unique_id += 1
        return paths

    @staticmethod
    def __parse_protobuf__(stream: Stream):
        # Read message length (128 bit varint)
        while True:
            message_length: int = WILL2Parser.__decode_varint__(stream).uint
            message = stream.read(message_length)
            path: Path = Path()
            path.ParseFromString(message)
            yield path

    @staticmethod
    def __decode_path_to_stroke__(path) -> Tuple[List[float], List[float], dict]:
        points: list = WILL2Parser.__decode_delta_encoded_points__(path.data, path.decimalPrecision)
        point_widths: list = WILL2Parser.__decode_delta_encoded_widths__(path.strokeWidth, path.decimalPrecision)
        points_color: dict = WILL2Parser.__decode_delta_encoded_colors__(path.strokeColor)
        return points, point_widths, points_color

    @staticmethod
    def __decode_delta_encoded_points__(arr: List[int], decimal_precision: float) -> List[float]:
        integers: List[int] = []
        last_x: int = arr[0]
        last_y: int = arr[1]
        integers.append(last_x)
        integers.append(last_y)
        for i in range(2, len(arr) - 1, 2):
            last_x = arr[i] + last_x
            last_y = arr[i + 1] + last_y
            integers.append(last_x)
            integers.append(last_y)
        floats: List[float] = list(map(lambda x: float(x) / (10 ** decimal_precision), integers))
        return floats

    @staticmethod
    def __decode_delta_encoded_widths__(arr: list, decimal_precision: float) -> List[float]:
        if len(arr) == 1:
            floats: List[float] = [float(arr[0]) / (10 ** decimal_precision)]
        else:
            integers: List[int] = []
            last_width: int = arr[0]
            integers.append(last_width)
            for i in range(1, len(arr)):
                last_width += arr[i]
                integers.append(last_width)
            floats: List[float] = list(map(lambda x: float(x) / (10 ** decimal_precision), integers))
        return floats

    @staticmethod
    def __decode_delta_encoded_colors__(arr: list) -> Dict[str, list]:
        colors: dict = {'r': [], 'g': [], 'b': [], 'a': []}
        if len(arr) == 1:
            integers: list = [arr[0]]
        else:
            integers: list = []
            last_color = arr[0]
            integers.append(last_color)
            for i in range(1, len(arr)):
                last_color += arr[i]
                integers.append(last_color)
        for rgba in integers:
            colors['r'].append(((rgba >> 24) & 0xFF) / 255.0)
            colors['g'].append(((rgba >> 16) & 0xFF) / 255.0)
            colors['b'].append(((rgba >> 8) & 0xFF) / 255.0)
            colors['a'].append((rgba & 0xFF) / 255.0)
        return colors

    @staticmethod
    def __decode_varint__(stream) -> BitArray:
        bit_array: BitArray = BitArray()
        while True:
            byte = stream.read(1)
            if not byte:
                raise EndOfStream()
            byte: byte = struct.unpack('B', byte)[0]
            has_more: bool = byte & 0x80  # test most-significant-bit
            bit_array.prepend(BitArray(uint=byte & 0x7F, length=7))
            if not has_more:
                break
        return bit_array

    @staticmethod
    def __decode_tag_wire_type__(bit_array: BitArray) -> Tuple[Bits, Bits]:
        wire_type: Bits = bit_array[-3:bit_array.length]
        tag: Bits = bit_array[0:-3]
        return tag, wire_type

    @staticmethod
    def __read_value__(stream, wire_type: Bits) -> BitArray:
        if wire_type.uint == 0:
            return WILL2Parser.__decode_varint__(stream)

        elif wire_type.uint == 1:
            return

        elif wire_type.uint == 2:
            length = WILL2Parser.__decode_varint__(stream).uint
            return stream.read(length)

        elif wire_type.uint == 3:
            return

        elif wire_type.uint == 4:
            return

        elif wire_type.uint == 5:
            return stream.read(4)

    @staticmethod
    def __proto_reader__(stream):
        idx: int = 0
        while idx < len(stream):
            bit_array: BitArray = WILL2Parser.__decode_varint__(stream)
            tag, wire_type = WILL2Parser.__decode_tag_wire_type__(bit_array)
            value = WILL2Parser.__read_value__(stream, wire_type)
            yield tag.uint, wire_type.uint, value

    @staticmethod
    def __default_ink_device__() -> device.InputDevice:
        return device.InputDevice()

    @staticmethod
    def __default_input_provider__() -> device.InkInputProvider:
        return device.InkInputProvider(input_type=device.InkInputType.PEN,
                                       properties=[('input_provider_generator', 'will')])

    @staticmethod
    def __default_environment__() -> device.Environment:
        return device.Environment()

    @staticmethod
    def __default_input_device__() -> device.InputDevice:
        return device.InputDevice()

    def __build_device_configuration__(self, ink_obj: uim.InkModel):
        ink_obj.input_configuration.add_environment(self.__default_environment)
        ink_obj.input_configuration.add_input_provider(self.__default_input_provider)

        self.__x_channel = device.SensorChannel(channel_type=device.InkSensorType.X,
                                                metric=device.InkSensorMetricType.LENGTH,
                                                resolution=device.virtual_resolution_for_si_unit(device.Unit.DIP),
                                                channel_min=0., channel_max=0., precision=2,
                                                ink_input_provider_id=self.__default_input_provider.id,
                                                input_device_id=self.__default_input_device.id)
        self.__y_channel = device.SensorChannel(channel_type=device.InkSensorType.Y,
                                                metric=device.InkSensorMetricType.LENGTH,
                                                resolution=device.virtual_resolution_for_si_unit(device.Unit.DIP),
                                                channel_min=0., channel_max=0., precision=2,
                                                ink_input_provider_id=self.__default_input_provider.id,
                                                input_device_id=self.__default_input_device.id)
        self.__t_channel = device.SensorChannel(channel_type=device.InkSensorType.TIMESTAMP,
                                                metric=device.InkSensorMetricType.TIME,
                                                resolution=device.virtual_resolution_for_si_unit(device.Unit.MS),
                                                channel_min=0., channel_max=0., precision=2,
                                                ink_input_provider_id=self.__default_input_provider.id,
                                                input_device_id=self.__default_input_device.id)
        ctx = device.SensorChannelsContext(channels=[self.__x_channel, self.__y_channel, self.__t_channel],
                                           ink_input_provider_id=self.__default_input_provider.id,
                                           input_device_id=self.__default_input_device.id)
        # Iterate over different contexts
        self.__default_sensors_context = device.SensorContext(sensor_channels_contexts=[ctx])
        self.__default_input_context = device.InputContext(environment_id=self.__default_environment.id,
                                                           sensor_context_id=self.__default_sensors_context.id)
        # Add ink device
        ink_obj.input_configuration.add_ink_device(self.__default_input_device)
        # Adding the context
        ink_obj.input_configuration.add_sensor_context(self.__default_sensors_context)
        # Adding input context
        ink_obj.input_configuration.add_input_context(self.__default_input_context)

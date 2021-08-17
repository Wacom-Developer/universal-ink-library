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
import ctypes
import uuid
from io import BytesIO
from typing import Any, List, Tuple, Optional, Dict

import uim.codec.format.UIM_3_1_0_pb2 as uim_3_1_0
from uim.codec.base import ContentType, PROPERTIES_HEADER, INPUT_DATA_HEADER, BRUSHES_HEADER, INK_DATA_HEADER, \
    KNOWLEDGE_HEADER, INK_STRUCTURE_HEADER, CompressionType, CHUNK_DESCRIPTION, CHUNK_ID_BYTES_SIZE
from uim.codec.context.decoder import DecoderContext
from uim.codec.context.scheme import PrecisionScheme
from uim.codec.parser.base import FormatException, SupportedFormats
from uim.codec.parser.decoder.base import CodecDecoder
from uim.model.base import Identifier
from uim.model.ink import InkModel, InkTree
from uim.model.inkdata.brush import RasterBrush, VectorBrush, BrushPolygon, BlendMode, BrushPolygonUri, RotationMode
from uim.model.inkdata.strokes import Stroke, PathPointProperties, Style
from uim.model.inkinput.inputdata import InkSensorType, InputContext, SensorContext, SensorChannel, \
    InkSensorMetricType, InkInputType, InputDevice, InkInputProvider, Environment, SensorChannelsContext, DataType
from uim.model.inkinput.sensordata import SensorData, ChannelData, InkState
from uim.model.semantics.node import BoundingBox, StrokeGroupNode, StrokeNode, StrokeFragment
from uim.model.semantics.syntax import CommonViews


class UIMDecoder310(CodecDecoder):
    """
    The UIMDecoder310 decodes the Universal Ink Model v3.1.0.

    References
    ----------
    [1]  Universal Ink Model documentation - URL https://developer-docs.wacom.com/sdk-for-ink/docs/model
    """

    MAP_CONTENT_TYPE: Dict[bytes, ContentType] = dict([(c.value, c) for c in ContentType])
    """Mapping of the `ContentType`."""

    MAP_COMPRESSION_TYPE: Dict[bytes, CompressionType] = dict([(c.value, c) for c in CompressionType])
    """Mapping of the `CompressionType`."""

    MAP_CHUNK_TYPE: Dict[bytes, Any] = {
        PROPERTIES_HEADER: uim_3_1_0.Properties(),
        INPUT_DATA_HEADER: uim_3_1_0.InputData(),
        BRUSHES_HEADER: uim_3_1_0.Brushes(),
        INK_DATA_HEADER: uim_3_1_0.InkData(),
        KNOWLEDGE_HEADER: uim_3_1_0.TripleStore(),
        INK_STRUCTURE_HEADER: uim_3_1_0.InkStructure()
    }
    """Mapping of the different chunk types."""

    MAP_INK_METRICS_TYPE: Dict[int, InkSensorMetricType] = {
        uim_3_1_0.LENGTH: InkSensorMetricType.LENGTH,
        uim_3_1_0.TIME: InkSensorMetricType.TIME,
        uim_3_1_0.FORCE: InkSensorMetricType.FORCE,
        uim_3_1_0.ANGLE: InkSensorMetricType.ANGLE,
        uim_3_1_0.NORMALIZED: InkSensorMetricType.NORMALIZED
    }
    """Mapping unit types."""

    MAP_STATE_TYPE: Dict[int, InkState] = {
        uim_3_1_0.PLANE: InkState.PLANE,
        uim_3_1_0.HOVERING: InkState.HOVERING,
        uim_3_1_0.IN_VOLUME: InkState.IN_VOLUME,
        uim_3_1_0.VOLUME_HOVERING: InkState.VOLUME_HOVERING
    }
    """Mapping of the uim input data states."""

    MAP_CHANNEL_TYPE: Dict[str, InkSensorType] = {
        InkSensorType.X.value: InkSensorType.X,
        InkSensorType.Y.value: InkSensorType.Y,
        InkSensorType.Z.value: InkSensorType.Z,
        InkSensorType.TIMESTAMP.value: InkSensorType.TIMESTAMP,
        InkSensorType.PRESSURE.value: InkSensorType.PRESSURE,
        InkSensorType.AZIMUTH.value: InkSensorType.AZIMUTH,
        InkSensorType.ALTITUDE.value: InkSensorType.ALTITUDE,
        InkSensorType.ROTATION.value: InkSensorType.ROTATION,
        InkSensorType.RADIUS_X.value: InkSensorType.RADIUS_X,
        InkSensorType.RADIUS_Y.value: InkSensorType.RADIUS_Y
    }
    """Mapping of channel types."""

    MAP_INPUT_PROVIDER_TYPE: Dict[int, InkInputType] = {
        uim_3_1_0.PEN: InkInputType.PEN,
        uim_3_1_0.TOUCH: InkInputType.TOUCH,
        uim_3_1_0.CONTROLLER: InkInputType.CONTROLLER,
        uim_3_1_0.MOUSE: InkInputType.MOUSE
    }
    """Mapping of input providers."""

    MAP_BLEND_MODE: Dict[int, BlendMode] = {
        uim_3_1_0.SOURCE_OVER: BlendMode.SOURCE_OVER,
        uim_3_1_0.DESTINATION_OVER: BlendMode.DESTINATION_OVER,
        uim_3_1_0.DESTINATION_OUT: BlendMode.DESTINATION_OUT,
        uim_3_1_0.LIGHTER: BlendMode.LIGHTER,
        uim_3_1_0.COPY: BlendMode.COPY,
        uim_3_1_0.MIN: BlendMode.MIN,
        uim_3_1_0.MAX: BlendMode.MAX
    }
    """Mapping of blend modes."""

    MAP_ROTATION_MODE: Dict[int, RotationMode] = {
        uim_3_1_0.NONE: RotationMode.NONE,
        uim_3_1_0.RANDOM: RotationMode.RANDOM,
        uim_3_1_0.TRAJECTORY: RotationMode.TRAJECTORY
    }
    """Map for rotation mode"""

    def __init__(self):
        pass

    @classmethod
    def parse_brushes(cls, context: DecoderContext, brushes: uim_3_1_0.Brushes):
        """
        Parse brush definitions.

        Parameters
        ----------
        context: `DecoderContext`
            Decoder context
        brushes: `uim_3_1_0.Brushes`
            Protobuf structure for brushes
        """
        # Decode vector brushes
        for vectorBrush in brushes.vectorBrushes:
            prototypes: list = []
            for p in vectorBrush.prototype:
                if p.shapeURI:
                    brush_prototype: BrushPolygonUri = BrushPolygonUri(p.shapeURI, p.size)
                else:
                    points: list = []
                    for idx in range(len(p.coordX)):
                        points.append((p.coordX[idx], p.coordY[idx]))
                    brush_prototype: BrushPolygon = BrushPolygon(p.size, points, p.indices)
                prototypes.append(brush_prototype)
            brush: VectorBrush = VectorBrush(
                vectorBrush.name,
                prototypes,
                vectorBrush.spacing,
            )
            context.ink_model.brushes.add_vector_brush(brush)

        # Decode raster brushes
        for rasterBrush in brushes.rasterBrushes:
            brush: RasterBrush = RasterBrush(
                rasterBrush.name,
                rasterBrush.spacing,
                rasterBrush.scattering,
                UIMDecoder310.MAP_ROTATION_MODE[rasterBrush.rotationMode],
                rasterBrush.shapeTexture,
                rasterBrush.shapeTextureURI,
                rasterBrush.fillTexture,
                rasterBrush.fillTextureURI,
                rasterBrush.fillWidth,
                rasterBrush.fillHeight,
                rasterBrush.randomizeFill,
                UIMDecoder310.MAP_BLEND_MODE[rasterBrush.blendMode]
            )
            context.ink_model.brushes.add_raster_brush(brush)

    @classmethod
    def parse_properties(cls, context: DecoderContext, properties: uim_3_1_0.Properties):
        """
        Parse properties Protobuf structure and assign it to internal structure.

        Parameters
        ----------
        context: `DecoderContext`
            Decoder context
        properties: `uim_3_1_0.Properties`
            Protobuf structure for properties
        """
        for p in properties.properties:
            context.ink_model.add_property(p.name, p.value)

    @classmethod
    def parse_input_data(cls, context: DecoderContext, input_data: uim_3_1_0.InputData):
        """
        Parse input data Protobuf structure and assign it to internal structure.

        Parameters
        ----------
        context: DecoderContext
            Decoder context
        input_data: uim_3_1_0.InputData
            Protobuf structure for input data (sensor data)s
        """
        input_context_data: uim_3_1_0.InputContextData = input_data.inputContextData
        # Parse Input Contexts
        for inputContext in input_context_data.inputContexts:
            input_context: InputContext = InputContext(
                Identifier.from_bytes(inputContext.id),
                Identifier.from_bytes(inputContext.environmentID),
                Identifier.from_bytes(inputContext.sensorContextID))
            context.ink_model.input_configuration.input_contexts.append(input_context)

        # Parse Ink Input Providers
        for inkInputProvider in input_context_data.inkInputProviders:
            properties: list = CodecDecoder.__parse_properties__(inkInputProvider.properties)
            ink_input_provider: InkInputProvider = InkInputProvider(
                Identifier.from_bytes(inkInputProvider.id),
                UIMDecoder310.MAP_INPUT_PROVIDER_TYPE[inkInputProvider.type],
                properties
            )
            context.ink_model.input_configuration.ink_input_providers.append(ink_input_provider)

        # Parse Input Devices
        for inputDevice in input_context_data.inputDevices:
            properties: list = CodecDecoder.__parse_properties__(inputDevice.properties)
            input_device: InputDevice = InputDevice(
                Identifier.from_bytes(inputDevice.id),
                properties
            )
            context.ink_model.input_configuration.devices.append(input_device)

        # Parse Environments
        for e in input_context_data.environments:
            properties: list = CodecDecoder.__parse_properties__(e.properties)
            environment: Environment = Environment(
                Identifier.from_bytes(e.id),
                properties
            )
            context.ink_model.input_configuration.environments.append(environment)

        # Parse Sensor Data Contexts
        for sensorContext in input_context_data.sensorContexts:
            sensor_channels_contexts: list = []

            # Parse Sensor Channels Contexts
            for sensorChannelsContext in sensorContext.sensorChannelsContext:
                channels: list = []

                # Parse Sensor Channels
                for sensorChannel in sensorChannelsContext.channels:
                    input_provider_uuid: Optional[uuid.UUID] = None
                    if sensorChannelsContext.inkInputProviderID:
                        input_provider_uuid = Identifier.from_bytes(sensorChannelsContext.inkInputProviderID)
                    sensor_channel: SensorChannel = SensorChannel(
                        Identifier.from_bytes(sensorChannel.id),
                        UIMDecoder310.MAP_CHANNEL_TYPE[sensorChannel.type],
                        UIMDecoder310.MAP_INK_METRICS_TYPE[sensorChannel.metric],
                        sensorChannel.resolution,
                        sensorChannel.min,
                        sensorChannel.max,
                        sensorChannel.precision,
                        data_type=DataType.FLOAT32,
                        ink_input_provider_id=input_provider_uuid,
                        input_device_id=Identifier.from_bytes(sensorChannelsContext.inputDeviceID)
                    )
                    channels.append(sensor_channel)
                # Check for input input provider uuid
                input_provider_uuid: Optional[uuid.UUID] = None
                if sensorChannelsContext.inkInputProviderID:
                    input_provider_uuid = Identifier.from_bytes(sensorChannelsContext.inkInputProviderID)
                # Sensor channels context
                sensor_channel_context: SensorChannelsContext = SensorChannelsContext(
                    Identifier.from_bytes(sensorChannelsContext.id),
                    channels,
                    sensorChannelsContext.samplingRateHint,
                    sensorChannelsContext.latency,
                    input_provider_uuid,
                    Identifier.from_bytes(sensorChannelsContext.inputDeviceID),
                )
                sensor_channels_contexts.append(sensor_channel_context)
            # Sensor context
            sensor_context: SensorContext = SensorContext(
                Identifier.from_bytes(sensorContext.id),
                sensor_channels_contexts
            )
            context.ink_model.input_configuration.sensor_contexts.append(sensor_context)

        # Parse Sensor Data
        sensor_data_array: list = []
        for sensorData in input_data.sensorData:
            input_context: InputContext = context.ink_model.input_configuration. \
                get_input_context(Identifier.from_bytes(sensorData.inputContextID))
            sensor_ctx: SensorContext = context.ink_model.input_configuration. \
                get_sensor_context(input_context.sensor_context_id)
            # Add sensor data
            sensor_data: SensorData = SensorData(
                Identifier.from_bytes(sensorData.id),
                Identifier.from_bytes(sensorData.inputContextID),
                UIMDecoder310.MAP_STATE_TYPE[sensorData.state],
                sensorData.timestamp
            )
            # Adding all channels
            for dataChannel in sensorData.dataChannels:
                sensor_type: SensorChannel = sensor_ctx.get_channel_by_id(
                    Identifier.from_bytes(dataChannel.sensorChannelID)
                )
                if sensor_type.type == InkSensorType.TIMESTAMP:
                    ctx: SensorChannel = sensor_ctx.get_channel_by_id(
                        Identifier.from_bytes(dataChannel.sensorChannelID)
                    )
                    channel_data: ChannelData = ChannelData(
                        Identifier.from_bytes(dataChannel.sensorChannelID),
                        CodecDecoder.__decode__(dataChannel.values, ctx.precision, ctx.resolution,
                                                start_value=sensorData.timestamp, data_type=float),
                    )
                    sensor_data.add_timestamp_data(sensor_type, channel_data.values)
                else:
                    ctx: SensorChannel = sensor_ctx.get_channel_by_id(
                        Identifier.from_bytes(dataChannel.sensorChannelID)
                    )
                    channel_data: ChannelData = ChannelData(
                        Identifier.from_bytes(dataChannel.sensorChannelID),
                        CodecDecoder.__decode__(dataChannel.values, ctx.precision, ctx.resolution),
                    )
                    sensor_data.add_data(sensor_type, channel_data.values)
            sensor_data_array.append(sensor_data)

        context.ink_model.sensor_data.sensor_data = sensor_data_array

    @classmethod
    def parse_ink_data(cls, context: DecoderContext, ink_data: uim_3_1_0.InkData):
        """
        Parse Protobuf structure and assign it to internal structure.

        Parameters
        ----------
        context: DecoderContext
            Decoder context
        ink_data: uim_3_1_0.InkData
            Protobuf structure for ink data
        """
        # First you need a root group to contain the strokes
        for p in ink_data.properties:
            # Decode RGBA value
            red, green, blue, alpha = PathPointProperties.color(p.color)
            path_point_properties: PathPointProperties = PathPointProperties(
                p.size,
                red,
                green,
                blue,
                alpha,
                p.rotation,
                p.scaleX,
                p.scaleY,
                p.scaleZ,
                p.offsetX,
                p.offsetY,
                p.offsetZ,
            )
            context.path_point_properties.append(path_point_properties)
        # Strokes
        idx: int = 0
        for s in ink_data.strokes:
            # Check if sensor id exists
            sensor_id: Optional[uuid.UUID] = None
            if s.sensorDataID:
                sensor_id = Identifier.from_bytes(s.sensorDataID)
            stroke: Stroke = Stroke(
                sid=Identifier.from_bytes(s.id),
                sensor_data_offset=s.sensorDataOffset,
                sensor_data_id=sensor_id,
                sensor_data_mapping=s.sensorDataMapping,
                random_seed=s.randomSeed,
                property_index=s.propertiesIndex
            )
            stroke.start_parameter = s.startParameter
            stroke.end_parameter = s.endParameter
            if len(s.splineData.splineX) > 0:
                splines: uim_3_1_0.Stroke.SplineData = s.splineData
                spline_x: list = list(splines.splineX)
                spline_y: list = list(splines.splineY)
                spline_z: list = list(splines.splineZ)
                sizes: list = list(splines.size)
                rotation: list = list(splines.rotation)
                scale_x: list = list(splines.scaleX)
                scale_y: list = list(splines.scaleY)
                scale_z: list = list(splines.scaleZ)
                offset_x: list = list(splines.offsetX)
                offset_y: list = list(splines.offsetY)
                offset_z: list = list(splines.offsetZ)
                list_red: list = list(splines.red)
                list_green: list = list(splines.green)
                list_blue: list = list(splines.blue)
                list_alpha: list = list(splines.alpha)
            else:
                splines: uim_3_1_0.Stroke.SplineCompressed = s.splineCompressed
                scheme: PrecisionScheme = PrecisionScheme()
                if s.precisions:
                    scheme.value = s.precisions
                spline_x: list = CodecDecoder.__decode__(list(splines.splineX), precision=scheme.position_precision)
                spline_y: list = CodecDecoder.__decode__(list(splines.splineY), precision=scheme.position_precision)
                spline_z: list = CodecDecoder.__decode__(list(splines.splineZ), precision=scheme.position_precision)
                sizes: list = CodecDecoder.__decode__(list(splines.size), precision=scheme.size_precision)
                rotation: list = CodecDecoder.__decode__(list(splines.rotation), precision=scheme.rotation_precision)
                scale_x: list = CodecDecoder.__decode__(list(splines.scaleX), precision=scheme.scale_precision)
                scale_y: list = CodecDecoder.__decode__(list(splines.scaleY), precision=scheme.scale_precision)
                scale_z: list = CodecDecoder.__decode__(list(splines.scaleZ), precision=scheme.scale_precision)
                offset_x: list = CodecDecoder.__decode__(list(splines.offsetX), precision=scheme.offset_precision)
                offset_y: list = CodecDecoder.__decode__(list(splines.offsetY), precision=scheme.offset_precision)
                offset_z: list = CodecDecoder.__decode__(list(splines.offsetZ), precision=scheme.offset_precision)
                list_red: list = list(splines.red)
                list_green: list = list(splines.green)
                list_blue: list = list(splines.blue)
                list_alpha: list = list(splines.alpha)
                stroke.precision_scheme = scheme
            stroke.splines_x = spline_x
            stroke.splines_y = spline_y
            stroke.splines_z = spline_z
            stroke.sizes = sizes
            stroke.rotations = rotation
            stroke.scales_x = scale_x
            stroke.scales_y = scale_y
            stroke.scales_z = scale_z
            stroke.offsets_x = offset_x
            stroke.offsets_y = offset_y
            stroke.offsets_z = offset_z
            stroke.red = list_red
            stroke.green = list_green
            stroke.blue = list_blue
            stroke.alpha = list_alpha
            props: Optional[PathPointProperties] = None
            brush: Optional[str] = None
            if s.brushURIIndex:
                brush_index: int = s.brushURIIndex - 1
                brush = ink_data.brushURIs[brush_index]
            if s.propertiesIndex:
                props = context.path_point_properties[s.propertiesIndex - 1]
            # Set style
            stroke.style = Style(properties=props, brush_uri=brush, particles_random_seed=s.randomSeed)
            if s.renderModeURIIndex > 0:
                stroke.style.render_mode_uri = ink_data.renderModeURIs[s.renderModeURIIndex - 1]
            idx += 1
            context.strokes.append(stroke)
        # Unit scale
        context.ink_model.unit_scale_factor = ink_data.unitScaleFactor
        if ink_data.transform.m00 > 0:
            context.ink_model.transform = [
                [ink_data.transform.m00, ink_data.transform.m01, ink_data.transform.m02, ink_data.transform.m03],
                [ink_data.transform.m10, ink_data.transform.m11, ink_data.transform.m12, ink_data.transform.m13],
                [ink_data.transform.m20, ink_data.transform.m21, ink_data.transform.m22, ink_data.transform.m23],
                [ink_data.transform.m30, ink_data.transform.m31, ink_data.transform.m32, ink_data.transform.m33]
            ]

    @classmethod
    def parse_knowledge(cls, context: DecoderContext, triple_store: uim_3_1_0.TripleStore):
        """
        Parse TripleStore protobuf message and return `TripleStore` object.
        Parameters
        ----------
        context: DecoderContext
            Decoder context
        triple_store: TripleStore
            triple_store protobuf message 'TripleStore'
        """
        for statement in triple_store.statements:
            context.ink_model.add_semantic_triple(statement.subject, statement.predicate, statement.object)

    @classmethod
    def parse_ink_structure(cls, context: DecoderContext, ink_structure: uim_3_1_0.InkStructure):
        UIMDecoder310.__parse_ink_tree__(context, ink_structure.inkTree)
        for view in ink_structure.views:
            UIMDecoder310.__parse_ink_tree__(context, view)

    @classmethod
    def __parse_ink_tree__(cls, context: DecoderContext, proto_tree: uim_3_1_0.InkTree):
        stack: List[StrokeGroupNode] = []
        # Sanity checks
        if proto_tree is None or len(proto_tree.tree) == 0:
            raise FormatException("Tree is empty")
        if proto_tree.tree[0].depth:
            raise FormatException("Tree root depth must be 0")
        view_name: str = proto_tree.name
        if proto_tree.name == '':
            tree: InkTree = InkTree(CommonViews.MAIN_INK_TREE.value)
            context.ink_model.ink_tree = tree
        else:
            tree: InkTree = InkTree(view_name)
            context.ink_model.add_tree(tree)
        # Root element
        one_of: str = proto_tree.tree[0].WhichOneof("id")
        if one_of == 'index':
            raise FormatException("Invalid tree root type")
        root_id: bytes = getattr(proto_tree.tree[0], one_of)
        prev_node: StrokeGroupNode = StrokeGroupNode(Identifier.from_bytes(root_id))
        tree.root = prev_node
        if proto_tree.tree[0].bounds:
            tree.root.group_bounding_box = UIMDecoder310.__extract_bounding_box__(proto_tree.tree[0].bounds)
        # Parent
        parent: StrokeGroupNode = tree.root
        # Iterate over all children of root
        for node_idx in range(1, len(proto_tree.tree)):
            node: uim_3_1_0.Node = proto_tree.tree[node_idx]
            if node.depth > len(stack):
                stack.append(parent)
                parent = prev_node
            elif node.depth < len(stack):
                while node.depth < len(stack):
                    parent = stack.pop()

            one_of: str = node.WhichOneof("id")
            value: Any = getattr(node, one_of)
            bbox: BoundingBox = UIMDecoder310.__extract_bounding_box__(node.bounds)
            # Handle different node types
            if one_of == 'groupID':  # Stroke Group Node
                group_id: uuid.UUID = Identifier.from_bytes(value)
                new_node: StrokeGroupNode = StrokeGroupNode(group_id)
                new_node.group_bounding_box = bbox
                # remember current node
                prev_node = new_node
            else:  # Stroke Node
                index: int = value
                if index > len(context.strokes):
                    raise FormatException(f"Reference stroke with index:= {index} does not exist in UIM.")
                stroke: Stroke = context.strokes[index]
                fragment: Optional[StrokeFragment] = None
                # Fragment
                if node.interval.toIndex > 0:
                    fragment: StrokeFragment = StrokeFragment(node.interval.fromIndex, node.interval.toIndex,
                                                              node.interval.fromTValue, node.interval.toTValue)
                # Create Stroke node
                new_node: StrokeNode = StrokeNode(stroke=stroke, fragment=fragment)
                new_node.group_bounding_box = bbox
            parent.add(new_node)

    @staticmethod
    def four_cc(content: bytes) -> Tuple[int, int, int, ContentType, CompressionType]:
        """
        Parse the version information.

        Parameters
        ----------
        content: bytes
            RIFF bytes

        Returns
        -------
            chunk_major_version: int
                Major version of the file
            chunk_minor_version: int
                Minor version of the file
            chunk_patch_version: int
                Patch version of the file
            content_type: `ContentType`
                Content type of the file Protobuf, text, binary, ...
            compression_type: `CompressionType
                Type of compression used for encoding the content.
        """
        chunk_major_version: int = int.from_bytes(content[0:1], byteorder='big')
        chunk_minor_version: int = int.from_bytes(content[1:2], byteorder='big')
        chunk_patch_version: int = int.from_bytes(content[2:3], byteorder='big')
        content_type: bytes = content[3:4]
        compression_type: bytes = content[4:5]
        return chunk_major_version, chunk_minor_version, chunk_patch_version, \
            UIMDecoder310.MAP_CONTENT_TYPE[content_type], UIMDecoder310.MAP_COMPRESSION_TYPE[compression_type]

    @staticmethod
    def __extract_bounding_box__(rect: uim_3_1_0.Rectangle) -> BoundingBox:
        if rect:
            return BoundingBox(rect.x, rect.y, rect.width, rect.height)
        return BoundingBox(0., 0., 0., 0.)

    @staticmethod
    def __read_size__(riff: BytesIO) -> int:
        return ctypes.c_uint32(int.from_bytes(riff.read(4), byteorder='little')).value

    @classmethod
    def __decode_uim_chunk__(cls, content: bytes, compression: CompressionType) -> bytes:
        if compression == CompressionType.ZIP:
            return content
        elif compression == CompressionType.LZMA:
            return content
        return content

    @classmethod
    def decode(cls, riff: BytesIO, size_head: int):
        """
       Decoding Universal Ink Model (RIFF / Protobuf encoded) content file.

       Parameters
       ----------
       riff: `BytesIO`
           RIFF content with encoded UIM v3.1.0 content.
       size_head: `int`
           Size of  the header

       Returns
       -------
           model - `InkModel`
               Parsed `InkModel` from UIM v3.1.0 ink content
       """
        # Reserved byte after version
        _ = riff.read(1)
        num_chunks: int = int((size_head - 4) / 8)
        chunk_desc: list = []
        # Collect the description of the chunks
        for i in range(num_chunks):
            chunk_desc.append(UIMDecoder310.four_cc(riff.read(CHUNK_DESCRIPTION)))
        # Content parser
        uim_content_parser: UIMDecoder310 = UIMDecoder310()
        context: DecoderContext = DecoderContext(version=SupportedFormats.UIM_VERSION_3_1_0.value,
                                                 ink_model=InkModel(SupportedFormats.UIM_VERSION_3_1_0.value))
        # Iterate over chunks
        for j in range(num_chunks):
            desc: list = chunk_desc[j]
            chunk_id = riff.read(CHUNK_ID_BYTES_SIZE)
            chunk_data_length: int = UIMDecoder310.__read_size__(riff)
            chunk_content: bytes = riff.read(chunk_data_length)
            if desc[0] == 3 and desc[1] == 1 and desc[2] == 0:
                if desc[3] == ContentType.PROTOBUF:
                    message: bytes = UIMDecoder310.__decode_uim_chunk__(chunk_content, desc[4])
                    if chunk_id in UIMDecoder310.MAP_CHUNK_TYPE:
                        protobuf_type = UIMDecoder310.MAP_CHUNK_TYPE[chunk_id]
                        protobuf_type.ParseFromString(message)
                        if chunk_id == PROPERTIES_HEADER:
                            uim_content_parser.parse_properties(context, protobuf_type)
                        elif chunk_id == INPUT_DATA_HEADER:
                            uim_content_parser.parse_input_data(context, protobuf_type)
                        elif chunk_id == BRUSHES_HEADER:
                            uim_content_parser.parse_brushes(context, protobuf_type)
                        elif chunk_id == INK_DATA_HEADER:
                            uim_content_parser.parse_ink_data(context, protobuf_type)
                        elif chunk_id == KNOWLEDGE_HEADER:
                            uim_content_parser.parse_knowledge(context, protobuf_type)
                        elif chunk_id == INK_STRUCTURE_HEADER:
                            uim_content_parser.parse_ink_structure(context, protobuf_type)
                else:
                    raise FormatException('Only protobuf decoding is supported.')
            # Check if padding byte is set
            if chunk_data_length % 2 != 0:
                riff.read(1)
        return context.ink_model

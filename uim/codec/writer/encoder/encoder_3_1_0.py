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
import logging
from typing import Any, List, Optional

import bitstring

import uim.codec.format.UIM_3_1_0_pb2 as uim_3_1_0
from uim.codec.base import ContentType, CompressionType, PADDING, DATA_HEADER, HEAD_HEADER, UIM_HEADER, RIFF_HEADER, \
    PROPERTIES_HEADER, SIZE_BYTE_SIZE, INPUT_DATA_HEADER, BRUSHES_HEADER, INK_DATA_HEADER, KNOWLEDGE_HEADER, \
    INK_STRUCTURE_HEADER, RESERVED
from uim.codec.context.encoder import EncoderContext
from uim.codec.context.scheme import PrecisionScheme
from uim.codec.parser.base import SupportedFormats, FormatException
from uim.codec.writer.encoder.base import CodecEncoder
from uim.model.helpers.treeiterator import PreOrderEnumerator
from uim.model.ink import InkModel
from uim.model.inkdata.brush import BrushPolygonUri, RotationMode, BlendModeURIs
from uim.model.inkdata.strokes import Stroke, PathPointProperties
from uim.model.inkinput import inputdata as device, sensordata as sensor
from uim.model.inkinput.inputdata import SensorChannel
from uim.model.semantics import node
from uim.model.semantics.node import BoundingBox, StrokeNode, StrokeGroupNode

# Create the Logger
logger: Optional[logging.Logger] = None

if logger is None:
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)


class UIMEncoder310(CodecEncoder):
    """Universal Ink Model. (v3.1.0)

    Formats the Universal Ink Model Data file codec.
    """
    # Constants for 3.1.0 Writer
    VERSION_MAJOR: bytes = b'\x03'
    VERSION_MINOR: bytes = b'\x01'
    VERSION_PATCH: bytes = b'\x00'
    CHUNK_SIZE: int = 8

    MAP_INK_METRICS_TYPE: dict = {
        device.InkSensorMetricType.TIME: uim_3_1_0.TIME,
        device.InkSensorMetricType.LENGTH: uim_3_1_0.LENGTH,
        device.InkSensorMetricType.FORCE: uim_3_1_0.FORCE,
        device.InkSensorMetricType.ANGLE: uim_3_1_0.ANGLE,
        device.InkSensorMetricType.NORMALIZED: uim_3_1_0.NORMALIZED
    }

    MAP_STATE_TYPE: dict = {
        sensor.InkState.PLANE: uim_3_1_0.PLANE,
        sensor.InkState.HOVERING: uim_3_1_0.HOVERING,
        sensor.InkState.IN_VOLUME: uim_3_1_0.IN_VOLUME,
        sensor.InkState.VOLUME_HOVERING: uim_3_1_0.VOLUME_HOVERING
    }

    MAP_INPUT_PROVIDER: dict = {
        device.InkInputType.PEN: uim_3_1_0.PEN,
        device.InkInputType.MOUSE: uim_3_1_0.MOUSE,
        device.InkInputType.TOUCH: uim_3_1_0.TOUCH,
        device.InkInputType.CONTROLLER: uim_3_1_0.CONTROLLER
    }

    MAP_ROTATION_MODE: dict = {
        RotationMode.NONE: uim_3_1_0.NONE,
        RotationMode.RANDOM: uim_3_1_0.RANDOM,
        RotationMode.TRAJECTORY: uim_3_1_0.TRAJECTORY
    }

    def __init__(self):
        pass

    @classmethod
    def __copy_sensor_data__(cls, s1: uim_3_1_0.SensorData, s2: sensor.SensorData, context: device.SensorContext):
        """
        Copy the SensorData.
        :param s1: protobuf structure
        :param s2: internal structure
        :param context: context for sensor
        """
        s1.id = s2.id.bytes_le
        s1.inputContextID = s2.input_context_id.bytes_le
        if s2.state:
            s1.state = UIMEncoder310.MAP_STATE_TYPE[s2.state]
        s1.timestamp = s2.timestamp
        # Copy data
        for d in s2.data_channels:
            sd: uim_3_1_0.ChannelData = s1.dataChannels.add()
            sd.sensorChannelID = d.id.bytes_le
            channel_ctx: SensorChannel = context.get_channel_by_id(d.id)
            if channel_ctx.type == device.InkSensorType.TIMESTAMP:
                if d.values:
                    conv: List[int] = UIMEncoder310.__encoding__(d.values, 0, channel_ctx.resolution,
                                                                 ignore_first=True)
                    sd.values.extend(conv)
            else:
                conv: List[int] = UIMEncoder310.__encoding__(d.values, channel_ctx.precision, channel_ctx.resolution)
                sd.values.extend(conv)

    @classmethod
    def __serialize_tree_structure__(cls, root_obj: node.InkNode, tree: uim_3_1_0.InkTree, context: EncoderContext,
                                     main_tree: bool = False):
        enumerator = PreOrderEnumerator(root_obj)
        for ink_node in enumerator:
            node_message: uim_3_1_0.Node = tree.tree.add()
            if isinstance(ink_node, StrokeGroupNode):
                node_message.groupID = ink_node.id.bytes_le
            elif isinstance(ink_node, StrokeNode):
                if ink_node.stroke.id in context.stroke_index_map:
                    node_message.index = context.stroke_index_map[ink_node.stroke.id]
                else:
                    raise FormatException(f"Stroke UUID:={ink_node.stroke.id} is not existing in Ink Tree.")

            node_message.depth = enumerator.get_depth_level()

            if isinstance(ink_node, StrokeGroupNode):
                if ink_node.group_bounding_box is not None:
                    box: BoundingBox = ink_node.group_bounding_box
                    if not (box.x == 0. and box.y == 0. and box.width == 0 and box.height == 0.):
                        UIMEncoder310.__copy_rectangle__(node_message.bounds, ink_node.group_bounding_box)
            # Copy interval information
            if not main_tree and isinstance(ink_node, StrokeNode):
                if ink_node.fragment:
                    node_message.interval.fromIndex = ink_node.fragment.from_point_index
                    node_message.interval.toIndex = ink_node.fragment.to_point_index
                    node_message.interval.fromTValue = ink_node.fragment.from_t_value
                    node_message.interval.toTValue = ink_node.fragment.to_t_value

    @classmethod
    def __copy_properties__(cls, p1, p2: list):
        """
        Copy the properties.
        :param p1: protobuf structure
        :param p2: internal structure
        """
        for p in p2:
            prop = p1.add()
            prop.name = p[0]
            if p[1]:
                prop.value = p[1]

    @classmethod
    def __copy_rectangle__(cls, r1: uim_3_1_0.Rectangle, r2: BoundingBox):
        """Copies the rectangle.

        :param r1:
        :param r2:
        :return:
        """
        r1.x = r2.x
        r1.y = r2.y
        r1.width = r2.width
        r1.height = r2.height

    @classmethod
    def __copy_sensor_channel_context__(cls, s1: uim_3_1_0.SensorChannelsContext, s2: device.SensorChannelsContext):
        """
        Copy the SensorChannelContext.
        :param s1: protobuf structure
        :param s2: internal structure
        """
        s1.id = s2.id.bytes_le
        if s2.sampling_rate:
            s1.samplingRateHint = s2.sampling_rate
        if s2.latency:
            s1.latency = s2.latency
        if s2.input_provider_id:
            s1.inkInputProviderID = s2.input_provider_id.bytes_le
        s1.inputDeviceID = s2.input_device_id.bytes_le
        for channel in s2.channels:
            c = s1.channels.add()
            UIMEncoder310.__copy_sensor_channel__(c, channel)

    @classmethod
    def __copy_sensor_channel__(cls, s1: uim_3_1_0.SensorChannel, s2: device.SensorChannel):
        """
        Copy the SensorChannel.
        :param s1: protobuf structure
        :param s2: internal structure
        """
        s1.id = s2.id.bytes_le
        s1.type = s2.type.value
        if s2.resolution:
            s1.resolution = s2.resolution
        if s2.min:
            s1.min = s2.min
        if s2.max:
            s1.max = s2.max
        if s2.precision:
            s1.precision = s2.precision
        s1.metric = UIMEncoder310.MAP_INK_METRICS_TYPE[s2.metric]

    @classmethod
    def __write_chunk__(cls, header: bytes, description: bitstring.BitStream, stream: bitstring.BitStream,
                        structure: Any, content_type: ContentType, compression: CompressionType):
        if compression != CompressionType.NONE:
            raise NotImplementedError(f"Compression: {compression.name} is not yet supported.")
        if content_type != ContentType.PROTOBUF:
            raise NotImplementedError(f"Content Type: {content_type.name} is not yet supported.")
        protobuf_content_buffer: bytes = bytes(structure.SerializeToString())
        # Description header
        # Each chunk descriptor occupies 8 bytes and is defined as follows:
        # Byte 0        | Byte 1       | Byte 2 | Byte 3       | Byte 4            | Byte 5   | Byte 6   | Byte 7   |
        # -----------------------------------------------------------------------------------------------------------
        # Chunk version                         | Content Type | Compression Type  | Reserved | Reserved | Reserved |
        # -----------------------------------------------------------------------------------------------------------
        # Major	        | Minor	       | Patch  |              |                   |          |          |          |
        description.append(UIMEncoder310.VERSION_MAJOR)
        description.append(UIMEncoder310.VERSION_MINOR)
        description.append(UIMEncoder310.VERSION_PATCH)
        description.append(content_type.value)
        description.append(compression.value)
        description.append(RESERVED)
        description.append(RESERVED)
        description.append(RESERVED)
        # Size of the protobuf message content
        chunk_data_size: int = len(protobuf_content_buffer)
        stream.append(header)
        stream.append(int(chunk_data_size).to_bytes(SIZE_BYTE_SIZE, byteorder="little"))
        stream.append(protobuf_content_buffer)
        # Adding padding byte
        if len(protobuf_content_buffer) % 2 != 0:
            stream.append(PADDING)
        logger.debug(f'Decode CHUNK: {header.decode("utf-8")}: {chunk_data_size} bytes')

    def encode(self, ink_model: InkModel, *args, **kwargs) -> bytes:
        """Formats input data document in the WILL 3.0 codec.
        :param ink_model: InkObject -
            InkObject object
        :param kwargs:
            format:=[json|binary] : Use json representation, [default:=binary]
        :return:
        """
        if not isinstance(ink_model, InkModel):
            raise Exception('Not an Ink Document object!')
        context: EncoderContext = EncoderContext(version=SupportedFormats.UIM_VERSION_3_1_0.value, ink_model=ink_model)
        # Content buffer
        buffer: bitstring.BitStream = bitstring.BitStream()
        # Description header for chunk
        header: bitstring.BitStream = bitstring.BitStream()
        # Serialize the different chunks
        head_chunk_data_size: int = len(DATA_HEADER)
        # 0: PRPS - Properties
        if ink_model.has_properties():
            properties: uim_3_1_0.Properties = UIMEncoder310.__serialize_properties__(context)
            UIMEncoder310.__write_chunk__(PROPERTIES_HEADER, header, buffer, properties, ContentType.PROTOBUF,
                                          CompressionType.NONE)
            head_chunk_data_size += UIMEncoder310.CHUNK_SIZE
        # 1: INPT - InputData
        if ink_model.has_input_data():
            input_data: uim_3_1_0.InputData = UIMEncoder310.__serialize_input_data__(context)
            UIMEncoder310.__write_chunk__(INPUT_DATA_HEADER, header, buffer, input_data, ContentType.PROTOBUF,
                                          CompressionType.NONE)
            head_chunk_data_size += UIMEncoder310.CHUNK_SIZE
        # 2: BRSH - Brushes
        if ink_model.has_brushes():
            brushes: uim_3_1_0.Brushes = UIMEncoder310.__serialize_brushes__(context)
            UIMEncoder310.__write_chunk__(BRUSHES_HEADER, header, buffer, brushes, ContentType.PROTOBUF,
                                          CompressionType.NONE)
            head_chunk_data_size += UIMEncoder310.CHUNK_SIZE
        # 3: INKD - InkData
        if ink_model.has_ink_data():
            ink_data: uim_3_1_0.InkData = UIMEncoder310.__serialize_ink_data__(context)
            UIMEncoder310.__write_chunk__(INK_DATA_HEADER, header, buffer, ink_data, ContentType.PROTOBUF,
                                          CompressionType.NONE)
            head_chunk_data_size += UIMEncoder310.CHUNK_SIZE
        # 4: KNWG - Knowledge Graph
        if ink_model.has_knowledge_graph():
            knowledge_graph: uim_3_1_0.TripleStore = UIMEncoder310.__serialize_knowledge_graph__(context)
            UIMEncoder310.__write_chunk__(KNOWLEDGE_HEADER, header, buffer, knowledge_graph, ContentType.PROTOBUF,
                                          CompressionType.NONE)
            head_chunk_data_size += UIMEncoder310.CHUNK_SIZE
        # 5: INKS - Ink Structure
        if ink_model.has_ink_structure():
            ink_structure: uim_3_1_0.InkStructure = UIMEncoder310.__serialize_ink_structure__(context)
            UIMEncoder310.__write_chunk__(INK_STRUCTURE_HEADER, header, buffer, ink_structure, ContentType.PROTOBUF,
                                          CompressionType.NONE)
            head_chunk_data_size += UIMEncoder310.CHUNK_SIZE
        # Write content
        chunk_content: bytes = buffer.tobytes()
        header_content: bytes = header.tobytes()
        # Size of the overall RIFF content
        riff_size: int = len(UIM_HEADER) + len(HEAD_HEADER) + 4 + 4 + len(header_content) + len(chunk_content)
        stream: bitstring.BitStream = bitstring.BitStream()
        # 'RIFF' (4 Bytes)
        stream.append(RIFF_HEADER)
        # Size (uint32): size of all chunks (4 Bytes)
        stream.append(int(riff_size).to_bytes(4, byteorder="little"))
        # 'UINK' (4 Bytes)
        stream.append(UIM_HEADER)
        # 'HEAD' (4 Bytes)
        stream.append(HEAD_HEADER)
        # Size (uint32): size of HEAD chunk (4 Bytes)
        stream.append(int(head_chunk_data_size).to_bytes(4, byteorder="little"))
        # The format version is followed by a list of data chunk descriptors.
        stream.append(UIMEncoder310.VERSION_MAJOR)
        stream.append(UIMEncoder310.VERSION_MINOR)
        stream.append(UIMEncoder310.VERSION_PATCH)
        stream.append(PADDING)
        stream.append(header_content)
        stream.append(chunk_content)
        content: bytes = stream.tobytes()
        assert (len(RIFF_HEADER) + 4 + riff_size) == len(content)
        return content

    @classmethod
    def __serialize_properties__(cls, context: EncoderContext) -> uim_3_1_0.Properties:
        properties: uim_3_1_0.Properties = uim_3_1_0.Properties()
        for p in context.ink_model.properties:
            prop = properties.properties.add()
            prop.name = p[0]
            if p[1]:
                prop.value = p[1]
        return properties

    @classmethod
    def __serialize_input_data__(cls, context: EncoderContext) -> uim_3_1_0.InputData:
        ctx_map: dict = {}
        sensor_ctx: dict = {}
        input_data: uim_3_1_0.InputData = uim_3_1_0.InputData()
        # Environment
        for env in context.ink_model.input_configuration.environments:
            e: uim_3_1_0.Environment = input_data.inputContextData.environments.add()
            e.id = env.id.bytes_le
            UIMEncoder310.__copy_properties__(e.properties, env.properties)

        # Input Provider
        for prov in context.ink_model.input_configuration.ink_input_providers:
            p: uim_3_1_0.InkInputProvider = input_data.inputContextData.inkInputProviders.add()
            p.id = prov.id.bytes_le
            if prov.type:
                p.type = UIMEncoder310.MAP_INPUT_PROVIDER[prov.type]
            UIMEncoder310.__copy_properties__(p.properties, prov.properties)

        # Input Devices
        for dev in context.ink_model.input_configuration.devices:
            d: uim_3_1_0.InputDevice = input_data.inputContextData.inputDevices.add()
            d.id = dev.id.bytes_le
            UIMEncoder310.__copy_properties__(d.properties, dev.properties)

        # Input Context
        for ctx in context.ink_model.input_configuration.input_contexts:
            c = input_data.inputContextData.inputContexts.add()
            c.id = ctx.id.bytes_le
            ctx_map[ctx.id] = ctx.sensor_context_id
            if ctx.environment_id:
                c.environmentID = ctx.environment_id.bytes_le
            if ctx.sensor_context_id:
                c.sensorContextID = ctx.sensor_context_id.bytes_le

        # Sensor Context
        for ctx in context.ink_model.input_configuration.sensor_contexts:
            c = input_data.inputContextData.sensorContexts.add()
            c.id = ctx.id.bytes_le
            # Remember the context
            sensor_ctx[ctx.id] = ctx
            for channel in ctx.sensor_channels_contexts:
                s_ctx = c.sensorChannelsContext.add()
                UIMEncoder310.__copy_sensor_channel_context__(s_ctx, channel)

        # Sensor values
        for sen in context.ink_model.sensor_data.sensor_data:
            s: uim_3_1_0.SensorData = input_data.sensorData.add()
            input_context: uim_3_1_0.InputContext = context.ink_model.input_configuration. \
                get_input_context(sen.input_context_id)
            c: uim_3_1_0.SensorContext = context.ink_model.input_configuration. \
                get_sensor_context(input_context.sensor_context_id)
            UIMEncoder310.__copy_sensor_data__(s, sen, c)
        return input_data

    @classmethod
    def __serialize_brushes__(cls, context: EncoderContext) -> uim_3_1_0.Brushes:
        brushes: uim_3_1_0.Brushes = uim_3_1_0.Brushes()
        # Vector brushes
        for brush in context.ink_model.brushes.vector_brushes:
            # Construct VectorBrush message
            vector_brush: uim_3_1_0.VectorBrush = brushes.vectorBrushes.add()
            vector_brush.name = brush.name
            # Iterate over brush prototypes
            for p in brush.prototypes:
                prototype = vector_brush.prototype.add()
                if isinstance(p, BrushPolygonUri):
                    prototype.shapeURI = p.shape_uri
                    prototype.size = p.min_scale
                else:
                    # Construct BrushPrototype message
                    prototype.coordX.extend(p.coord_x)
                    prototype.coordY.extend(p.coord_y)
                    prototype.coordZ.extend(p.coord_z)
                    prototype.indices.extend(p.indices)
                    prototype.size = p.min_scale
            vector_brush.spacing = brush.spacing
        # Raster brushes
        for brush in context.ink_model.brushes.raster_brushes:
            raster_brush: uim_3_1_0.RasterBrush = brushes.rasterBrushes.add()
            raster_brush.name = brush.name
            raster_brush.spacing = brush.spacing
            raster_brush.scattering = brush.scattering
            raster_brush.rotationMode = UIMEncoder310.MAP_ROTATION_MODE[brush.rotation]
            # Iterate over brush shapes
            for texture in brush.shape_textures:
                raster_brush.shapeTexture.append(texture)
            # Iterate over brush texture uris
            for uri in brush.shape_texture_uris:
                raster_brush.shapeTextureURI.append(uri)
            raster_brush.fillTexture = brush.fill_texture
            raster_brush.fillTextureURI = brush.fill_texture_uri
            raster_brush.fillWidth = brush.fill_width
            raster_brush.fillHeight = brush.fill_height
            raster_brush.randomizeFill = brush.randomize_fill
        return brushes

    @classmethod
    def __serialize_properties_data__(cls, properties: PathPointProperties,
                                      proto_properties: uim_3_1_0.PathPointProperties):
        # Construct Path.Style.PathPointsProperties message

        color: int = PathPointProperties.rgba(properties.red, properties.green, properties.blue, properties.alpha)
        proto_properties.color = color

        if properties.size != 1.0:
            proto_properties.size = properties.size
        if properties.rotation != 0.0:
            proto_properties.rotation = properties.rotation
        if properties.scale_x != 1.0:
            proto_properties.scaleX = properties.scale_x
        if properties.scale_y != 1.0:
            proto_properties.scaleY = properties.scale_y
        if properties.scale_z != 1.0:
            proto_properties.scaleZ = properties.scale_z
        if properties.offset_x != 0.0:
            proto_properties.offsetX = properties.offset_x
        if properties.offset_y != 0.0:
            proto_properties.offsetY = properties.offset_y
        if properties.offset_z != 0.0:
            proto_properties.offsetZ = properties.offset_z

    @classmethod
    def __serialize_transform__(cls, context: EncoderContext, matrix4: uim_3_1_0.Matrix):
        transform = context.ink_model.transform
        matrix4.m00 = transform[0][0]
        matrix4.m01 = transform[0][1]
        matrix4.m02 = transform[0][2]
        matrix4.m03 = transform[0][3]
        matrix4.m10 = transform[1][0]
        matrix4.m11 = transform[1][1]
        matrix4.m12 = transform[1][2]
        matrix4.m13 = transform[1][3]
        matrix4.m20 = transform[2][0]
        matrix4.m21 = transform[2][1]
        matrix4.m22 = transform[2][2]
        matrix4.m23 = transform[2][3]
        matrix4.m30 = transform[3][0]
        matrix4.m31 = transform[3][1]
        matrix4.m32 = transform[3][2]
        matrix4.m33 = transform[3][3]

    @classmethod
    def __serialize_ink_data__(cls, context: EncoderContext) -> uim_3_1_0.InkData:
        ink_data: uim_3_1_0.InkData = uim_3_1_0.InkData()
        ink_data.unitScaleFactor = context.ink_model.unit_scale_factor
        if not context.ink_model.default_transform:
            UIMEncoder310.__serialize_transform__(context, ink_data.transform)
        idx: int = 0
        properties_map: dict = {}
        properties_index: int = 1
        brush_uris: List[str] = []
        render_mode_uris: List[str] = []
        for p in PreOrderEnumerator(context.ink_model.ink_tree.root):
            if isinstance(p, StrokeNode):
                stroke_node: StrokeNode = p
                stroke: Stroke = stroke_node.stroke
                # Construct Path message
                path: uim_3_1_0.Stroke = ink_data.strokes.add()
                path.id = stroke.id.bytes_le
                path.startParameter = stroke.start_parameter
                path.endParameter = stroke.end_parameter
                path.propertiesIndex = stroke.properties_index
                if stroke.precision_scheme is None:  # Uncompressed spline
                    spline_data: uim_3_1_0.Stroke.SplineData = path.splineData
                    spline_data.splineX.extend(stroke.splines_x)
                    spline_data.splineY.extend(stroke.splines_y)
                    spline_data.splineZ.extend(stroke.splines_z)
                    spline_data.red.extend(stroke.red)
                    spline_data.green.extend(stroke.green)
                    spline_data.blue.extend(stroke.blue)
                    spline_data.alpha.extend(stroke.alpha)
                    spline_data.size.extend(stroke.sizes)
                    spline_data.rotation.extend(stroke.rotations)
                    spline_data.scaleX.extend(stroke.scales_x)
                    spline_data.scaleY.extend(stroke.scales_y)
                    spline_data.scaleZ.extend(stroke.scales_z)
                    spline_data.offsetX.extend(stroke.offsets_x)
                    spline_data.offsetY.extend(stroke.offsets_y)
                    spline_data.offsetZ.extend(stroke.offsets_z)
                else:  # Compression enabled
                    spline_compressed: uim_3_1_0.Stroke.SplineCompressed = path.splineCompressed
                    encoding: PrecisionScheme = stroke.precision_scheme
                    spline_compressed.splineX.extend(UIMEncoder310.__encoding__(stroke.splines_x,
                                                                                encoding.position_precision))
                    spline_compressed.splineY.extend(UIMEncoder310.__encoding__(stroke.splines_y,
                                                                                encoding.position_precision))
                    spline_compressed.splineZ.extend(UIMEncoder310.__encoding__(stroke.splines_z,
                                                                                encoding.position_precision))
                    spline_compressed.red.extend(stroke.red)
                    spline_compressed.green.extend(stroke.green)
                    spline_compressed.blue.extend(stroke.blue)
                    spline_compressed.alpha.extend(stroke.alpha)
                    spline_compressed.size.extend(UIMEncoder310.__encoding__(stroke.sizes, encoding.size_precision))
                    spline_compressed.rotation.extend(UIMEncoder310.__encoding__(stroke.rotations,
                                                                                 encoding.rotation_precision))
                    spline_compressed.scaleX.extend(UIMEncoder310.__encoding__(stroke.scales_x,
                                                                               encoding.scale_precision))
                    spline_compressed.scaleY.extend(UIMEncoder310.__encoding__(stroke.scales_y,
                                                                               encoding.scale_precision))
                    spline_compressed.scaleZ.extend(UIMEncoder310.__encoding__(stroke.scales_z,
                                                                               encoding.scale_precision))
                    spline_compressed.offsetX.extend(UIMEncoder310.__encoding__(stroke.offsets_x,
                                                                                encoding.offset_precision))
                    spline_compressed.offsetY.extend(UIMEncoder310.__encoding__(stroke.offsets_y,
                                                                                encoding.offset_precision))
                    spline_compressed.offsetZ.extend(UIMEncoder310.__encoding__(stroke.offsets_z,
                                                                                encoding.offset_precision))
                    path.precisions = stroke.precision_scheme.value

                path.sensorDataOffset = stroke.sensor_data_offset
                # Link to sensor data
                if stroke.sensor_data_id:
                    path.sensorDataID = stroke.sensor_data_id.bytes_le
                path.sensorDataMapping.extend(stroke.sensor_data_mapping)
                # Construct Path.Style message
                if stroke.style:
                    p_path_point_properties: PathPointProperties = stroke.style.path_point_properties
                    if p_path_point_properties.id not in properties_map:
                        properties_map[p_path_point_properties.id] = properties_index
                        properties_index += 1
                        UIMEncoder310.__serialize_properties_data__(p_path_point_properties, ink_data.properties.add())
                    stroke.propertiesIndex = properties_map[p_path_point_properties.id]
                    path.randomSeed = stroke.style.particles_random_seed
                    path.propertiesIndex = properties_map[p_path_point_properties.id]
                    if stroke.style.brush_uri is not None:
                        if stroke.style.brush_uri not in brush_uris:
                            brush_uris.append(stroke.style.brush_uri)
                        # Index is 1-based
                        path.brushURIIndex = brush_uris.index(stroke.style.brush_uri) + 1
                    if stroke.style.render_mode_uri != BlendModeURIs.SOURCE_OVER:
                        if stroke.style.render_mode_uri not in render_mode_uris:
                            render_mode_uris.append(stroke.style.render_mode_uri)
                        # Index is 1-based
                        path.renderModeURIIndex = render_mode_uris.index(stroke.style.render_mode_uri) + 1
                context.stroke_index_map[stroke.id] = idx
                idx += 1
        if len(render_mode_uris) > 0:
            ink_data.renderModeURIs.extend(render_mode_uris)
        ink_data.brushURIs.extend(brush_uris)
        return ink_data

    @classmethod
    def __serialize_knowledge_graph__(cls, context: EncoderContext):
        triple_store: uim_3_1_0.TripleStore = uim_3_1_0.TripleStore()
        # Statements
        for stmt in context.ink_model.knowledge_graph.statements:
            if (stmt.subject is not None and stmt.subject != '') and \
                    (stmt.predicate is not None and stmt.predicate != ''):
                n_stmt = triple_store.statements.add()
                subject_uri: str = stmt.subject
                n_stmt.subject = subject_uri
                n_stmt.predicate = stmt.predicate
                n_stmt.object = stmt.object if stmt.object is not None else ''
        return triple_store

    @classmethod
    def __serialize_ink_structure__(cls, context: EncoderContext):
        ink_structure: uim_3_1_0.InkStructure = uim_3_1_0.InkStructure()
        # Main tree
        if context.ink_model.ink_tree:
            UIMEncoder310.__serialize_tree_structure__(context.ink_model.ink_tree.root, ink_structure.inkTree,
                                                       context, main_tree=True)
        # Content views
        for view in context.ink_model.views:
            view_message: uim_3_1_0.InkTree = ink_structure.views.add()
            view_message.name = context.view_name(view.name, SupportedFormats.UIM_VERSION_3_1_0)
            if view.root:
                UIMEncoder310.__serialize_tree_structure__(view.root, view_message, context)
        return ink_structure

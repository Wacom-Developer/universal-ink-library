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
from typing import List, BinaryIO, Dict, Optional

from google.protobuf import json_format

import uim.codec.format.UIM_3_0_0_pb2 as uim_3_0_0
from uim.codec.base import DATA_HEADER
from uim.codec.context.decoder import DecoderContext
from uim.codec.parser.base import FormatException, SupportedFormats
from uim.codec.parser.decoder.base import CodecDecoder
from uim.model.base import UUIDIdentifier, Identifier
from uim.model.ink import InkModel, InkTree
from uim.model.inkdata.brush import RasterBrush, VectorBrush, BrushPolygon, BlendMode, BrushPolygonUri, RotationMode
from uim.model.inkdata.strokes import Stroke, Style, PathPointProperties
from uim.model.inkinput.inputdata import InkSensorType, InputContext, SensorContext, SensorChannel, \
    InkSensorMetricType, InkInputType, InputDevice, InkInputProvider, Environment, SensorChannelsContext, DataType
from uim.model.inkinput.sensordata import SensorData, ChannelData, InkState
from uim.model.semantics.node import BoundingBox, StrokeNode, StrokeGroupNode
from uim.model.semantics.syntax import CommonViews


class UIMDecoder300(CodecDecoder):
    """
    The UIMDecoder300 decodes the Universal Ink Model v3.0.0 and maps it into the model for v3.1.0.

    References
    ----------
    [1]  Universal Ink Model documentation - URL https://developer-docs.wacom.com/sdk-for-ink/docs/model
    """

    MAP_INK_METRICS_TYPE: Dict[int, InkSensorMetricType] = {
        uim_3_0_0.LENGTH: InkSensorMetricType.LENGTH,
        uim_3_0_0.TIME: InkSensorMetricType.TIME,
        uim_3_0_0.FORCE: InkSensorMetricType.FORCE,
        uim_3_0_0.ANGLE: InkSensorMetricType.ANGLE,
        uim_3_0_0.NORMALIZED: InkSensorMetricType.NORMALIZED
    }
    """Mapping metric types from UIM v3.0.0 to internal enum."""

    MAP_STATE_TYPE: Dict[int, InkState] = {
        uim_3_0_0.PLANE: InkState.PLANE,
        uim_3_0_0.HOVERING: InkState.HOVERING,
        uim_3_0_0.IN_VOLUME: InkState.IN_VOLUME,
        uim_3_0_0.VOLUME_HOVERING: InkState.VOLUME_HOVERING
    }
    """Mapping of the uim input data states."""

    MAP_CHANNEL_TYPE: Dict[int, InkSensorType] = {
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
    """Mapping for channel type."""

    MAP_INPUT_PROVIDER_TYPE: Dict[int, InkInputType] = {
        InkInputType.PEN.value: InkInputType.PEN,
        InkInputType.TOUCH.value: InkInputType.TOUCH,
        InkInputType.CONTROLLER.value: InkInputType.CONTROLLER,
        InkInputType.MOUSE.value: InkInputType.MOUSE
    }
    """Mapping for input provider."""

    MAP_BLEND_MODE: Dict[int, BlendMode] = {
        uim_3_0_0.SOURCE_OVER: BlendMode.SOURCE_OVER,
        uim_3_0_0.DESTINATION_OVER: BlendMode.DESTINATION_OVER,
        uim_3_0_0.DESTINATION_OUT: BlendMode.DESTINATION_OUT,
        uim_3_0_0.LIGHTER: BlendMode.LIGHTER,
        uim_3_0_0.COPY: BlendMode.COPY,
        uim_3_0_0.MIN: BlendMode.MIN,
        uim_3_0_0.MAX: BlendMode.MAX
    }
    """Mapping for blending mode."""

    # Map for rotation mode
    MAP_ROTATION_MODE: Dict[int, RotationMode] = {
        uim_3_0_0.NONE: RotationMode.NONE,
        uim_3_0_0.RANDOM: RotationMode.RANDOM,
        uim_3_0_0.TRAJECTORY: RotationMode.TRAJECTORY
    }

    def __init__(self):
        pass

    @classmethod
    def decode(cls, riff: BytesIO, size_head: int) -> InkModel:
        """
        Decoding Universal Ink Model (RIFF / Protobuf encoded) content file.

        Parameters
        ----------
        riff: `BytesIO`
            RIFF content with encoded UIM v3.0.0 content.
        size_head: `int`
            Size of  the header

        Returns
        -------
            model - `InkModel`
                Parsed `InkModel` from UIM v3.0.0 ink content
        """
        riff.read((size_head - 3) + 1)
        if riff.read(4) != DATA_HEADER:
            raise FormatException('Data header missing.')
        data_size = ctypes.c_uint32(int.from_bytes(riff.read(4), byteorder='little')).value
        message: bytes = riff.read(data_size)
        # read document
        document: uim_3_0_0.InkObject = uim_3_0_0.InkObject()
        document.ParseFromString(message)
        return UIMDecoder300.decode_document(document)

    @classmethod
    def decode_json(cls, fp: BinaryIO) -> InkModel:
        """
        Decoding Universal Ink Model (JSON Protobuf encoded) content file.

        Parameters
        ----------
        fp: `BinaryIO`
            JSON with encoded UIM v3.0.0 content.

        Returns
        -------
            model - `InkModel`
                Parsed `InkModel` from UIM v3.0.0 ink content
        """
        message = fp.read()
        document: uim_3_0_0.InkObject = uim_3_0_0.InkObject()
        document: uim_3_0_0.InkObject = json_format.Parse(message, document)
        return UIMDecoder300.decode_document(document)

    @classmethod
    def decode_document(cls, document: uim_3_0_0.InkObject) -> InkModel:
        """
        Decoding Protobuf content file.

        Parameters
        ----------
        document: `uim_3_0_0.InkObject`
            Parsed protobuf structure.

        Returns
        -------
            model - `InkModel`
                Parsed `InkModel` from UIM v3.0.0 ink content
        """
        context: DecoderContext = DecoderContext(version=SupportedFormats.UIM_VERSION_3_0_0.value,
                                                 ink_model=InkModel(SupportedFormats.UIM_VERSION_3_0_0.value))
        # Set properties
        context.ink_model.properties = CodecDecoder.__parse_properties__(document.properties)
        # Parse input data
        UIMDecoder300.__parse_input_data__(context, document.inputData)
        # Parse ink data
        UIMDecoder300.__parse_ink_data__(context, document.inkData)
        # Parse brushes
        UIMDecoder300.__parse_brushes__(context, document.brushes)
        # Parse main tree
        UIMDecoder300.__parse_ink_tree__(context, document.inkTree, CommonViews.MAIN_INK_TREE.value)
        # Parse view
        for view in document.views:
            UIMDecoder300.__parse_ink_tree__(context, view.tree, view.name)
        # Parse knowledge graph
        UIMDecoder300.__parse_knowledge_graph__(context, document.knowledgeGraph)
        # Finally upgrade the URIs
        context.upgrade_uris()
        return context.ink_model

    @classmethod
    def __parse_input_data__(cls, context: DecoderContext, input_data: uim_3_0_0.InputData):
        input_context_data: uim_3_0_0.InputContextData = input_data.inputContextData
        # Parse Input Contexts
        for inputContext in input_context_data.inputContexts:
            input_context: InputContext = InputContext(
                UUIDIdentifier.str_to_uimid(inputContext.id),
                UUIDIdentifier.str_to_uimid(inputContext.environmentID),
                UUIDIdentifier.str_to_uimid(inputContext.sensorContextID))
            context.ink_model.input_configuration.input_contexts.append(input_context)

        # Parse Ink Input Providers
        for inkInputProvider in input_context_data.inkInputProviders:
            properties = CodecDecoder.__parse_properties__(inkInputProvider.properties)
            ink_input_provider = InkInputProvider(
                UUIDIdentifier.str_to_uimid(inkInputProvider.id),
                UIMDecoder300.MAP_INPUT_PROVIDER_TYPE[inkInputProvider.type],
                properties
            )
            context.ink_model.input_configuration.ink_input_providers.append(ink_input_provider)

        # Parse Input Devices
        for inputDevice in input_context_data.inputDevices:
            properties = CodecDecoder.__parse_properties__(inputDevice.properties)
            input_device: InputDevice = InputDevice(
                UUIDIdentifier.str_to_uimid(inputDevice.id),
                properties
            )
            context.ink_model.input_configuration.devices.append(input_device)

        # Parse Environments
        for environment in input_context_data.environments:
            properties = CodecDecoder.__parse_properties__(environment.properties)
            environment = Environment(UUIDIdentifier.str_to_uimid(environment.id), properties)
            context.ink_model.input_configuration.environments.append(environment)

        # Parse Sensor Data Contexts
        for sensorContext in input_context_data.sensorContexts:
            sensor_channels_contexts: list = []

            # Parse Sensor Channels Contexts
            for sensorChannelsContext in sensorContext.sensorChannelsContext:
                channels: list = []
                input_provider_uuid: Optional[uuid.UUID] = None
                if sensorChannelsContext.inkInputProviderID:
                    input_provider_uuid = Identifier.str_to_uimid(sensorChannelsContext.inkInputProviderID)
                # Parse Sensor Channels
                for sensorChannel in sensorChannelsContext.channels:
                    sensor_channel: SensorChannel = SensorChannel(
                        UUIDIdentifier.str_to_uimid(sensorChannel.id),
                        UIMDecoder300.MAP_CHANNEL_TYPE[sensorChannel.type],
                        UIMDecoder300.MAP_INK_METRICS_TYPE[sensorChannel.metric],
                        sensorChannel.resolution,
                        sensorChannel.min,
                        sensorChannel.max,
                        sensorChannel.precision,
                        data_type=DataType.FLOAT32,
                        ink_input_provider_id=input_provider_uuid,
                        input_device_id=Identifier.str_to_uimid(sensorChannelsContext.inputDeviceID)
                    )
                    channels.append(sensor_channel)
                input_provider_uuid: Optional[uuid.UUID] = None
                if sensorChannelsContext.inkInputProviderID:
                    input_provider_uuid = Identifier.str_to_uimid(sensorChannelsContext.inkInputProviderID)
                sensor_channel_context: SensorChannelsContext = SensorChannelsContext(
                    Identifier.str_to_uimid(sensorChannelsContext.id),
                    channels,
                    sensorChannelsContext.samplingRateHint.value,
                    sensorChannelsContext.latency.value,
                    input_provider_uuid,
                    Identifier.str_to_uimid(sensorChannelsContext.inputDeviceID),
                )
                sensor_channels_contexts.append(sensor_channel_context)
            sensor_context: SensorContext = SensorContext(
                Identifier.str_to_uimid(sensorContext.id),
                sensor_channels_contexts
            )
            context.ink_model.input_configuration.sensor_contexts.append(sensor_context)

        # Parse Sensor Data
        sensor_data_array: list = []
        for sensorData in input_data.sensorData:
            input_context: InputContext = context.ink_model. \
                input_configuration.get_input_context(Identifier.str_to_uimid(sensorData.inputContextID))
            sensor_ctx: SensorContext = context.ink_model.input_configuration. \
                get_sensor_context(input_context.sensor_context_id)
            # Add sensor data
            sensor_data: SensorData = SensorData(
                Identifier.str_to_uimid(sensorData.id),
                Identifier.str_to_uimid(sensorData.inputContextID),
                UIMDecoder300.MAP_STATE_TYPE[sensorData.state],
                sensorData.timestamp
            )
            for dataChannel in sensorData.dataChannels:
                sensor_type: SensorChannel = sensor_ctx.get_channel_by_id(
                    Identifier.str_to_uimid(dataChannel.sensorChannelID)
                )
                if sensor_type.type == InkSensorType.TIMESTAMP:
                    ctx: SensorChannel = sensor_ctx.get_channel_by_id(
                        Identifier.str_to_uimid(dataChannel.sensorChannelID))
                    channel_data: ChannelData = ChannelData(
                        Identifier.str_to_uimid(dataChannel.sensorChannelID),
                        CodecDecoder.__decode__(dataChannel.values, ctx.precision, ctx.resolution,
                                                start_value=sensorData.timestamp, data_type=float),
                    )
                else:
                    ctx: SensorChannel = sensor_ctx.get_channel_by_id(
                        Identifier.str_to_uimid(dataChannel.sensorChannelID)
                    )
                    channel_data: ChannelData = ChannelData(
                        Identifier.str_to_uimid(dataChannel.sensorChannelID),
                        CodecDecoder.__decode__(dataChannel.values, ctx.precision, ctx.resolution),
                    )
                sensor_data.add_data(sensor_type, channel_data.values)

            sensor_data_array.append(sensor_data)

        context.ink_model.sensor_data.sensor_data = sensor_data_array

    @classmethod
    def __parse_ink_data__(cls, context: DecoderContext, ink_data: uim_3_0_0.InkData):
        # Iterate over strokes
        for p in ink_data.strokes:
            properties = p.style.properties
            path_point_properties: PathPointProperties = PathPointProperties(
                properties.size.value,
                properties.red.value,
                properties.green.value,
                properties.blue.value,
                properties.alpha.value,
                properties.rotation.value,
                properties.scaleX.value,
                properties.scaleY.value,
                properties.scaleZ.value,
                properties.offsetX.value,
                properties.offsetY.value,
                properties.offsetZ.value,
            )
            style: Style = Style(
                path_point_properties,
                p.style.brushURI,
                p.style.particlesRandomSeed,
                p.style.renderModeURI
            )
            sensor_id: Optional[uuid.UUID] = None
            if p.sensorDataID:
                sensor_id = Identifier.str_to_uimid(p.sensorDataID)
            stroke: Stroke = Stroke(
                Identifier.str_to_uimid(p.id),
                p.sensorDataOffset,
                sensor_id,
                p.sensorDataMapping,
                style
            )
            stroke.start_parameter = p.startParameter
            stroke.end_parameter = p.endParameter
            stroke.red = list(p.red)
            stroke.green = list(p.green)
            stroke.blue = list(p.blue)
            stroke.alpha = list(p.alpha)
            stroke.splines_x = list(p.splineX)
            stroke.splines_y = list(p.splineY)
            stroke.splines_z = list(p.splineZ)
            stroke.sizes = list(p.size)
            stroke.rotations = list(p.rotation)
            stroke.scales_x = list(p.scaleX)
            stroke.scales_y = list(p.scaleY)
            stroke.scales_z = list(p.scaleZ)
            stroke.offsets_x = list(p.offsetX)
            stroke.offsets_y = list(p.offsetY)
            stroke.offsets_z = list(p.offsetZ)
            context.strokes.append(stroke)

    @classmethod
    def __parse_brushes__(cls, context: DecoderContext, brushes: uim_3_0_0.Brushes):
        # iterate over vector brushes
        for vectorBrush in brushes.vectorBrushes:
            prototypes: list = []
            for p in vectorBrush.prototype:
                if p.shapeURI:
                    brush_prototype: BrushPolygonUri = BrushPolygonUri(p.shapeURI, p.size)
                else:
                    points: list = []
                    for idx in range(len(p.coordX)):
                        points.append((p.coordX[idx], p.coordY[idx]))
                    brush_prototype: BrushPolygon = BrushPolygon(min_scale=p.size, points=points, indices=p.indices)
                prototypes.append(brush_prototype)
            brush: VectorBrush = VectorBrush(
                vectorBrush.name,
                prototypes,
                vectorBrush.spacing
            )
            context.ink_model.brushes.add_vector_brush(brush)
        # Iterate over raster brushes
        for rasterBrush in brushes.rasterBrushes:
            brush: RasterBrush = RasterBrush(
                rasterBrush.name,
                rasterBrush.spacing,
                rasterBrush.scattering,
                UIMDecoder300.MAP_ROTATION_MODE[rasterBrush.rotationMode],
                rasterBrush.shapeTexture,
                rasterBrush.shapeTextureURI,
                rasterBrush.fillTexture,
                rasterBrush.fillTextureURI,
                rasterBrush.fillWidth,
                rasterBrush.fillHeight,
                rasterBrush.randomizeFill,
                UIMDecoder300.MAP_BLEND_MODE[rasterBrush.blendMode]
            )
            context.ink_model.brushes.add_raster_brush(brush)

    @classmethod
    def __extract_bounding_box__(cls, rect: uim_3_0_0.Rectangle) -> BoundingBox:
        if rect:
            return BoundingBox(rect.x, rect.y, rect.width, rect.height)
        return BoundingBox(0., 0., 0., 0.)

    @classmethod
    def __parse_ink_tree__(cls, context: DecoderContext, proto_tree: List[uim_3_0_0.Node], view: str):
        stack: List[StrokeGroupNode] = []
        # Sanity checks
        if proto_tree is None or len(proto_tree) == 0:
            raise FormatException("Tree is empty")
        if proto_tree[0].depth:
            raise FormatException("Tree root depth must be 0")
        # Differentiate between main tree and view
        if view == CommonViews.MAIN_INK_TREE.value:
            tree: InkTree = InkTree(view)
            context.ink_model.ink_tree = tree
        else:
            tree: InkTree = InkTree(view)
            context.ink_model.add_tree(tree)
        # Root element
        root_id: str = proto_tree[0].id
        prev_node: StrokeGroupNode = StrokeGroupNode(Identifier.str_to_uimid(root_id))
        tree.root = prev_node
        tree.root.group_bounding_box = UIMDecoder300.__extract_bounding_box__(proto_tree[0].groupBoundingBox)
        # Parent
        parent: StrokeGroupNode = tree.root
        # Iterate over all children of root
        for node_idx in range(1, len(proto_tree)):
            node: uim_3_0_0.Node = proto_tree[node_idx]
            if node.depth > len(stack):
                stack.append(parent)
                parent = prev_node
            elif node.depth < len(stack):
                while node.depth < len(stack):
                    parent = stack.pop()

            bbox: BoundingBox = UIMDecoder300.__extract_bounding_box__(node.groupBoundingBox)
            # Handle different node types
            if node.type == uim_3_0_0.STROKE_GROUP:  # Stroke Group Node
                group_id: uuid.UUID = Identifier.str_to_uimid(node.id)
                new_node: StrokeGroupNode = StrokeGroupNode(group_id)
                new_node.group_bounding_box = bbox
                # remember current node
                prev_node = new_node
            else:  # Stroke Node
                index: int = node.index
                if index > len(context.strokes):
                    raise FormatException(f"Reference stroke with index:= {index} does not exist in UIM.")
                stroke: Stroke = context.strokes[index]
                # Create Stroke node
                new_node: StrokeNode = StrokeNode(stroke=stroke, fragment=None)
                new_node.group_bounding_box = bbox
            parent.add(new_node)

    @classmethod
    def __parse_knowledge_graph__(cls, context: DecoderContext, knowledge_graph: uim_3_0_0.TripleStore):
        for el in knowledge_graph.statements:
            if el.subject != '':
                context.ink_model.add_semantic_triple(el.subject, el.predicate, el.object)

    @classmethod
    def __parse_transform__(cls, document, ink_object: InkModel):
        """Parse transformation matrix message (Matrix4)."""
        t = document.transform
        matrix: list = [
            [t.m00, t.m01, t.m02, t.m03],
            [t.m10, t.m11, t.m12, t.m13],
            [t.m20, t.m21, t.m22, t.m23],
            [t.m30, t.m31, t.m32, t.m33],
        ]
        ink_object.transform = matrix

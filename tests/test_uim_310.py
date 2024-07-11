# -*- coding: utf-8 -*-
# Copyright © 2021-present Wacom Authors. All Rights Reserved.
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
from io import BytesIO
from pathlib import Path

import bitstring
import pytest

from uim.codec.base import ContentType, CompressionType
from uim.codec.context.decoder import DecoderContext
from uim.codec.context.encoder import EncoderContext
from uim.codec.parser.base import SupportedFormats, FormatException
from uim.codec.parser.uim import UIMParser
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model import UUIDIdentifier
from uim.model.ink import InkModel
from uim.model.inkinput.sensordata import ChannelData
from uim.model.semantics.schema import CommonViews

# Test data directory
test_data_dir: Path = Path(__file__).parent / '../ink/uim_3.1.0/'
raster_data_dir: Path = Path(__file__).parent / '../ink/special'


def uim_files() -> list:
    return [f for f in test_data_dir.iterdir() if f.is_file() and f.name.endswith('.uim')]


@pytest.mark.parametrize('path', uim_files())
def test_uim_3_1_0_bytes_io(path: Path):
    with path.open('rb') as fp:
        uim_bytes: bytes = fp.read()
        parser: UIMParser = UIMParser()
        ink_model: InkModel = parser.parse(BytesIO(uim_bytes))
        assert ink_model.has_brushes()
        assert ink_model.has_ink_data()
        assert ink_model.has_ink_structure()
        assert len(ink_model.strokes) > 0


@pytest.mark.parametrize('path', uim_files())
def test_uim_3_1_0(path: Path):
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(path)
    assert ink_model.has_brushes()
    assert ink_model.has_ink_data()
    assert ink_model.has_ink_structure()
    assert len(ink_model.strokes) > 0
    # Validate encoding
    uim_bytes: bytes = UIMEncoder310().encode(ink_model)
    assert len(uim_bytes) > 0
    # Validate decoding
    ink_model_decoded: InkModel = parser.parse(uim_bytes)
    assert ink_model_decoded.has_brushes()
    assert ink_model_decoded.has_ink_data()
    assert ink_model_decoded.has_ink_structure()
    assert len(ink_model_decoded.strokes) > 0
    # Validate sensor data
    for sd_1, sd_2 in zip(ink_model.sensor_data.sensor_data, ink_model_decoded.sensor_data.sensor_data):
        for s_idx in range(len(sd_1.data_channels)):
            s1_data: ChannelData = sd_1.data_channels[s_idx]
            s2_data: ChannelData = sd_2.data_channels[s_idx]
            # Ids must be the same
            assert s1_data.id == s2_data.id
            for v_idx, val_1 in enumerate(s1_data.values):
                val_2 = sd_2.data_channels[s_idx].values[v_idx]
                assert val_1 == pytest.approx(val_2)
    for str_1, str_2 in zip(ink_model.strokes, ink_model_decoded.strokes):
        # Ids must be the same
        assert str_1.id == str_2.id
    assert str(ink_model) == str(ink_model_decoded)


def test_load_raster():
    """
    Test loading raster data.
    """
    raster_file: Path = raster_data_dir / 'raster.uim'
    parser: UIMParser = UIMParser()
    ink_model: InkModel = parser.parse(raster_file)
    assert ink_model.has_brushes()
    assert len(ink_model.brushes.raster_brushes) == 4
    for raster in ink_model.brushes.raster_brushes:
        assert str(raster)


def test_not_accept():
    """
    Testing type not accepted.
    """
    parser: UIMParser = UIMParser()
    with pytest.raises(TypeError):
        parser.parse(45)


def test_wrong_bytes():
    """
    Test wrong bytes.
    """
    parser: UIMParser = UIMParser()
    with pytest.raises(FormatException):
        parser.parse(BytesIO(b'Hello Ink'))


def test_wrong_version():
    """
    Test wrong version.
    """
    reserved: bytes = b'\x00'
    buffer: bitstring.BitStream = bitstring.BitStream()
    buffer.append(b'RIFF')
    # Size (uint32): size of all chunks (4 Bytes)
    buffer.append(int(0).to_bytes(4, byteorder="little"))
    buffer.append(b'UINK')
    buffer.append(b'HEAD')
    buffer.append(UIMEncoder310.VERSION_MAJOR)
    buffer.append(UIMEncoder310.VERSION_MINOR)
    buffer.append(UIMEncoder310.VERSION_MINOR)
    buffer.append(ContentType.PROTOBUF.value)
    buffer.append(CompressionType.NONE.value)
    buffer.append(reserved)
    buffer.append(reserved)
    buffer.append(reserved)
    parser: UIMParser = UIMParser()
    with pytest.raises(FormatException):
        parser.parse(BytesIO(buffer.tobytes()))


def test_missing_header():
    """
    Test missing header.
    """
    reserved: bytes = b'\x00'
    buffer: bitstring.BitStream = bitstring.BitStream()
    buffer.append(b'RIFF')
    # Size (uint32): size of all chunks (4 Bytes)
    buffer.append(int(0).to_bytes(4, byteorder="little"))
    buffer.append(b'UINK')
    buffer.append(UIMEncoder310.VERSION_MAJOR)
    buffer.append(UIMEncoder310.VERSION_MINOR)
    buffer.append(UIMEncoder310.VERSION_MINOR)
    buffer.append(ContentType.PROTOBUF.value)
    buffer.append(CompressionType.NONE.value)
    buffer.append(reserved)
    buffer.append(reserved)
    buffer.append(reserved)
    parser: UIMParser = UIMParser()
    with pytest.raises(FormatException):
        parser.parse(BytesIO(buffer.tobytes()))


def test_encoder_context():
    """
    Test encoder context.
    """
    assert (EncoderContext.view_name(CommonViews.HWR_VIEW.value, SupportedFormats.UIM_VERSION_3_1_0)
            == CommonViews.HWR_VIEW.value)
    assert (EncoderContext.view_name(CommonViews.LEGACY_HWR_VIEW.value, SupportedFormats.UIM_VERSION_3_1_0)
            == CommonViews.HWR_VIEW.value)
    assert (EncoderContext.view_name(CommonViews.NER_VIEW.value, SupportedFormats.UIM_VERSION_3_1_0)
            == CommonViews.NER_VIEW.value)
    assert (EncoderContext.view_name(CommonViews.LEGACY_NER_VIEW.value, SupportedFormats.UIM_VERSION_3_1_0)
            == CommonViews.NER_VIEW.value)
    assert (EncoderContext.view_name("Undefined", SupportedFormats.UIM_VERSION_3_1_0) == "Undefined")
    with pytest.raises(FormatException):
        # Only UIM 3.1.0 is supported
        EncoderContext.view_name(CommonViews.HWR_VIEW.value, SupportedFormats.UIM_VERSION_3_0_0)

    ink_model: InkModel = InkModel()
    context = EncoderContext(version=SupportedFormats.UIM_VERSION_3_1_0.value, ink_model=ink_model)
    assert context.format_version == SupportedFormats.UIM_VERSION_3_1_0.value


def test_decoder_context():
    """
    Test decoder context.
    """
    ink_model: InkModel = InkModel()
    context = DecoderContext(version=SupportedFormats.UIM_VERSION_3_1_0.value, ink_model=ink_model)
    assert context.format_version == SupportedFormats.UIM_VERSION_3_1_0.value
    with pytest.raises(ValueError):
        context.stroke_by_identifier(UUIDIdentifier.id_generator().hex)

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
import uuid
from pathlib import Path

from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.ink import InkModel
from uim.model.inkdata.brush import BrushPolygonUri, VectorBrush
from uim.model.semantics.schema import SegmentationSchema, CommonViews

from uim.codec.parser.inkml import InkMLParser

if __name__ == '__main__':
    parser: InkMLParser = InkMLParser()
    # Add a brush specified with shape Uris
    bpu_1: BrushPolygonUri = BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=1", min_scale=0.)
    bpu_2: BrushPolygonUri = BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=0.5", min_scale=4.)
    poly_uris: list = [
        bpu_1, bpu_2
    ]
    vector_brush_1: VectorBrush = VectorBrush(
        "app://qa-test-app/vector-brush/MyEllipticBrush",
        poly_uris)
    parser.register_brush(brush_uri='default', brush=vector_brush_1)
    parser.use_brush = 'default'
    device_id: str = uuid.uuid4().hex
    parser.update_default_context(sample_rate=80, serial_number=device_id, manufacturer="Test Manufacturer",
                                  model="Test Model")
    parser.content_view = CommonViews.HWR_VIEW.value
    parser.cropping_ink = True
    parser.default_annotation_type = SegmentationSchema.UNLABELED
    parser.default_xy_resolution = 10
    parser.default_position_precision = 3
    parser.default_value_resolution = 42
    # Kondate database is not using namespace
    parser.default_namespace = ''
    ink_model: InkModel = parser.parse(Path(__file__).parent / '..' / 'ink' / 'inkml' / 'kondate.inkml')
    with Path("kondate.uim").open("wb") as file:
        file.write(UIMEncoder310().encode(ink_model))

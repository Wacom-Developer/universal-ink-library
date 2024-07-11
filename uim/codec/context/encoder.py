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
import uuid
from typing import Dict

from uim.codec.context.version import Version
from uim.codec.parser.base import SupportedFormats, FormatException
from uim.model.ink import InkModel
from uim.model.semantics.schema import CommonViews


class EncoderContext:
    """
    EncoderContext
    ==============

    Context used while encoding an ink file.

    The context is used to store the state of the encoding process, such as the encoded strokes and the
    current state of the ink model.

    Parameters
    ----------
    version: `Version`
        Version of the ink file
    ink_model: `InkModel`
        Reference of the `InkModel` that will be encoded
    """

    def __init__(self, version: Version, ink_model: InkModel):
        self.__format_version: Version = version
        self.__ink_model: InkModel = ink_model
        self.__stroke_index_map: Dict[uuid.UUID, int] = {}

    @property
    def format_version(self) -> Version:
        """Version of the format. (`Version`, read-only)"""
        return self.__format_version

    @property
    def ink_model(self) -> InkModel:
        """Current state of the ink model. (`InkModel`, read-only)"""
        return self.__ink_model

    @property
    def stroke_index_map(self) -> Dict[uuid.UUID, int]:
        """Stroke index map. (`Dict[uuid.UUID, int]`, read-only)"""
        return self.__stroke_index_map

    @staticmethod
    def view_name(view_name: str, target_format: SupportedFormats) -> str:
        """
        Depending on the target format the appropriate view name is chosen.

        Parameters
        ----------
        view_name: `str`
            Name of the view
        target_format: `SupportedFormats`
            Chosen target format

        Returns
        -------
            name - str
                Name of view depending on the format. UIM v3.1.0 and v3.0.0 have different conventions
        """
        if target_format == SupportedFormats.UIM_VERSION_3_1_0:
            if view_name in (CommonViews.HWR_VIEW.value, CommonViews.LEGACY_HWR_VIEW.value):
                return CommonViews.HWR_VIEW.value
            if view_name in (CommonViews.NER_VIEW.value, CommonViews.LEGACY_NER_VIEW.value):
                return CommonViews.NER_VIEW.value
            return view_name
        raise FormatException(f"Not supported version. Format:={target_format}")

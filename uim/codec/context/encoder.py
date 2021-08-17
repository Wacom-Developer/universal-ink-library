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

import uuid
from typing import List, Dict

from uim.codec.context.version import Version
from uim.codec.parser.base import SupportedFormats, FormatException
from uim.model.ink import InkModel
from uim.model.inkdata.strokes import PathPointProperties
from uim.model.semantics.node import StrokeGroupNode
from uim.model.semantics.syntax import CommonViews


class EncoderContext(object):
    """
    Context used while encoding an ink file.

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
        self.__path_properties: List[PathPointProperties] = []
        self.__stroke_uri: Dict[uuid.UUID, StrokeGroupNode] = {}

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

    @property
    def path_point_properties(self) -> List[PathPointProperties]:
        """List of the path point properties. (`List[PathPointProperties]`, read-only)"""
        return self.__path_properties

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
            if view_name == CommonViews.HWR_VIEW.value or view_name == CommonViews.LEGACY_HWR_VIEW.value:
                return CommonViews.HWR_VIEW.value
            elif view_name == CommonViews.NER_VIEW.value or view_name == CommonViews.LEGACY_NER_VIEW.value:
                return CommonViews.NER_VIEW.value
            else:
                return view_name
        elif target_format == SupportedFormats.UIM_VERSION_3_0_0:
            if view_name == CommonViews.HWR_VIEW.value or view_name == CommonViews.LEGACY_HWR_VIEW.value:
                return CommonViews.LEGACY_HWR_VIEW.value
            elif view_name == CommonViews.NER_VIEW.value or view_name == CommonViews.LEGACY_NER_VIEW.value:
                return CommonViews.LEGACY_NER_VIEW.value
            else:
                return view_name
        else:
            raise FormatException(f"Not supported version. Format:={target_format}")

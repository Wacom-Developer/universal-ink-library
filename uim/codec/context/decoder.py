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

from typing import List, Dict

from uim.codec.context.version import Version
from uim.model.helpers.treeiterator import PreOrderEnumerator
from uim.model.ink import InkModel
from uim.model.inkdata.strokes import Stroke, PathPointProperties
from uim.model.semantics.node import StrokeGroupNode


class DecoderContext(object):
    """
    Decoder Context used while parsing an ink file.

    Parameters
    ----------
    version: `Version`
        Version of the parsed ink file
    ink_model: `InkModel`
        Reference of the `InkModel` that will be available after parsing process is finished

    """

    def __init__(self, version: Version, ink_model: InkModel):
        self.__format_version: Version = version
        self.__ink_model: InkModel = ink_model
        self.__strokes: List[Stroke] = []
        self.__stroke_id_map: Dict[str, int] = {}
        self.__path_properties: List[PathPointProperties] = []

    def register_stroke(self, stroke: Stroke, stroke_identifier: str):
        """
        Register a stroke for the context.

        Parameters
        ----------
        stroke: `Stroke`
            Stroke structure
        stroke_identifier: str
            Identifier from a different format
        """
        self.strokes.append(stroke)
        if stroke_identifier:
            self.__stroke_id_map[stroke_identifier] = len(self.strokes) - 1

    def stroke_by_identifier(self, identifier: str) -> Stroke:
        """
        Retrieve stroke by using the registered identifier.

        Parameters
        ----------
        identifier: str
            Registered identifier

        Returns
        -------
        stroke - Stroke
            Stroke which is registered for identifier

        Raises
        ------
            ValueError
                if the identifier is not registered
        """
        if identifier in self.__stroke_id_map:
            return self.strokes[self.__stroke_id_map[identifier]]
        raise ValueError(f'No stroke for identifier:={identifier} registered.')

    @property
    def format_version(self) -> Version:
        """Version of the format. (`Version`, read-only)"""
        return self.__format_version

    @property
    def ink_model(self) -> InkModel:
        """Current state of the ink model. (`InkModel`, read-only)"""
        return self.__ink_model

    @property
    def strokes(self) -> List[Stroke]:
        """List of the parsed strokes. (`List[Stroke]`, read-only)"""
        return self.__strokes

    @property
    def path_point_properties(self) -> List[PathPointProperties]:
        """List of the path point properties. (`List[PathPointProperties]`, read-only)"""
        return self.__path_properties

    def upgrade_uris(self):
        """Upgrade the URIs for groups from UIM 3.0.0 to UIM 3.1.0."""
        uri_view: dict = {}
        for view in self.ink_model.views:
            for ink_node in PreOrderEnumerator(view.root):
                if isinstance(ink_node, StrokeGroupNode):
                    uri_view[ink_node.uri_legacy] = ink_node.uri

        for stmt in self.ink_model.knowledge_graph.statements:
            if stmt.subject in uri_view:
                stmt.subject = uri_view[stmt.subject]
            if stmt.object in uri_view:
                stmt.object = uri_view[stmt.object]

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
import functools
import uuid
from abc import ABC, abstractmethod
from typing import List, Any, Optional
from typing import Tuple
from uim.codec.parser.base import SupportedFormats
from uim.model.base import UUIDIdentifier, InkModelException
from uim.model.inkdata.strokes import Stroke
from uim.model.semantics.structures import BoundingBox
from uim.model.semantics.syntax import CommonViews


class URIBuilder(ABC):
    """
    Generates URIs according to the ink model URI scheme.
    """
    SCHEME: str = "uim:"

    def __init__(self):
        pass

    @staticmethod
    def build_uri(sub_path: str, model_id: uuid.UUID = None):
        """
        Build a URI for a model.

        Parameters
        ----------
        sub_path: str
            Sub path.
        model_id: UUID
            Unique ID of the model.

        Returns
        -------
        uri - `str`
            Model URI
        """
        uri: str = URIBuilder.SCHEME
        if model_id is not None:
            uri += f'{str(model_id)}/'
        uri += f'{sub_path}/'
        return uri

    @staticmethod
    def build_named_entity_uri(uimid: uuid.UUID, model_id: uuid.UUID = None) -> str:
        """Creates a URI for the specified named entity identifier.

        Parameters
        ----------
        uimid: `UUID`
            UUID of a node
        model_id: UUID
            ID of the model [optional]

        Returns
        -------
        uri: str
            URI for a named entity
        """
        if not isinstance(uimid, uuid.UUID):
            raise InkModelException("The named entity identifier should be a valid UUID.")
        return URIBuilder.build_uri('ne', model_id) + str(uimid)

    @staticmethod
    def build_entity_uri(uimid: uuid.UUID, model_id: uuid.UUID = None) -> str:
        """
        Creates a URI for the specified entity view identifier.

        Parameters
        ----------
        uimid: `UUID`
            UUID of a node
        model_id: UUID
            ID of the model [optional]

        Returns
        -------
        uri: str
            URI for an entity
        """
        if not isinstance(uimid, uuid.UUID):
            raise InkModelException("The named entity identifier should be a valid UUID.")
        return URIBuilder.build_uri('', model_id) + str(uimid)

    @staticmethod
    def build_node_uri_from(node_uuid: uuid.UUID, view_name: str,
                            uri_format: SupportedFormats = SupportedFormats.UIM_VERSION_3_1_0) -> str:
        """
        Creates a URI for a node in a view.

        Parameters
        ----------
        node_uuid: `UUID`
            UUID of a node
        view_name: `str`
            Name of the view
        uri_format: `SupportedFormats'
            Target format

        Returns
        -------
        uri: str
            URI for an node within a specific view
        """
        node_uri: str = URIBuilder.build_uri('node')

        if view_name == CommonViews.LEGACY_HWR_VIEW.value:
            node_uri += 'hwr/' if uri_format == SupportedFormats.UIM_VERSION_3_1_0 else ''
        elif view_name == CommonViews.LEGACY_NER_VIEW.value:
            node_uri += 'ner/' if uri_format == SupportedFormats.UIM_VERSION_3_1_0 else ''
        else:
            node_uri += f'{view_name}/'

        node_uri += f'{node_uuid}'
        return node_uri

    @staticmethod
    def build_node_uri(ink_node: 'InkNode', uri_format: SupportedFormats) -> str:
        """
        Creates a URI for an ink node.

        Parameters
        ----------
        ink_node: `InkNode`
            Node in a tree
        uri_format: `SupportedFormats`
            URI format

        Returns
        -------
            uri - `str`
                Build a URI for the ink node
        """
        if isinstance(ink_node, StrokeGroupNode):
            return URIBuilder.build_node_uri_from(ink_node.id, ink_node.view_name, uri_format)
        elif isinstance(ink_node, StrokeNode):
            stroke_node: StrokeNode = ink_node
            node_uri: str = URIBuilder.build_node_uri_from(stroke_node.stroke.id, stroke_node.view_name, uri_format)
            if stroke_node.fragment:
                node_uri += f'#frag={stroke_node.fragment.from_point_index},{stroke_node.fragment.to_point_index}'
            return node_uri


class InkNode(UUIDIdentifier):
    """
c
    Node - the node message. Used for the definition of tree-context.

    The ink tree is built with a generic node structure. For building the tree the depth attribute reflects the
    depth within the tree. For serialization of the tree structure, the depth first pre-order tree serialization is
    applied.

    Each node has an unique identifier id (uri) which is relevant for the semantic statements as an identifier for the
    subject. The groupBoundingBox is optional for `StrokeGroupNode`s and assists with easier visual debugging or
    to highlight the relevant area for clickable options.

    Parameters
    ----------
    node_id: `UUID`
        Node ID as identifier.
    :param group_bounding_box: Rectangle -
        Bounding box (Group nodes only)
    """

    def __init__(self, node_id: uuid.UUID, group_bounding_box: BoundingBox = None):
        super(UUIDIdentifier, self).__init__(node_id)
        self.__id: uuid.UUID = node_id
        self.__group_bounding_box: BoundingBox = group_bounding_box
        self.__parent: Optional[StrokeGroupNode] = None
        self.__tree: 'InkTree' = None
        self.__transient_tag = None

    @property
    def transient_tag(self) -> str:
        """Transient tag of the node. (`str`)"""
        return self.__transient_tag

    @transient_tag.setter
    def transient_tag(self, value):
        self.__transient_tag = value

    @property
    def tree(self) -> 'InkTree':
        """Reference to  the respective `InkTree`. (`InkTree`, read-only)"""
        if self.__tree is None and not self.is_root():
            self.__tree = self.parent.tree
        return self.__tree

    @tree.setter
    def tree(self, value: 'InkTree'):
        self.__tree = value

    @property
    def root(self) -> 'InkNode':
        """Reference to the root node (`InkNode`) of the `InkTree`. (`InkNode`, read-only)"""
        self.__assert_assigned_to_a_tree__()
        return self.__tree.root

    @property
    def parent(self):
        """Reference to the parent node (`InkNode`) of the `InkTree`. (`InkNode`, read-only)"""
        return self.__parent

    def is_root(self) -> bool:
        """
        Check if the node is the root node.
        
        Returns
        -------
        flag: bool
            Flag if the `InkNode` is a root node
        """
        return self.__parent is None

    @property
    def view_name(self) -> str:
        """Name of the associated view. (`str`, read-only)"""
        self.__assert_assigned_to_a_tree__()
        return self.__tree.name

    @property
    def uri(self) -> str:
        """URI according to UIM v3.1.0 specification. (`str`, read-only)"""
        return self.__generate_uri__()

    @property
    def uri_legacy(self) -> str:
        """URI according to UIM v3.0.0 specification. (`str`, read-only)"""
        return f'uim:node/{self.id}'

    @property
    def group_bounding_box(self) -> BoundingBox:
        """Bounding box (`StrokeGroupNode`s only). (`str`)"""
        return self.__group_bounding_box

    @group_bounding_box.setter
    def group_bounding_box(self, bbox: BoundingBox):
        self.__group_bounding_box = bbox

    @abstractmethod
    def __generate_uri__(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def child_nodes_count(self) -> int:
        """"
        Counts the number of child `InkNode`s.
        
        Returns
        -------
        number: int
            Number of child nodes
        """
        pass

    def is_assigned_to_a_tree(self) -> bool:
        """
        Check if the Node is assigned to a tree.
        
        Returns
        -------
        assigned: bool
            Flag if the Node is assigned to a tree
        """
        return self.tree is not None

    def __assert_not_owned__(self):
        """
        Assert that the node is not assigned to tree.
        
        Raises
        ------
        InkModelException
            If `InkNode` already assigned to a tree
        """
        if self.is_assigned_to_a_tree():
            raise InkModelException('Node already assigned to a tree.')
        pass

    def __assert_assigned_to_a_tree__(self):
        """
        Assert that the node is not assigned to a tree.
        
        Raises
        ------
        InkModelException
            If Node not assigned to a tree yet.
        """
        if not self.is_assigned_to_a_tree():
            raise InkModelException("Node not yet assigned to a tree.")

    def __repr__(self):
        return '<Node: [id:={},  uri:={}]>'.format(self.id, self.uri)


class StrokeFragment(ABC):
    """
    StrokeFragment
    ==============
    Denotes a stroke fragment, to reference fragments of the stroke. Fragments can be used for defining semantic
    statements, for instance characters within a word, which requires to assign semantics only on a fragment of
    the stroke.
    
    Parameters
    ----------
    from_point_index: int
        The index of the first path point, which is relevant for this node.
    to_point_index: int
        The index of the last path point, which is relevant for this node.
    from_t_value: int
        The t parameter value of the first point of this node.
    to_t_value: int
        The t parameter value of the last point of this node.
    """

    def __init__(self, from_point_index: int, to_point_index: int, from_t_value: float, to_t_value: float):
        if from_point_index < 0:
            raise ValueError(". The value of from_point_index must be non-negative")

        if to_point_index < from_point_index:
            raise ValueError("The value of to_point_index must be greater or equal to from_point_index")

        if from_t_value < 0. or from_t_value >= 1.:
            raise ValueError("The value of from_t_value must be in the interval [0, 1)")

        if (to_t_value <= from_t_value) or (to_t_value > 1.):
            raise ValueError("The value of to_t_value must be in the interval (fromTValue, 1]")

        self.__from_point_index: int = from_point_index
        self.__to_point_index: int = to_point_index
        self.__from_t_value: float = from_t_value
        self.__to_t_value: float = to_t_value

    @property
    def from_point_index(self) -> int:
        """Gets the index of the first path point of this node. (`int`)"""
        return self.__from_point_index

    @from_point_index.setter
    def from_point_index(self, value: int):
        self.__from_point_index = value

    @property
    def to_point_index(self) -> int:
        """Gets the index of the last path point of this node. (`int`)"""
        return self.__to_point_index

    @to_point_index.setter
    def to_point_index(self, value: int):
        self.__to_point_index = value

    @property
    def from_t_value(self) -> float:
        """Gets the t parameter value of the first point of this node. (`int`)"""
        return self.__from_t_value

    @from_t_value.setter
    def from_t_value(self, value: float):
        self.__from_t_value = value

    @property
    def to_t_value(self) -> float:
        """Gets the t parameter value of the last point of this node. (`int`)"""
        return self.__to_t_value

    @to_t_value.setter
    def to_t_value(self, value: float):
        self.__to_t_value = value


class StrokeNode(InkNode):
    """
    StrokeNode
    ==========
    Represents an ´InkNode´ that refers to a Stroke object.
    A `StrokeNode` can represent either a whole path or part of a path within the ink model.

    Parameters
    ----------
    stroke: `Stroke`
        Stroke which is referenced
    fragment: `StrokeFragment`
        Fragment referencing only parts of the `Stroke`

    Examples
    --------
    >>> from uim.model.ink import InkModel, InkTree
    >>> from uim.model.semantics.node import StrokeGroupNode, StrokeNode, StrokeFragment, URIBuilder
    >>> # Create the model
    >>> ink_model: InkModel = InkModel()
    >>> # Assign the group as the root of the main ink tree
    >>> ink_model.ink_tree = InkTree()
    >>> # First you need a root group to contain the strokes
    >>> root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    >>> ink_model.ink_tree.root = root
    >>>
    >>> # Add a node for stroke 0
    >>> stroke_node_0: StrokeNode = StrokeNode(stroke_0, StrokeFragment(0, 1, 0.0, 1.0))
    >>> root.add(stroke_node_0)
    >>>
    >>> # Add a node for stroke 1
    >>> root.add(StrokeNode(stroke_1, StrokeFragment(0, 1, 0.0, 1.0)))
    """

    def __init__(self, stroke: Stroke, fragment: StrokeFragment = None):
        super().__init__(node_id=stroke.id)
        self.__ref_stroke: Stroke = stroke
        self.__fragment: StrokeFragment = fragment

    @property
    def stroke(self) -> Stroke:
        """References the strokes. (`Stroke`)"""
        return self.__ref_stroke

    @stroke.setter
    def stroke(self, stroke: Stroke):
        self.__ref_stroke = stroke

    @property
    def fragment(self) -> StrokeFragment:
        """`StrokeFragment` that specifies a fragment of the stroke. (`StrokeFragment`)

        Notes
        -----
        If the property value is not null, the stroke node refers to the specified fragment of the stroke.
        """
        return self.__fragment

    @fragment.setter
    def fragment(self, fragment: StrokeFragment):
        self.__fragment = fragment

    def child_nodes_count(self) -> int:
        """
        Number of child nodes.

        Returns
        -------
        num_child_nodes: int
            number of children nodes
        """
        return 0

    def __generate_uri__(self):
        return URIBuilder().build_node_uri(self, SupportedFormats.UIM_VERSION_3_1_0)

    def __repr__(self):
        if self.stroke:
            return '<StrokeNode: [stroke id:={}]>'.format(self.stroke.id if self.stroke is not None else '')


class StrokeGroupNode(InkNode):
    """
    StrokeGroupNode
    ===============
    A non-leaf node, used to group ink-nodes of type `StrokeNode` and/or `StrokeGroupNode`.

    Parameters
    ----------
    uim_id: `UUID`
        Identifier of this stroke node.
    """

    def __init__(self, uim_id: uuid.UUID):
        super().__init__(node_id=uim_id)
        self.__children: List[InkNode] = []

    def add(self, node: InkNode) -> InkNode:
        """
        Adds a child node to this group.

        Parameters
        -----------
        node: `InkNode`
            The child node to be added.

        Raises
        ------
        InkModelException
            If `InkNode` already assigned to a tree or trying to add an ink node as a child, which has already a parent.
        """
        node.__assert_not_owned__()

        if node.parent is not None:
            raise InkModelException(f"Trying to add an ink node as a child, which has already a parent. Node: {node}")

        node._InkNode__parent = self
        self.__children.append(node)

        if node.is_assigned_to_a_tree():
            self.tree.register_sub_tree(node)

        return node

    def child_nodes_count(self) -> int:
        """
        Number of child nodes.

        Returns
        -------
        number_of_child_nodes: `int`
            Number of child nodes
        """
        return len(self.__children)

    def child_group_nodes_count(self) -> int:
        """
        Number of child group nodes.

        Returns
        -------
        number_of_child_nodes: `int`
            Number of child group nodes
        """
        count: int = 0
        if self.child_nodes_count() > 0:
            for n in self.__children:
                count = count + 1 if type(n) == StrokeGroupNode else 0
        return count

    def child_stroke_nodes_count(self) -> int:
        """
        Number of child stroke nodes.

        Returns
        -------
        number_of_child_nodes: `int`
            Number of child stroke group nodes
        """
        count: int = 0
        if self.child_nodes_count() > 0:
            for n in self.__children:
                count = count + 1 if type(n) == StrokeNode else 0
        return count

    def sort_children(self, lambda_sort_func: Any, reverse: bool = False):
        """
        Sorts the children based on a sorting function.

        Parameters
        ----------
        lambda_sort_func: Any
            Sorting function for children.
        reverse: bool
            Flag for reversed order [default:=False]
        """
        self.__children = sorted(self.__children, key=functools.cmp_to_key(lambda_sort_func), reverse=reverse)

    @property
    def children(self) -> Tuple[InkNode]:
        """Children of the node. (`Tuple[InkNode]`, read-only)"""
        return tuple(self.__children)

    def __generate_uri__(self, uri_format: SupportedFormats = SupportedFormats.UIM_VERSION_3_1_0) -> str:
        return URIBuilder().build_node_uri(self, uri_format)

    def __repr__(self):
        return '<StrokeGroupNode: [uri:={}, children:={}]>'.format(self.uri, len(self.children))

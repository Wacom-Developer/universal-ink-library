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
import functools
import logging
import uuid
from abc import ABC, abstractmethod
from typing import List, Any, Optional
from typing import Tuple
from uim.codec.parser.base import SupportedFormats
from uim.model.base import UUIDIdentifier, InkModelException
from uim.model.semantics.structures import BoundingBox
from uim.model.semantics.schema import CommonViews

logger: logging.Logger = logging.getLogger(__name__)


class URIBuilder(ABC):
    """
    URIBuilder
    ==========
    Generates URIs according to the ink model URI scheme.
    """
    SCHEME: str = "uim:"

    def __init__(self):
        pass

    @staticmethod
    def build_uri(sub_path: str, model_id: uuid.UUID = None):
        """
        Creates a URI for the specified sub-path and model identifier.
        Parameters
        ----------
        sub_path: str
            Sub-path
        model_id: UUID [default=None]
            Model identifier [optional]

        Returns
        -------
        uri: str
            URI
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
        uimid: UUID
            UUID of the named entity
        model_id: Optional[UUID] (optional) [default=None]
            ID of the model [optional]

        Returns
        -------
        uri: str
            URI for the named entity with the ink model
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
        uimid: UUID
            UUID of the named entity
        model_id: Optional[UUID] (optional) [default=None]
            ID of the model [optional]

        Returns
        -------
        uri: str
            URI for the entity with the ink model
        """
        if not isinstance(uimid, uuid.UUID):
            raise InkModelException("The named entity identifier should be a valid UUID.")
        return URIBuilder.build_uri('', model_id) + str(uimid)

    @staticmethod
    def build_node_uri_from(node_uuid: uuid.UUID, view_name: str,
                            uri_format: SupportedFormats = SupportedFormats.UIM_VERSION_3_1_0) -> str:
        """
        Build the node URI.

        Parameters
        ----------
        node_uuid: UUID
            Node UUID
        view_name: str
            Name of the view
        uri_format: SupportedFormats (optional) [default=SupportedFormats.UIM_VERSION_3_1_0]
            URI format

        Returns
        -------
        uri: str
            URI for the node
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
    def build_stroke_uri(stroke_uuid: uuid.UUID) -> str:
        """
        Build the stroke URI.

        Parameters
        ----------
        stroke_uuid: UUID
            Stroke UUID

        Returns
        -------
        uri: str
            URI for the stroke
        """
        return f"{URIBuilder.build_uri('stroke')}{str(stroke_uuid)}"

    @staticmethod
    def build_node_uri(ink_node: 'InkNode', uri_format: SupportedFormats) -> str:
        """Creates a URI for an ink node.

        Parameters
        ----------
        ink_node: InkNode
            Node in a tree
        uri_format: SupportedFormats
            URI format

        Returns
        -------
        uri: str
            URI for the node
        """
        if isinstance(ink_node, StrokeGroupNode):
            return URIBuilder.build_node_uri_from(ink_node.id, ink_node.view_name, uri_format)
        if isinstance(ink_node, StrokeNode):
            stroke_node: StrokeNode = ink_node
            node_uri: str = URIBuilder.build_node_uri_from(stroke_node.stroke.id, stroke_node.view_name, uri_format)
            if stroke_node.fragment:
                node_uri += f'#frag={stroke_node.fragment.from_point_index},{stroke_node.fragment.to_point_index}'
            return node_uri
        raise InkModelException(f"Unknown type of InkNode. Type {type(ink_node)} is not supported.")

    @staticmethod
    def build_tree_uri(tree_name: str) -> str:
        """
        Build the tree URI.
        Parameters
        ----------
        tree_name: str
            Name of the tree

        Returns
        -------
        uri: str
            URI for the tree
        """
        return f"uim:tree/{tree_name}"


class InkNode(UUIDIdentifier):
    """
    InkNode
    =======
    Represents a node in the ink tree. The node can be a `StrokeNode` or a `StrokeGroupNode`.

    The ink tree is built with a generic node structure. For building the tree the depth attribute reflects the
    depth within the tree. For serialization of the tree structure, the depth first pre-order tree serialization is
    applied.

    Each node has a unique identifier id (uri) which is relevant for the semantic statements as an identifier for the
    subject. The groupBoundingBox is optional for `StrokeGroupNode`s and assists with easier visual debugging or
    to highlight the relevant area for clickable options.

    Parameters
    ----------
    node_id: `UUID`
        Node ID as identifier.
    group_bounding_box: Optional[BoundingBox] (optional) [default=None]
        Bounding box (Group nodes only)
    """

    def __init__(self, node_id: uuid.UUID, group_bounding_box: Optional[BoundingBox] = None):
        super(UUIDIdentifier, self).__init__(node_id)
        self.__group_bounding_box: BoundingBox = group_bounding_box if group_bounding_box else BoundingBox(x=0, y=0,
                                                                                                           width=0,
                                                                                                           height=0)
        self.__parent: Optional[StrokeGroupNode] = None
        self.__tree: Optional['InkTree'] = None
        self.__transient_tag: Optional[str] = None

    @property
    def transient_tag(self) -> str:
        """Transient tag of the node. (`str`)"""
        return self.__transient_tag

    @transient_tag.setter
    def transient_tag(self, value):
        self.__transient_tag = value

    @property
    def tree(self) -> Optional['InkTree']:
        """Reference to  the respective `InkTree`. (`InkTree`, read-only)"""
        if self.__tree is None and not self.is_root():
            self.__tree = self.parent.tree
        return self.__tree

    @tree.setter
    def tree(self, value: Optional['InkTree']):
        self.__tree = value

    @property
    def root(self) -> 'InkNode':
        """Reference to the root node (`InkNode`) of the `InkTree`. (`InkNode`, read-only)"""
        self.__assert_assigned_to_a_tree__()
        return self.__tree.root

    @property
    def parent(self) -> Optional['StrokeGroupNode']:
        """Reference to the parent node (`StrokeGroupNode`) of the `InkTree`. (`InkNode`)"""
        return self.__parent

    @parent.setter
    def parent(self, value: Optional['StrokeGroupNode']):
        self.__parent = value

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
        """
        Counts the number of child `InkNode`s.
        
        Returns
        -------
        number: int
            Number of child nodes
        """
        raise NotImplementedError()

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

    def __dict__(self):
        return {
            'id': str(self.id),
            'uri': self.uri,
            'groupBoundingBox': self.group_bounding_box.__dict__() if self.group_bounding_box else None
        }

    def __json__(self):
        return self.__dict__()


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
    from_t_value: float
        The t parameter value of the first point of this node.
    to_t_value: float
        The t parameter value of the last point of this node.

    Raises
    ------
    ValueError
        Thrown if the values are negative or out of the defined range.
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

    def __eq__(self, other: Any):
        if not isinstance(other, StrokeFragment):
            logger.warning(f"Comparing StrokeFragment with {type(other)}")
            return False
        if self.from_point_index != other.from_point_index:
            logger.warning(f"StrokeFragment from_point_index is different. {self.from_point_index} != "
                           f"{other.from_point_index}")
            return False
        if self.to_point_index != other.to_point_index:
            logger.warning(f"StrokeFragment to_point_index is different. {self.to_point_index} != "
                           f"{other.to_point_index}")
            return False
        if self.from_t_value != other.from_t_value:
            logger.warning(f"StrokeFragment from_t_value is different. {self.from_t_value} != {other.from_t_value}")
            return False
        if self.to_t_value != other.to_t_value:
            logger.warning(f"StrokeFragment to_t_value is different. {self.to_t_value} != {other.to_t_value}")
            return False
        return True

    def __dict__(self):
        return {
            'from_point_index': self.from_point_index,
            'to_point_index': self.to_point_index,
            'from_t_value': self.from_t_value,
            'to_t_value': self.to_t_value
        }

    def __json__(self):
        return self.__dict__()

    def __repr__(self):
        return f'<StrokeFragment: [from_point_index:={self.from_point_index}, to_point_index:={self.to_point_index}, ' \
               f'from_t_value:={self.from_t_value}, to_t_value:={self.to_t_value}]>'


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
    fragment: Optional[`StrokeFragment`] (optional) [default: None]
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

    def __init__(self, stroke: 'Stroke', fragment: Optional[StrokeFragment] = None):
        super().__init__(node_id=stroke.id)
        self.__ref_stroke: 'Stroke' = stroke
        self.__fragment: StrokeFragment = fragment

    @property
    def stroke(self) -> 'Stroke':
        """References the strokes. (`Stroke`)"""
        return self.__ref_stroke

    @stroke.setter
    def stroke(self, stroke: 'Stroke'):
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

    def __dict__(self):
        return {
            'type': 'StrokeNode',  # 'type' is added to distinguish between StrokeNode and StrokeGroupNode in the JSON
            'id': str(self.id),
            'uri': self.uri,
            'stroke_id': str(self.stroke.id) if self.stroke is not None else None,
            'fragment': self.fragment.__dict__() if self.fragment else None
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, StrokeNode):
            logger.warning(f"Comparing StrokeNode with {type(other)}")
            return False
        if self.stroke != other.stroke:
            logger.warning(f"StrokeNode is different. {self.stroke} != {other.stroke}")
            return False
        if self.fragment != other.fragment:
            logger.warning(f"StrokeNode fragment is different. {self.fragment} != {other.fragment}")
            return False
        return self.id == other.id

    def __repr__(self):
        return f'<StrokeNode: [stroke id:={self.stroke.id}]>'


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

        node.parent = self
        self.__children.append(node)

        if node.is_assigned_to_a_tree():
            self.tree.register_sub_tree(node)

        return node

    def remove(self, node: InkNode):
        """
        Remove child node.

        Parameters
        ----------
        node: `InkNode`
            The child node to be removed.
        """
        self.__children.remove(node)
        node.tree = None
        node.parent = None

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
                count = count + 1 if isinstance(n, StrokeGroupNode) else 0
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
                count += 1 if isinstance(n, StrokeNode) else 0
        return count

    def sort_children(self, lambda_sort_func: Any, reverse: bool = False):
        """
        Sorts the children based on a sorting function.

        Parameters
        ----------
        lambda_sort_func: Any
            Sorting function for children.
        reverse: bool (optional) [default:=False]
            Flag for reversed order [default:=False]
        """
        self.__children = sorted(self.__children, key=functools.cmp_to_key(lambda_sort_func), reverse=reverse)

    @property
    def children(self) -> Tuple[InkNode]:
        """Children of the node. (`Tuple[InkNode]`, read-only)"""
        return tuple(self.__children)

    def __generate_uri__(self, uri_format: SupportedFormats = SupportedFormats.UIM_VERSION_3_1_0) -> str:
        return URIBuilder().build_node_uri(self, uri_format)

    def __dict__(self):
        return {
            'type': 'StrokeGroupNode',
            # 'type' is added to distinguish between StrokeNode and StrokeGroupNode in the JSON
            'id': str(self.id),
            'uri': self.uri,
            'children': [child.__dict__() for child in self.__children]
        }

    def __json__(self):
        return self.__dict__()

    def __eq__(self, other: Any):
        if not isinstance(other, StrokeGroupNode):
            logger.warning(f"Comparing StrokeGroupNode with {type(other)}")
            return False
        return self.id == other.id

    def __repr__(self):
        return f'<StrokeGroupNode: [uri:={self.uri}, children:={len(self.children)}]>'

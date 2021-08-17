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
from typing import List, Optional

from uim.model.semantics.node import InkNode, StrokeGroupNode


class StackItem(object):
    """
    Represents an item in the internal stack of the enumerator.

    Parameters
    ----------
    node - `InkNode`
        Reference to node
    index - `int`
        Index of the group node within its parent.
    """

    def __init__(self, node: InkNode, index: int):
        self.__node: InkNode = node
        self.__index: int = index

    @property
    def node(self) -> InkNode:
        """The element at the current position of the enumerator. (`InkNode`, read-only)"""
        return self.__node

    @property
    def index(self) -> int:
        """Index of the current node within its parent.  (`int`, read-only)"""
        return self.__index

    def __repr__(self):
        return f'<StackItem : [index:={self.index}, node-id:={self.node.id}]>'


class PreOrderEnumerator(object):
    """
    Depth first pre-order traversal of the DOM tree.

    Parameters
    ----------
    node - `InkNode`
        Reference to root node
    """

    def __init__(self, root: InkNode):
        """
        Initializes new instance of the enumerator with the specified parameters.
        :param root: InkNode -
            The node that will be used as a root for the traversal.
        """
        self.__root: InkNode = root
        self.__stack: List[StackItem] = []
        self.__current: Optional[InkNode] = None
        self.__current_index_in_parent: int = 0

    def __iter__(self):
        return self

    def get_depth_level(self) -> int:
        """
        Returns the depth level within the tree.

        Returns
        -------
        depth: int
            Depth within in the resulting tree
        """
        return len(self.__stack)

    def __next__(self):
        """
        Updates the internal state, and update the one in list (current).

        Raises
        -------
        `StopIteration`
            Stops the iteration process
        """
        if self.__current is None:
            self.__current = self.__root  # Will be the root node
            self.__current_index_in_parent = 0
            return self.__current

        current_node: InkNode = self.__current

        if isinstance(current_node, StrokeGroupNode):
            current_group: StrokeGroupNode = current_node

            if (current_group is not None) and (len(current_group.children) > 0):
                self.__stack.append(StackItem(current_group, self.__current_index_in_parent))
                self.__current = current_group.children[0]
                self.__current_index_in_parent = 0
                return self.__current

        while len(self.__stack) > 0:

            # Get the parent group of the current node (from the top of the stack)
            cur_parent: InkNode = self.__stack[-1].node

            # Calculate the index of the next sibling
            sibling_index_in_parent: int = (self.__current_index_in_parent + 1)

            # Return the next sibling of the current node
            if isinstance(cur_parent, StrokeGroupNode) and sibling_index_in_parent < len(cur_parent.children):
                self.__current = cur_parent.children[sibling_index_in_parent]
                self.__current_index_in_parent = sibling_index_in_parent
                return self.__current

            # No next sibling - pop from the stack
            parent: StackItem = self.__stack.pop()
            self.__current = parent.node
            self.__current_index_in_parent = parent.index
        raise StopIteration

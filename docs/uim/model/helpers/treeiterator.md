Module uim.model.helpers.treeiterator
=====================================

Classes
-------

`PreOrderEnumerator(root: uim.model.semantics.node.InkNode)`
:   PreOrderEnumerator
    ==================
    Depth first pre-order traversal of the DOM tree.
    
    Parameters
    ----------
    node - `InkNode`
        The node that will be used as a root for the traversal.

    ### Methods

    `get_depth_level(self) ‑> int`
    :   Returns the depth level within the tree.
        
        Returns
        -------
        depth: int
            Depth within in the resulting tree

`StackItem(node: uim.model.semantics.node.InkNode, index: int)`
:   StackItem
    =========
    Represents an item in the internal stack of the enumerator.
    
    Parameters
    ----------
    node - `InkNode`
        Reference to node
    index - `int`
        Index of the group node within its parent.

    ### Instance variables

    `index: int`
    :   Index of the current node within its parent.  (`int`, read-only)

    `node: uim.model.semantics.node.InkNode`
    :   The element at the current position of the enumerator. (`InkNode`, read-only)
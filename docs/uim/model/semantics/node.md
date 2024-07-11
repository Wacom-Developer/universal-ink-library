Module uim.model.semantics.node
===============================

Classes
-------

`InkNode(node_id: uuid.UUID, group_bounding_box: Optional[uim.model.semantics.structures.BoundingBox] = None)`
:   InkNode
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

    ### Ancestors (in MRO)

    * uim.model.base.UUIDIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Descendants

    * uim.model.semantics.node.StrokeGroupNode
    * uim.model.semantics.node.StrokeNode

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `group_bounding_box: uim.model.semantics.structures.BoundingBox`
    :   Bounding box (`StrokeGroupNode`s only). (`str`)

    `parent: Optional[uim.model.semantics.node.StrokeGroupNode]`
    :   Reference to the parent node (`StrokeGroupNode`) of the `InkTree`. (`InkNode`)

    `root: uim.model.semantics.node.InkNode`
    :   Reference to the root node (`InkNode`) of the `InkTree`. (`InkNode`, read-only)

    `transient_tag: str`
    :   Transient tag of the node. (`str`)

    `tree: Optional[InkTree]`
    :   Reference to  the respective `InkTree`. (`InkTree`, read-only)

    `uri: str`
    :   URI according to UIM v3.1.0 specification. (`str`, read-only)

    `uri_legacy: str`
    :   URI according to UIM v3.0.0 specification. (`str`, read-only)

    `view_name: str`
    :   Name of the associated view. (`str`, read-only)

    ### Methods

    `child_nodes_count(self) ‑> int`
    :   Counts the number of child `InkNode`s.
        
        Returns
        -------
        number: int
            Number of child nodes

    `is_assigned_to_a_tree(self) ‑> bool`
    :   Check if the Node is assigned to a tree.
        
        Returns
        -------
        assigned: bool
            Flag if the Node is assigned to a tree

    `is_root(self) ‑> bool`
    :   Check if the node is the root node.
        
        Returns
        -------
        flag: bool
            Flag if the `InkNode` is a root node

`StrokeFragment(from_point_index: int, to_point_index: int, from_t_value: float, to_t_value: float)`
:   StrokeFragment
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

    ### Ancestors (in MRO)

    * abc.ABC

    ### Instance variables

    `from_point_index: int`
    :   Gets the index of the first path point of this node. (`int`)

    `from_t_value: float`
    :   Gets the t parameter value of the first point of this node. (`int`)

    `to_point_index: int`
    :   Gets the index of the last path point of this node. (`int`)

    `to_t_value: float`
    :   Gets the t parameter value of the last point of this node. (`int`)

`StrokeGroupNode(uim_id: uuid.UUID)`
:   StrokeGroupNode
    ===============
    A non-leaf node, used to group ink-nodes of type `StrokeNode` and/or `StrokeGroupNode`.
    
    Parameters
    ----------
    uim_id: `UUID`
        Identifier of this stroke node.

    ### Ancestors (in MRO)

    * uim.model.semantics.node.InkNode
    * uim.model.base.UUIDIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `children: Tuple[uim.model.semantics.node.InkNode]`
    :   Children of the node. (`Tuple[InkNode]`, read-only)

    ### Methods

    `add(self, node: uim.model.semantics.node.InkNode) ‑> uim.model.semantics.node.InkNode`
    :   Adds a child node to this group.
        
        Parameters
        -----------
        node: `InkNode`
            The child node to be added.
        
        Raises
        ------
        InkModelException
            If `InkNode` already assigned to a tree or trying to add an ink node as a child, which has already a parent.

    `child_group_nodes_count(self) ‑> int`
    :   Number of child group nodes.
        
        Returns
        -------
        number_of_child_nodes: `int`
            Number of child group nodes

    `child_nodes_count(self) ‑> int`
    :   Number of child nodes.
        
        Returns
        -------
        number_of_child_nodes: `int`
            Number of child nodes

    `child_stroke_nodes_count(self) ‑> int`
    :   Number of child stroke nodes.
        
        Returns
        -------
        number_of_child_nodes: `int`
            Number of child stroke group nodes

    `remove(self, node: uim.model.semantics.node.InkNode)`
    :   Remove child node.
        
        Parameters
        ----------
        node: `InkNode`
            The child node to be removed.

    `sort_children(self, lambda_sort_func: Any, reverse: bool = False)`
    :   Sorts the children based on a sorting function.
        
        Parameters
        ----------
        lambda_sort_func: Any
            Sorting function for children.
        reverse: bool (optional) [default:=False]
            Flag for reversed order [default:=False]

`StrokeNode(stroke: Stroke, fragment: Optional[uim.model.semantics.node.StrokeFragment] = None)`
:   StrokeNode
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

    ### Ancestors (in MRO)

    * uim.model.semantics.node.InkNode
    * uim.model.base.UUIDIdentifier
    * uim.model.base.Identifier
    * abc.ABC

    ### Class variables

    `SEPARATOR: str`
    :

    ### Instance variables

    `fragment: uim.model.semantics.node.StrokeFragment`
    :   `StrokeFragment` that specifies a fragment of the stroke. (`StrokeFragment`)
        
        Notes
        -----
        If the property value is not null, the stroke node refers to the specified fragment of the stroke.

    `stroke: Stroke`
    :   References the strokes. (`Stroke`)

    ### Methods

    `child_nodes_count(self) ‑> int`
    :   Number of child nodes.
        
        Returns
        -------
        num_child_nodes: int
            number of children nodes

`URIBuilder()`
:   URIBuilder
    ==========
    Generates URIs according to the ink model URI scheme.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Class variables

    `SCHEME: str`
    :

    ### Static methods

    `build_entity_uri(uimid: uuid.UUID, model_id: uuid.UUID = None) ‑> str`
    :   Creates a URI for the specified entity view identifier.
        
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

    `build_named_entity_uri(uimid: uuid.UUID, model_id: uuid.UUID = None) ‑> str`
    :   Creates a URI for the specified named entity identifier.
        
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

    `build_node_uri(ink_node: InkNode, uri_format: uim.codec.parser.base.SupportedFormats) ‑> str`
    :   Creates a URI for an ink node.
        
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

    `build_node_uri_from(node_uuid: uuid.UUID, view_name: str, uri_format: uim.codec.parser.base.SupportedFormats = SupportedFormats.UIM_VERSION_3_1_0) ‑> str`
    :   Build the node URI.
        
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

    `build_stroke_uri(stroke_uuid: uuid.UUID) ‑> str`
    :   Build the stroke URI.
        
        Parameters
        ----------
        stroke_uuid: UUID
            Stroke UUID
        
        Returns
        -------
        uri: str
            URI for the stroke

    `build_tree_uri(tree_name: str) ‑> str`
    :   Build the tree URI.
        Parameters
        ----------
        tree_name: str
            Name of the tree
        
        Returns
        -------
        uri: str
            URI for the tree

    `build_uri(sub_path: str, model_id: uuid.UUID = None)`
    :   Creates a URI for the specified sub-path and model identifier.
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
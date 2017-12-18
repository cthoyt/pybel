# -*- coding: utf-8 -*-

from ..graph import BELGraph
from ...constants import (
    ABUNDANCE, ACTIVITY, CAUSAL_RELATIONS, DEGRADATION, FRAGMENT, FUNCTION, GENE, GMOD, HGVS, KIND,
    MODIFIER, OBJECT, PATHOLOGY, PMOD, PROTEIN, RELATION, SUBJECT, TRANSLOCATION, VARIANTS,
)
from ...tokens import node_to_tuple

__all__ = [
    'keep_node_permissive',
    'has_protein_modification',
]


def node_predicate(fn):
    """Apply this as a decorator to a function that takes a single argument, a PyBEL node data dictionary, to make
    sure that it can also accept a pair of arguments, a BELGraph and a PyBEL node tuple as well.

    :type fn: types.FunctionType
    :rtype: types.FunctionType
    """

    def wrapped(*args):
        if not args:
            raise ValueError

        x = args[0]

        if isinstance(x, BELGraph):
            return fn(x.node[args[1]], *args[2:])

        if isinstance(x, dict):
            return fn(*args)

        raise ValueError

    return wrapped


def keep_node_permissive(graph, node):
    """A default node filter that always evaluates to :data:`True`.

    Given BEL graph :code:`graph`, applying :func:`keep_node_permissive` with a filter on the nodes iterable
    as in :code:`filter(keep_node_permissive, graph.nodes_iter())` will result in the same iterable as
    :meth:`BELGraph.nodes_iter`

    :param BELGraph graph: A BEL graph
    :param tuple node: The node
    :return: Always returns :data:`True`
    :rtype: bool
    """
    return True


@node_predicate
def is_abundance(data):
    """Returns true if the node is an abundance

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return data[FUNCTION] == ABUNDANCE


@node_predicate
def is_gene(data):
    """Returns true if the node is a gene

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return data[FUNCTION] == GENE


@node_predicate
def is_protein(data):
    """Returns true if the node is a protein

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return data[FUNCTION] == PROTEIN


@node_predicate
def is_pathology(data):
    """Returns true if the node is a pathology

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return data[FUNCTION] == PATHOLOGY


@node_predicate
def not_pathology(data):
    """Returns false if the node is a pathology

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return data[FUNCTION] != PATHOLOGY


@node_predicate
def has_variant(data):
    """Returns true if the node has any variants

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return VARIANTS in data


def _node_has_variant(data, variant):
    """Checks if a node has at least one of the given variant

    :param dict data: A PyBEL data dictionary
    :param str variant: :data:`PMOD`, :data:`HGVS`, :data:`GMOD`, or :data:`FRAGMENT`
    :rtype: bool
    """
    return VARIANTS in data and any(
        variant_dict[KIND] == variant
        for variant_dict in data[VARIANTS]
    )


@node_predicate
def has_protein_modification(data):
    """Returns true if the node has a protein modification variant

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return _node_has_variant(data, PMOD)


@node_predicate
def has_gene_modification(data):
    """Checks if a node has a gene modification

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return _node_has_variant(data, GMOD)


@node_predicate
def has_hgvs(data):
    """Checks if a node has an HGVS variant

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return _node_has_variant(data, HGVS)


@node_predicate
def has_fragment(data):
    """Checks if a node has a fragment

    :param dict data: A PyBEL data dictionary
    :rtype: bool
    """
    return _node_has_variant(data, FRAGMENT)


def _node_has_modifier(graph, node, modifier):
    """Returns true if over any of a nodes edges, it has a given modifier - :data:`pybel.constants.ACTIVITY`,
     :data:`pybel.constants.DEGRADATION`, or :data:`pybel.constants.TRANSLOCATION`.

    :param pybel.BELGraph graph: A BEL graph
    :param tuple node: A BEL node
    :param str modifier: One of :data:`pybel.constants.ACTIVITY`, :data:`pybel.constants.DEGRADATION`, or
                        :data:`pybel.constants.TRANSLOCATION`
    :return: If the node has a known modifier
    :rtype: bool
    """
    for _, _, d in graph.in_edges_iter(node, data=True):
        if OBJECT in d and MODIFIER in d[OBJECT] and d[OBJECT][MODIFIER] == modifier:
            return True

    for _, _, d in graph.out_edges_iter(node, data=True):
        if SUBJECT in d and MODIFIER in d[SUBJECT] and d[SUBJECT][MODIFIER] == modifier:
            return True

    return False


def has_activity(graph, node):
    """Returns true if over any of the node's edges it has a molecular activity

    :param pybel.BELGraph graph: A BEL graph
    :param tuple node: A BEL node
    :return: If the node has a known molecular activity
    :rtype: bool
    """
    return _node_has_modifier(graph, node, ACTIVITY)


def is_degraded(graph, node):
    """Returns true if over any of the node's edges it is degraded

    :param pybel.BELGraph graph: A BEL graph
    :param tuple node: A BEL node
    :return: If the node has a known degradation
    :rtype: bool
    """
    return _node_has_modifier(graph, node, DEGRADATION)


def is_translocated(graph, node):
    """Returns true if over any of the node's edges it is transloated

    :param pybel.BELGraph graph: A BEL graph
    :param tuple node: A BEL node
    :return: If the node has a known translocation
    :rtype: bool
    """
    return _node_has_modifier(graph, node, TRANSLOCATION)


def has_causal_in_edges(graph, node):
    """Returns true if the node contains any in_edges that are causal

    :param pybel.BELGraph graph: A BEL graph
    :param tuple node: A BEL node
    :rtype: bool
    """
    return any(
        data[RELATION] in CAUSAL_RELATIONS
        for _, _, data in graph.in_edges_iter(node, data=True)
    )


def has_causal_out_edges(graph, node):
    """Returns true if the node contains any out_edges that are causal

    :param pybel.BELGraph graph: A BEL graph
    :param tuple node: A BEL node
    :rtype: bool
    """
    return any(
        data[RELATION] in CAUSAL_RELATIONS
        for _, _, data in graph.out_edges_iter(node, data=True)
    )


def node_exclusion_filter_builder(nodes):
    """Builds a function that returns true

    :param nodes: A list of PyBEL node data dictionaries or PyBEL node tuples
    :rtype: types.FunctionType
    """
    nodes = {
        node_to_tuple(node) if isinstance(node, dict) else node
        for node in nodes
    }

    @node_predicate
    def node_exclusion_filter(data):
        """Returns true if the node is not in the given set of nodes

        :param dict data: A PyBEL data dictionary
        :rtype: bool
        """
        return node_to_tuple(data) not in nodes

    return node_exclusion_filter

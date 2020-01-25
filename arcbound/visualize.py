""" Visualizes arcbound graphs.

Requires graphviz.
"""

from typing import Dict, Set

import attr

try:
    import graphviz
except ImportError:
    pass

from .arc import arc
from .requires import requires


@requires("graphviz")
@attr.s(auto_attribs=True)
class Digraph(object):
    """ Creates a digraph from an input dictionary mapping dependencies to
    nodes.
    """
    deps_by_node: Dict[str, Set[str]]

    ############################################################################
    # Set up the nodes and edges.
    ############################################################################

    @property
    @arc(deps_by_node="deps_by_node")
    def nodes(self, deps_by_node: Dict[str, Set[str]]) -> Set[str]:
        """ Returns the nodes in the graph.
        """
        return (
            set(deps_by_node)
            | {node for nodes in deps_by_node.values() for node in nodes}
        )

    @property
    @arc(deps_by_node="deps_by_node")
    def edges(self, deps_by_node: Dict[str, Set[str]]) -> Set[str]:
        """ Returns the edges in the graph.
        """
        return {
            f"{node}{dep}"
            for node, deps in deps_by_node.items()
            for dep in deps
        }

    ############################################################################
    # Draw the graph. 
    ############################################################################

    @property
    def blank_graph(
        self,
        graph_name="test",
        filename="test",
        node_attr=None,
        file_format=""
    ) -> graphviz.Digraph:
        """ Returns an instantiated graphviz Digraph object.
        """
        return graphviz.Digraph()

    @property
    @arc(dag="blank_graph", deps_by_node="deps_by_node")
    def graph(
        self,
        dag: graphviz.Digraph,
        deps_by_node: Dict[str, Set[str]]
    ) -> graphviz.Digraph:
        """ Returns a graphviz Digraph object with the nodes and edges defined
        in the arcbound graph. 
        """
        for node in deps_by_node:
            dag.node(name=node, label=node) 

        for node, deps in deps_by_node.items():
            for dep in deps:
                dag.edge(dep, node)

        return dag


""" Visualizes arcbound graphs.

Requires graphviz.
"""

from typing import Dict, Set

import attr

try:
    import graphviz
except ImportError:
    pass

from .arc import arcs, auto_arcs
from .requires import requires


@requires("graphviz")
@attr.s(auto_attribs=True)
class Digraph(object):
    """ Creates a digraph from an input dictionary mapping dependencies to
    nodes.
    """
    deps_by_node: Dict[str, Set[str]]
    filename: str = "arcbound_digraph"
    file_format: str = "png"
    digraph_kwargs: dict = attr.Factory(dict)

    ###########################################################################
    # Set up the nodes and edges.
    ###########################################################################

    @property
    @auto_arcs()
    def nodes(self, deps_by_node: Dict[str, Set[str]]) -> Set[str]:
        """ Returns the nodes in the graph.
        """
        return (
            set(deps_by_node)
            | {node for nodes in deps_by_node.values() for node in nodes}
        )

    @property
    @auto_arcs()
    def edges(self, deps_by_node: Dict[str, Set[str]]) -> Set[str]:
        """ Returns the edges in the graph.
        """
        return {
            f"{node}{dep}"
            for node, deps in deps_by_node.items()
            for dep in deps
        }

    ###########################################################################
    # Draw the graph.
    ###########################################################################

    @property
    @auto_arcs()
    def blank_graph(
        self,
        graph_name: str = "test",
        filename: str = "test",
        file_format: str = "png",
        digraph_kwargs: dict = None
    ) -> graphviz.Digraph:
        """ Returns an instantiated graphviz Digraph object.

        Args:
            graph_name: Graph name used in the source code.
            filename: Filename to save the output to.
            file_format: How to render the output format.
            digraph_kwargs (dict): Additional kwargs to pass to the Digraph
                instantiation.
        """
        return graphviz.Digraph(
            name=graph_name,
            filename=filename,
            format=file_format,
            **digraph_kwargs
        )

    @property
    @arcs(dag="blank_graph", deps_by_node="deps_by_node")
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

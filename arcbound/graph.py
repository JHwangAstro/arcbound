""" The graph function wraps an input class, adding properties accessing methods
decorated with arcbound.arc.
"""

import functools
import inspect
from typing import Callable, Dict, List, Tuple, Type, TypeVar

from .arc import arc
from .visualize import Digraph

ClassType = TypeVar("ClassType")
ArcboundGraph = TypeVar("ArcboundGraph", bound="ArcboundGraph")

def create_arcbound_graph(cls: ClassType) -> ArcboundGraph:
    """ Returns an ArcboundGraph object created using an input class.

    The ArcboundGraph object contains properties summarizing the attributes of
    the class decorated with arcbound.arc and a method for returning underlying
    functions generating the properties and methods.

    Args:
        cls: Class to graph methods and properties decorated with arcbound.arc.
    """
    class ArcboundGraph(object):
        """
        Properties:
            class_attrs: List of attribute names belonging to the input class.
            properties: Dictionary mapping methods decorated with both
                property and arcbound.arc to the property name.
            methods: Dictionary mapping methods decorated with arcbound.arc.
            nodes: Dictionary combining the properties and methods dictionaries.
            arcs: Dictionary mapping dependencies of methods decorated with
                arcbound.arc.
            
        Methods:
            get_node: Returns as a curried function the decorated method with
                the instance variable already set.
        """
        @property
        @functools.lru_cache()
        def class_attrs(self) -> List[str]:
            """ Returns a list of attribute names belonging to the input class.
            """
            return dir(cls)

        @property
        @arc(functions_list="class_attrs")
        def properties(self, functions_list: List[str]) -> Dict[str, Callable]:
            """ Returns a dictionary mapping property names to the method
            defining the property for methods decorated with arcbound.arc.
            """
            return {
                function_name: method.fget
                for function_name in functions_list 
                for method in [getattr(cls, function_name)]
                if isinstance(method, property)
                if hasattr(method.fget, "arc")
            }
        
        @property
        @arc(functions_list="class_attrs")
        def methods(self, functions_list: List[str]) -> Dict[str, Callable]:
            """ Returns a dictionary mapping method names and methods for
            methods decorated with arcbound.arc.
            """
            return {
                function_name: method
                for function_name in functions_list 
                for method in [getattr(cls, function_name)]
                if hasattr(method, "arc")
            }
        
        @property
        @arc(d1="properties", d2="methods")
        def nodes(
            self,
            d1: Dict[str, Callable],
            d2: Dict[str, Callable]
        ) -> Dict[str, Callable]:
            """ Combines the properties and methods into a single dictionary.
            """
            return {**d1, **d2}

        @property
        @arc(nodes="nodes")
        def arcs(self, nodes: Dict[str, Callable]) -> Dict[str, Tuple[str]]:
            """ Returns a dictionary mapping dependencies by method/property.
            """
            return {
                name: {dep for dep in method.arc}
                for name, method in nodes.items()
            }
        
        @arc(nodes="nodes")
        def get_node(self, k: str, nodes: Dict[str, Callable]) -> Callable:
            """ Returns the function defining the method or property.
            """
            def default_f(cls, *args, **kwargs) -> None:
                """ Dummy function returning None and indicating if the
                requested method is defined and/or decorated.
                """
                if k in dir(cls):
                    print("This method is not decorated.")
                else:
                    print("This method does not exist.")

                return None

            return nodes.get(k, default_f)

    return ArcboundGraph


def graph(cls: ClassType) -> Callable[[ClassType], ClassType]:
    """ Returns a class with properties and functions leveraging methods
    decorated with the arcbound.arc function.

    Args:
        cls: Class to be decorated.

    Example:
        import arcbound as ab 

    	@ab.graph
        class test():
            def __init__(self, root_val: int) -> None:
                self.root = root_val
                return None

            @property
            @ab.arc(x="root")
            def branch(self, x: int) -> int:
                return x * x 

            @ab.arc(x="branch", y="branch")
            def leaf(self, x: int, y: int) -> int:
                return x * y

            def twig(self, x: int, y: int) -> int:
                return x * y

        Test = test(5)

        Test.arcbound_graph.methods
        # {'leaf': <function __main__.test.leaf(self, x:int, y:int) -> int>}

        Test.arcbound_graph.properties
        # {'branch': <function __main__.test.branch(self, x:int) -> int>}

        Test.arcbound_graph.nodes
        # {'branch': <function __main__.test.branch(self, x:int) -> int>,
        #  'leaf': <function __main__.test.leaf(self, x:int, y:int) -> int>}

        Test.get_arcbound_node("branch")(10)
        # 100

        Test.get_arcbound_node("leaf")(2, 3)
        # 6

        Test.get_arcbound_node("twig")(2, 3)
        # This method is not decorated.
        
        Test.get_arcbound_node("nest")(10)
        # This method does not exist.
    """
    class wrapper_class(cls):
        """ Returns a class with properties and functions leveraging methods
        decorated with the arcbound.arc function.

        Attributes:
            arcbound_graph: Returns an ArcboundGraph summarizing the input
                class's decorated methods.
            
        Functions:
            get_arcbound_node: Returns a curried function with the class's self
                provided as the class instance.
        """
        @property
        def arcbound_graph(self) -> ArcboundGraph:
            """ Returns an ArcboundGraph object used to summarize and interact
            with attributes decorated with arcbound.arc.
            """
            return create_arcbound_graph(cls)()
        
        @arc(arcbound_graph="arcbound_graph")
        def get_arcbound_node(
            self,
            k: str,
            arcbound_graph: ArcboundGraph 
        ) -> Callable:
            """ Returns the function defining the method or property with the
            instance variable already assigned.
            """
            f = arcbound_graph.get_node(k)

            return functools.partial(f, self)

        @arc(graph="arcbound_graph")
        def create_arcbound_graph(
            self,
            graph: ArcboundGraph,
            filename: str = "arcbound_graph.png",
            file_format: str = "png",
            **digraph_kwargs
        ) -> Digraph:
            """ Returns a graphviz-generated DiGraph made of the decorated
            methods.
            """
            return Digraph(
                deps_by_node=graph.arcs,
                filename=filename,
                file_format=file_format,
                digraph_kwargs=digraph_kwargs
            ).graph

        def render_arcbound_graph(
            self,
            filename: str = "arcbound_graph.png",
            file_format: str = "png",
            directory: str = "./",
            **digraph_kwargs
        ) -> str:
            """ Save the graph. Returns the path to the saved file.
            """
            graph = self.create_arcbound_graph(
                filename=filename,
                file_format=file_format,
                **digraph_kwargs
            )

            return graph.render(filename=filename, directory=directory)

    return wrapper_class


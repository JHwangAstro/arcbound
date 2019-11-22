""" The graph function wraps an input class, adding properties accessing methods
decorated with arcbound.arc.
"""

import functools
import inspect
from typing import Callable, Dict, Type, TypeVar

from .arc import arc

T = TypeVar("T")

def graph(cls: T) -> T:
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
    """
    class wrapper_class(cls) -> T:
        """ Returns a class with properties and functions leveraging methods
        decorated with the arcbound.arc function.

        Attributes:
            arcbound_properties:
            arcbound_methods:
            arcbound_nodes:
            
        Functions:
            get_arcbound_node:
        """
        @property
        def arcbound_properties(self) -> Dict[str, Callable]:
            """ Returns a dictionary mapping property names to the method
            defining the property for methods decorated with arcbound.arc.
            """
            return {
                function_name: method.fget
                for function_name in dir(cls)
                for method in [getattr(cls, function_name)]
                if isinstance(method, property)
                if hasattr(method.fget, "arc")
            }
        
        @property
        def arcbound_methods(self) -> Dict[str, Callable]:
            """ Returns a dictionary mapping method names and methods for
            methods decorated with arcbound.arc.
            """
            return {
                function_name: method
                for function_name in dir(cls)
                for method in [getattr(cls, function_name)]
                if (hasattr(method, "arc") & inspect.ismethod(method))
            }
        
        @property
        @arc(d1="arcbound_properties", d2="arcbound_methods")
        def arcbound_nodes(
            self,
            d1: Dict[str, Callable],
            d2: Dict[str, Callable]
        ) -> Dict[str, Callable]:
            """ Combines the arcbound_properties and arcbound_methods into a
            single dictionary.
            """
            return {
                **self.arcbound_properties,
                **self.arcbound_methods
            }
        
        @arc(nodes="arcbound_nodes")
        def get_arcbound_node(
            self,
            k: str,
            nodes: Dict[str, Callable]
        ) -> Callable:
            """ Returns the function defining the method or property with the
            instance variable already assigned.
            """
            def default_f(self, *args, **kwargs) -> None:
                """ Dummy function returning None and indicating if the
                requested method is defined and/or decorated.
                """
                if k in dir(cls):
                    print("This method is not decorated.")
                else:
                    print("This method does not exist.")

                return None

            return functools.partial(nodes.get(k, default_f), self)
        
    return wrapper_class


""" The arc function wraps an input function to have default inputs set to
other attributes within the class and sets an attribute to the input function
documenting this dependency.
"""

import functools
import inspect
from typing import Callable, TypeVar

ReturnType = TypeVar("ReturnType")
FuncType = Callable[..., ReturnType]

def arc(**attribute_kwargs) -> Callable[[FuncType], FuncType]:
    """ Returns a function that sets instance attributes as default values.

    This decorator enables methods within a class to be constructed into a
    directed acyclic graph. Adds a 'deps' attribute to the returned function
    containing a dictionary defining the attributes to set as default values.

    Args:
        **attribute_kwargs: keyword to attribute values to set as defaults in
            the input function.

    Example:
        import arcbound as ab 

        class Test():
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

        test = Test(5)
        test.branch # 25
        test.leaf() # 625
        test.leaf(x=10) # 250
        test.leaf(x=10, y=10) #100
    """
    def wrapper_factory(f: FuncType) -> FuncType:
        """ Returns a function with default values set to the object's
        attributes and adds the deps attribute to the wrapper function.

        Args:
            f: Function to decorate.
        """
        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> ReturnType:
            """ Returns the results of the input function with default values
            set by the attribute kwargs.

            Assumes that the first argument is the object-reference variable.
            """
            # Assign arguments without a keyword to the appropriate keywords.
            self, *non_self_args = args
            self_kw, *func_kws = inspect.getfullargspec(f).args

            arg_kwargs = {k: v for k, v in zip(func_kws, non_self_args)}

            instantiated_attribute_kwargs = {
                k: getattr(self, attr)
                for k, attr in attribute_kwargs.items()
            }

            combined_kwargs = {
                **instantiated_attribute_kwargs,
                **kwargs,
                **arg_kwargs
            }
            
            return f(self, **combined_kwargs)

        wrapper.arc = tuple(attribute_kwargs.values())
        
        return wrapper
    
    return wrapper_factory 


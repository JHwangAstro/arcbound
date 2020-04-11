""" The requires decorator checks if a package is available and raises an error
or sends a warning otherwise.
"""

import functools
import importlib.util
from typing import Callable, TypeVar, Union
import warnings

ClassType = TypeVar("ClassType")


def requires(
    package: str,
    message: str = None,
    warn_only: bool = False,
) -> Callable[[ClassType], ClassType]:
    """ Returns the input object with an added check that the input package
    is installed at instantiation.

    Args:
        package: Name of package to check for.
        message: Message to print out if package is not installed.
        warn_only: Flag determining if import errors should be downgraded to
            a warning.
    """
    def wrapper_factory(
        obj: Union[ClassType, Callable]
    ) -> Union[ClassType, Callable]:
        """ Returns the input class with an added check that a specified package
        is installed at instantiation.

        Args:
            obj: Class or function to be modified with a package check.
        """
        if callable(obj):
            @functools.wraps(obj)
            def obj_with_requires(*args, **kwargs):
                """ Adds a package check before executing the function.
                """
                library_loaded = importlib.util.find_spec(package)

                if (not library_loaded) & (not warn_only):
                    default_error = f"{obj.__name__} requires {package}."
                    raise ImportError(message or default_error)

                elif (not library_loaded):
                    default_warning = f"{package} not installed, proceeding."

                    warnings.warn(message or default_warning, ImportWarning)

                return obj(*args, **kwargs)

        else:
            class obj_with_requires(obj):
                """ Adds a package check to the __init__ method of the parent
                class.
                """
                __doc__ = obj.__doc__

                def __init__(self, *args, **kwargs):
                    """ First checks if the specified package is installed then
                    proceeds with the parent's initialization.

                    Raises:
                        ImportError: The required package is not found.
                    """
                    library_loaded = importlib.util.find_spec(package)

                    if (not library_loaded) & (not warn_only):
                        default_error = f"{obj.__name__} requires {package}."
                        raise ImportError(message or default_error)

                    elif (not library_loaded):
                        default_warning = f"""
                            {package} not installed, proceeding.
                            """

                        warnings.warn(
                            message or default_warning,
                            ImportWarning
                        )

                    super().__init__(*args, **kwargs)

        return obj_with_requires

    return wrapper_factory

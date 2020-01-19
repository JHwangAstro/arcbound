"""
"""

import functools
import importlib.util
from typing import Callable, TypeVar
import warnings

ClassType = TypeVar("ClassType")
RequiresType = Callable[..., ClassType]

def requires(
    package: str,
    message: str = None,
    warn_only: bool = False,
) -> RequiresType:
    """ Returns a function checking if the requested package is installed.

    Args:
        package: Name of package to check for.
        message: Message to print out if package is not installed.
        warn_only: Flag determining if import errors should be downgraded to
            a warning.
    """
    def check_package(cls: ClassType) -> ClassType:
        """ Returns a function checking if the requested package is installed.
        Raises an import error if the requested package is not installed,
        otherwise returns the class.
        """
        library_loaded = importlib.util.find_spec(package)

        if (not library_loaded) & (not warn_only):
            default_error = f"{cls.__name__} requires {package}"

            raise ImportError(message or default_error)

        elif (not library_loaded):
            default_warning = f"{package} not installed, proceeding anyways."
            warnings.warn(message or default_warning, ImportWarning)

        return cls

    return check_package


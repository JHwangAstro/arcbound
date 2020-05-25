""" The arc function wraps an input function to have default inputs set to
other attributes within the class and sets an attribute to the input function
documenting this dependency.
"""

import functools
import inspect
from typing import Any, Callable, Dict, Tuple, TypeVar, Union

import attr

ReturnType = TypeVar("ReturnType")
ClassType = TypeVar("ClassType")
FuncType = Callable[..., ReturnType]


@attr.s(auto_attribs=True, hash=False)
class Arc(object):
    """ Sets options on how an arc should be created.

    input_parameters:
        name: Name of the attribute to set as default.
        conditional: Function taking a class instance as an input, determining
            if the attribute should be set. The default function returns True.
        transform: Function that transforms the linked attribute before
            input to the decorated method.
        converter: Previous argument name for the transform input. Will be
            deprecated in the future.
        silent: Determines if the arc is documented.
        tag_only: Determines if the arc should be used only for documentation;
            will not set the default to the attribute if set to True.
    """
    name: str
    conditional: Callable[..., bool] = attr.Factory(lambda: lambda x: True)
    transform: Callable[..., Any] = attr.Factory(lambda: lambda x: x)
    converter: Callable[..., Any] = None
    silent: bool = False
    tag_only: bool = False

    def valid(self, cls: ClassType) -> bool:
        """ Determines if the default value should be assigned to the arc.
        """
        return self.conditional(cls)

    def value(self, cls: ClassType) -> Any:
        """ Return the value to be assigned as the default value in the
        function. If the converter argument is set, return the output of the
        function applied to the attribute.
        """
        initial_value = getattr(cls, self.name)

        if self.converter is None:
            value = self.transform(initial_value)

        else:
            print("Change converter to transform; will be deprecated.")
            value = self.converter(initial_value)

        return value


def arcs(
    auto_arcs: bool = False,
    silent_arcs: bool = False,
    arc_generator: Callable[..., Dict[str, Union[str, Arc]]] = None,
    arc_tags: Tuple[str] = (),
    extra_attribute_kwargs: dict = None,
    **attribute_kwargs
) -> Callable[[FuncType], FuncType]:
    """ Returns a function that sets instance attributes as default values.

    This decorator enables methods within a class to be constructed into a
    directed acyclic graph. Adds a 'deps' attribute to the returned function
    containing a dictionary defining the attributes to set as default values.

    Args:
        auto_arcs: Determines if arcs should automatically be created from all
            keywords in the input function.
        silent_arcs: Determines if the arcs are documented.
        arc_generator: Function defining arcs at runtime from the instance.
        arc_tags: Arcs to document without affecting the input function.
        extra_attribute_kwargs: Dictionary explicitly mapping keyword to
            attribute values to set as defaults in the input function to avoid
            potential namespace collisions.
        **attribute_kwargs: Keyword to attribute values to set as defaults in
            the input function.

    Example:
        import arcbound as ab

        class Test():
            def __init__(self, root_val: int) -> None:
                self.root = root_val
                return None

            @property
            @ab.arcs(x="root")
            def branch(self, x: int) -> int:
                return x * x

            @ab.arcs(x="branch", y="branch")
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

        Assumes that the first argument is the object-reference variable.

        If auto_arcs is true, attempts to set all arguments in the function
        with a default as the identically named attribute in the instance.

        Args:
            f: Function to decorate.
        """
        self_kw, *func_kws = inspect.getfullargspec(f).args

        # Combines the kwargs provided with an explicit dictionary argument
        # to avoid potential namespace collisions.
        initial_attribute_kwargs = dict(
            **attribute_kwargs,
            **(extra_attribute_kwargs or {})
        )

        assert all(
            isinstance(attribute, str) or isinstance(attribute, Arc)
            for attribute in initial_attribute_kwargs.values()
        ), "All arc definitions should either be a string or Arc object."

        @functools.wraps(f)
        def wrapper(*args, **kwargs) -> ReturnType:
            """ Returns the results of the input function with default values
            set by the attribute kwargs.
            """
            # Assign arguments without a keyword to the appropriate keywords.
            self, *non_self_args = args
            unused_kws = (k for k in func_kws if k not in kwargs)
            arg_kwargs = {k: v for k, v in zip(unused_kws, non_self_args)}

            # Generate attribute kwargs.
            generated_attribute_kwargs = (
                {} if arc_generator is None else
                arc_generator(self)
            )

            # Combines the kwargs provided with an explicit dictionary argument
            # to avoid potential namespace collisions.
            all_attribute_kwargs = dict(
                **initial_attribute_kwargs,
                **generated_attribute_kwargs,
            )

            # If auto_arcs is set to true, auto_kwargs maps the each argument
            # to the identically named attribute if it exists.
            if auto_arcs:
                available_attributes = set(dir(self))

                auto_kwargs = {
                    k: getattr(self, k)
                    for k in func_kws
                    if k not in all_attribute_kwargs
                    if k in available_attributes
                }

            else:
                auto_kwargs = {}

            unpacked_attribute_kwargs = {
                k: (
                    getattr(self, attribute) if isinstance(attribute, str) else
                    attribute.value(self)
                )
                for k, attribute in all_attribute_kwargs.items()
                if (
                    isinstance(attribute, str)
                    or (attribute.valid(self) & (not attribute.tag_only))
                )
            }

            combined_kwargs = {
                **auto_kwargs,
                **unpacked_attribute_kwargs,
                **kwargs,
                **arg_kwargs
            }

            return f(self, **combined_kwargs)

        if silent_arcs:
            tagged_arcs = ()

        else:
            # Set edges even if conditionals were not met.
            if auto_arcs:
                auto_arc_tags = tuple(
                    k
                    for k in func_kws
                    if k not in initial_attribute_kwargs
                )

            else:
                auto_arc_tags = ()

            unpacked_arc_tags = tuple(
                attribute if isinstance(attribute, str) else
                attribute.name
                for k, attribute in initial_attribute_kwargs.items()
                if isinstance(attribute, str) or (not attribute.silent)
            )

            tagged_arcs = tuple(
                auto_arc_tags + unpacked_arc_tags + arc_tags
            )

        wrapper.arcs = tagged_arcs

        return wrapper

    return wrapper_factory


def arc(**attribute_kwargs) -> Callable[[FuncType], FuncType]:
    """ Placeholder for arcs. Will be deprecated on release.
    """
    return arcs(**attribute_kwargs)


def auto_arcs() -> Callable[[FuncType], FuncType]:
    """ Syntactical sugar for arcs(auto_arcs=True).
    """
    return arcs(auto_arcs=True)

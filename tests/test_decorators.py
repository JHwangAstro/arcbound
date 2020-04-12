""" Unit tests for the arc decorator.
"""

import unittest

import math
from typing import Callable, Tuple, Union

import arcbound as ab
import attr


@ab.graph
@attr.s(auto_attribs=True)
class QuadraticSolver(object):
    """ Calculates the solutions to a given quadratic equation.

    Input parameters:
        a: Quadratic coefficient.
        b: Linear coefficient.
        c: Constant.
    """
    a: float = 0.
    b: float = 0.
    c: float = 0.

    # Here we explicitly define the coefficient arcs.
    @property
    @ab.arcs(a="a", b="b", c="c")
    def discriminant(self, a: float, b: float, c: float) -> float:
        """ Discriminant of the quadratic equation; used to determine the
        number of roots and if they are rational.
        """
        return b * b - 4 * a * c

    # Here we use the auto_arcs decorator to automatically link to the
    # property of the same name.
    @property
    @ab.auto_arcs()
    def roots(
        self,
        a: float,
        b: float,
        discriminant: float
    ) -> Tuple[Union[float, complex], ...]:
        """ Returns the root(s) of the equation.
        """
        if discriminant == 0:
            roots = (-b / (2 * a),)

        elif discriminant > 0:
            roots = (
                (-b + math.sqrt(discriminant)) / (2 * a),
                (-b - math.sqrt(discriminant)) / (2 * a),
            )

        else:
            real = -b / (2 * a)
            imag = math.sqrt(-discriminant) / (2 * a)
            roots = (
                complex(real, imag),
                complex(real, -imag)
            )

        return roots

    # Transform the linked property prior to entering the method.
    @property
    @ab.arcs(
        roots=ab.Arc(
            "roots",
            transform=lambda roots: tuple(
                root if isinstance(root, complex) else
                complex(root, 0.)
                for root in roots
            )
        )
    )
    def complex_roots(
        self,
        roots: Tuple[Union[float, complex], ...]
    ) -> Tuple[complex, ...]:
        """ Standardizes the types to complex.
        """
        return roots

    # Since this property is not decorated with an arcbound decorator, a node
    # is not generated on the arcbound_graph.
    @property
    def number_of_roots(self) -> int:
        """ Returns the number of roots.
        """
        discriminant = self.discriminant

        return (
            1 if discriminant == 0. else
            2
        )


class TestArc(unittest.TestCase):
    """ Unit test for the arc and graph decorators.
    """
    @property
    def test_class(self):
        """ Instantiated test class.
        """
        return QuadraticSolver(a=1, b=4, c=3)

    @ab.auto_arcs()
    def test_default_argument(self, test_class: QuadraticSolver):
        """ Tests specified attribute is passed to the method as a default
        argument.
        """
        self.assertEqual(test_class.discriminant, 4)

    @ab.auto_arcs()
    def test_nested_default_arguments(self, test_class: QuadraticSolver):
        """ Tests specified attributes are passed to the method as default
        arguments and nested decorated methods work as expected.

        Also tests the auto_arcs decorator works as expected.
        """
        self.assertEqual(test_class.roots, (-1.0, -3.0))

    @ab.auto_arcs()
    def test_transform(self, test_class: QuadraticSolver):
        """ Tests specified attributes are passed to the method as default
        arguments and nested decorated methods work as expected.

        Also tests the auto_arcs decorator works as expected.
        """
        self.assertEqual(
            test_class.complex_roots,
            (complex(-1.0, 0.), complex(-3.0, 0.))
        )

    @property
    @ab.auto_arcs()
    def method_node(self, test_class: QuadraticSolver) -> Callable:
        """ Retrieve a node from the arcbound_graph.
        """
        return test_class.get_arcbound_node("discriminant")

    @ab.auto_arcs()
    def test_node_no_defaults(self, method_node: Callable):
        """ Tests retrieved function behaves as expected with all arguments
        passed in.
        """
        self.assertEqual(method_node(a=2, b=4, c=-2), 32)

    @ab.auto_arcs()
    def test_get_node_with_defaults(self, method_node: Callable):
        """ Tests retrieved function behaves as expected with default values
        for keywords not specified.
        """
        self.assertEqual(method_node(), 4)


if __name__ == "__main__":
    unittest.main()

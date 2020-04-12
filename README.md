# Arcbound 
> Collection of tools to arrange bound methods into a graph.

Arcbound contains a series of decorators to aid data-driven programming, where
the methods and properties of a class are abstracted as nodes on a graph,
inter-connected by arcs (directed edges).

## Installation
```bash
pip install arcbound
```

## Usage example
```python
import math
from typing import Tuple, Union

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


quad_solver = QuadraticSolver(a=1, b=4, c=3)

quad_solver.roots
# (-1,0, -3.0)

# Create a function that solves for the discriminant of a quadratic equation.
# Retains the defaults of a=1, b=4, and c=3 from the quad_solver object.
discriminant_solver = quad_solver.get_arcbound_node("discriminant")
discriminant_solver(a=2, b=4)
# -8

quad_solver.visualize_arcbound_graph()
```
![arcbound_graph](https://github.com/JHwangAstro/arcbound/blob/master/utils/arcbound_graph.png "ArcboundGraph")


# Arcbound 
> Collection of tools to arrange bound methods into a graph.

Arcbound contains a series of decorators to aid data-driven programming, where
the methods and properties of a class are abstracted as nodes on a graph,
inter-connected by arcs (directed edges).

## Installation

## Usage example
```python
import arcbound as ab

@ab.graph
class Example():
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
    
    @ab.arc(x="branch", y="leaf")
    def catepillar(self, x: int, y: int) -> int:
        return x * y
    
    def twig(self, x: int, y: int) -> int:
        return x * y

example = Example(5)

example.get_arcbound_node("catepillar")(y=-2)
# -50

example.visualize_arcbound_graph()
```
![arcbound_graph](https://github.com/JHwangAstro/arcbound/blob/master/utils/arcbound_graph.png "ArcboundGraph")


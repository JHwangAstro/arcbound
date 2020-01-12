""" Unit tests for the arc decorator.
"""

import unittest

import arcbound as ab 


@ab.graph
class Test():
    """ Test class used for unit testing the graph and arc decorators.
    """
    def __init__(self, root_val: int) -> None:
        self.root = root_val
        return None

    @property
    @ab.arc(x="root")
    def branch(self, x: int) -> int:
        return x * x 

    @property
    @ab.arc(x="branch", y="branch")
    def leaf(self, x: int, y: int) -> int:
        return x * y


class TestArc(unittest.TestCase):
    """ Unit test for the arc and graph decorators.
    """
    @property
    def test_class(self):
        """ Instantiated test class.
        """
        return Test(5)

    def test_default_argument(self):
        """ Tests specified attribute is passed to the method as a default
        argument.
        """
        test_class = self.test_class
        self.assertEqual(test_class.branch, 25)

    def test_nested_default_arguments(self):
        """ Tests specified attributes are passed to the method as default
        arguments and nested decorated methods work as expected.
        """
        test_class = self.test_class
        self.assertEqual(test_class.leaf, 625)

    def test_get_node_no_defaults(self):
        """ Tests retrieved function behaves as expected with all arguments
        passed in.
        """
        test_class = self.test_class
        self.assertEqual(test_class.get_arcbound_node("leaf")(x=10, y=10), 100)

    def test_get_node_with_defaults(self):
        """ Tests retrieved function behaves as expected with default values
        for keywords not specified.
        """
        test_class = self.test_class
        self.assertEqual(test_class.get_arcbound_node("leaf")(x=10), 250)


if __name__ == "__main__":
    unittest.main()


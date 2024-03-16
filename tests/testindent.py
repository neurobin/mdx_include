"""This file is used to test the strip_indent feature"""


class Example:
    """
    Defines an Example object

    This docstring should be sliced from this file and the four leading spaces should be stripped from each line
    """

    attribute1 = None

    def __init__(self, attr1):
        self.attribute1 = attr1

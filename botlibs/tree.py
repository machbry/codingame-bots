class Tree:
    def __init__(self, value):
        self._value = value
        self._children = []

    @property
    def value(self):
        return self._value

    @property
    def children(self):
        return self._children

    def add_child(self, child):
        self._children.append(child)

class Tree:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children
        if self.children is None:
            self.children = []

    def add_child(self, child):
        self.children.append(child)
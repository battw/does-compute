from utils import Vec

class Model():
    def __init__(self):
        self._cellar = Cellar()
        print("init model")

    def update(self, dt):
        pass# print("update model")

    def place_node(self, position, orientation):
        cell = self._cellar.get_cell(position)
        try:
            cell.add_node(Node(position, orientation))
        except Exception:
            return
        print("place node (pos={}, orient={})".format(position, orientation))

    def delete_nodes_at(self, position):
        print("delete nodes (pos={})".format(position))

    def invert_nodes_at(self, position):
        print("invert nodes (pos={})".format(position))

    def get_all_objects():
        print("get objects")

class Node():
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = orientation
        self.is_inverted = False

    def invert(self):
        self.is_inverted = not self.is_inverted

class Signal():
    def __init__(self, position, orientation, node):
        self.start = position
        self.end = position
        self.orientation = orientation
        self.node = node

class Cell():
    def __init__(self):
        self.node_list = list()
        self.signal_list = list()

    def add_node(self, node):
        """Add node if there is no other node with the same orientation."""
        if not any([node.orientation == other.orientation for other in self.node_list]):
            self.node_list.append(node)
        else:
            raise Exception("Failed to add node.")

    def add_signal(self, signal):
        pass

class Cellar():
    def __init__(self):
        self.cell_dict = dict()

    def get_cell(self, position):
        if position in self.cell_dict.keys():
            return self.cell_dict[position]
        new_cell = Cell()
        self.cell_dict[position] = new_cell
        return new_cell
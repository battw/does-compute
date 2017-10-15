from utils import Vec

class Model():
    def __init__(self):
        self.cellar = Cellar()
        self.living_signal_list = list()
        self.decaying_signal_list = list()
        print("init model")

    def update(self, dt):
        for signal in self.living_signal_list:
            signal.extend()
        for signal in self.decaying_signal_list:
            signal.decay()

    def place_node(self, position, orientation):
        self.cellar.add_node(Node(position, orientation, self.cellar))
        print("place node (pos=({}), orient=({}))".format(position, orientation))

    def delete_nodes_at(self, position):
        self.cellar.delete_nodes(position)
        for signal in self.cellar.get_signals(position):
            if signal.start_position == position:
                self.living_signal_list.remove(signal)
                self.decaying_signal_list.append(signal)
            elif signal.end_position == position:
                self.living_signal_list.append(signal)
        print("delete nodes (pos={})".format(position))

    def invert_nodes_at(self, position):
        for node in self.cellar.get_nodes(position):
            node.invert()
            if node.signal:
                self.living_signal_list.remove(node.signal)
                self.decaying_signal_list.append(node.signal)
                node.signal = None
            else:
                node.signal = Signal(position, node.orientation, node, self.cellar)
                self.add_signal(node.signal)
        print("invert nodes (pos={})".format(position))

    def add_signal(self, signal):
        self.cellar.add_signal(signal, signal.start_position)
        self.living_signal_list.append(signal)


    def items(self):
        return self.cellar.items()
        print("get objects")

class Node():
    def __init__(self, position, orientation, cellar):
        self.cellar = cellar
        self.position = position
        self.orientation = orientation
        self.is_inverted = False
        self.signal = None

    def invert(self):
        self.is_inverted = not self.is_inverted


class Signal():
    def __init__(self, position, orientation, node, cellar):
        self.start_position= position
        self.end_position = position
        self.orientation = orientation
        self.node = node
        self.cellar = cellar


    def extend(self):
        next_position = self.end_position + self.orientation
        self.end_position = next_position
        self.cellar.add_signal(self, next_position)

    def decay(self):
        print("decay")


class Cell():
    def __init__(self, position):
        self.node_list = list()
        self.signal_list = list()
        self.position = position

    def add_node(self, node):
        self.node_list.append(node)

    def has_node_with_orientation(self, orientation):
        return any([orientation == other.orientation for other in self.node_list])

    def add_signal(self, signal):
        self.signal_list.append(signal)

    def invert_nodes(self):
        for node in self.node_list:
            node.invert()

    def delete_nodes(self):
        self.node_list = list()


    def delete_signals(self):
        self.signal_list = list()

    def is_recieving_signal(self):
        for signal in self.signal_list:
            if signal.start_position!= self.position:
                return True
        return False

    def is_empty(self):
        return not (self.node_list or self.signal_list)

class Cellar():
    def __init__(self):
        self._cell_dict = dict()

    def add_node(self, node):
        cell = self._get_cell(node.position)
        cell.add_node(node)

    def delete_nodes(self, position):
        cell = self._get_cell(position)
        cell.delete_nodes()
        self._remove_cell_if_empty(position)

    def get_nodes(self, position):
        cell = self._get_cell(position)
        self._remove_cell_if_empty(position)
        return iter(cell.node_list)

    def add_signal(self, signal, position):
        cell = self._get_cell(position)
        cell.add_signal(signal)

    def delete_signals(self, position):
        cell = self._get_cell(position)
        cell.delete_signals(position)
        self._remove_cell_if_empty(position)

    def get_signals(self, position):
        cell = self._get_cell(position)
        self._remove_cell_if_empty(position)
        return iter(cell.signal_list)

    def items(self):
        return self._cell_dict.items()

    def _get_cell(self, position):
        if position not in self._cell_dict.keys():
            self._cell_dict[position] = Cell(position)
        return self._cell_dict[position]

    def _remove_cell_if_empty(self, position):
        cell = self._get_cell(position)
        if cell.is_empty():
            del self._cell_dict[position]

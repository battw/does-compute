from utils import Vec

class Model():
    def __init__(self):
        self.cellar = Cellar()
        self.living_signal_list = list()
        self.decaying_signal_list = list()
        print("init model")

    def update(self, dt):
        self.update_living_signals()
        self.update_decaying_signals()

    def update_living_signals(self):
        for signal in self.living_signal_list:
            signal.extend()
            nodes = self.cellar.get_nodes(signal.end_position)
            if nodes:
                self.living_signal_list.remove(signal)
            for node in nodes:
                if not node.signal and not node.is_inverted:
                    self.add_signal(node)
                elif node.signal and node.is_inverted:
                    self._kill_signal(node.signal)

    def update_decaying_signals(self):
        WHEN SIGNAL DECAYS UNTIL IT REACHES another node the input to that node isn't sorted out
        for signal in self.decaying_signal_list:
            signal.decay()
            if signal.start_position == signal.end_position + signal.orientation:
                self.decaying_signal_list.remove(signal)


    def place_node(self, position, orientation):
        self.cellar.add_node(Node(position, orientation, self.cellar))
        print("place node (pos=({}), orient=({}))".format(position, orientation))

    def delete_nodes_at(self, position):
        self.cellar.delete_nodes(position)
        for signal in self.cellar.get_signals(position):
            if signal.start_position == position and signal in self.living_signal_list:
                self._kill_signal(signal)
            elif signal.end_position == position:
                self.living_signal_list.append(signal)
        print("delete nodes (pos={})".format(position))

    def invert_nodes_at(self, position):
        for node in self.cellar.get_nodes(position):
            node.invert()
            if node.signal:
                self._kill_signal(node.signal)
            else:
                self.add_signal(node)
        print("invert nodes (pos={})".format(position))

    def add_signal(self, node):
        signal = Signal(node, self.cellar)
        self.living_signal_list.append(signal)


    def _kill_signal(self, signal):
        if signal in self.living_signal_list:
            self.living_signal_list.remove(signal)
        if signal not in self.decaying_signal_list:
            self.decaying_signal_list.append(signal)
            signal.decay() #This keeps the timing the same as for living signals.



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
    def __init__(self, node, cellar):
        self.start_position = node.position
        self.end_position = node.position
        self.orientation = node.orientation
        self.node = node
        node.signal = self
        self.cellar = cellar
        cellar.add_signal(self, self.start_position)


    def extend(self):
        next_position = self.end_position + self.orientation
        self.end_position = next_position
        self.cellar.add_signal(self, next_position)

    def decay(self):
        if self.node:
            self.node.signal = None
            self.node = None
        self.cellar.delete_signal(self, self.start_position)
        self.start_position += self.orientation
        print("decay")


class Cell():
    def __init__(self, position):
        self.node_list = list()
        self.signal_list = list()
        self.position = position

    def add_node(self, node):
        for other in self.node_list:
            if node.orientation == other.orientation:
                return
        self.node_list.append(node)

    def has_node_with_orientation(self, orientation):
        return any([orientation == other.orientation for other in self.node_list])

    def add_signal(self, signal):
        self.signal_list.append(signal)

    def invert_nodes(self):
        for node in self.node_list:
            node.invert()

    def delete_nodes(self):
        self.node_list.clear()

    def delete_signals(self):
        self.signal_list.clear()

    def delete_signal(self, signal):
        assert signal in self.signal_list

        if signal in self.signal_list:
            self.signal_list.remove(signal)

    def is_recieving_signal(self):
        for signal in self.signal_list:
            if signal.start_position != self.position:
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
        return list(cell.node_list)

    def add_signal(self, signal, position):
        cell = self._get_cell(position)
        cell.add_signal(signal)

    def delete_signals(self, position):
        cell = self._get_cell(position)
        cell.delete_signals(position)
        self._remove_cell_if_empty(position)

    def delete_signal(self, signal, position):
        cell = self._get_cell(position)
        cell.delete_signal(signal)
        self._remove_cell_if_empty(position)

    def get_signals(self, position):
        cell = self._get_cell(position)
        self._remove_cell_if_empty(position)
        return list(cell.signal_list)

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

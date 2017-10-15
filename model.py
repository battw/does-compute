from utils import Vec

class Model():
    def __init__(self):
        self.cell_dict = dict()
        self.living_signal_list = list()
        self.decaying_signal_list = list()
        print("init model")

    def update(self, dt):
        for signal in self.living_signal_list:
            signal.extend()
        for signal in self.decaying_signal_list:
            signal.decay()

    def place_node(self, position, orientation):
        if position not in self.cell_dict.keys():
            self.cell_dict[position] = Cell(position)
        self.cell_dict[position].add_node(Node(position, orientation, self))
        print("place node (pos=({}), orient=({}))".format(position, orientation))

    def delete_nodes_at(self, position):
        if position in self.cell_dict.keys():
            cell = self.cell_dict[position]
            cell.node_list = list()
            for signal in cell.signal_list:
                if signal.start_postion == position:
                    self.decaying_signal_list.append(signal)
                elif signal.end_position == position:
                    self.living_signal_list.append(signal)
                else:
                    raise Exception("Not implemented signal splitting")
            del self.cell_dict[position]

        print("delete nodes (pos={})".format(position))

    def invert_nodes_at(self, position):
        if position in self.cell_dict.keys():
            for node in self.cell_dict[position].node_list:
                node.invert()
                if node.signal:
                    self.decaying_signal_list.append(node.signal)
                else:
                    node.signal = Signal(position, node.orientation, node, self)
                    self.living_signal_list.append(node.signal)
        print("invert nodes (pos={})".format(position))

    def add_signal(self, signal):
        assert self.cell_dict[signal.position]
        cell = self.cell_dict[position]
        cell.signal_list.append(signal)
        self.live_signal_list.append(signal)


    def items(self):
        return self.cell_dict.items()
        print("get objects")

class Node():
    def __init__(self, position, orientation, model):
        self.model = model
        self.position = position
        self.orientation = orientation
        self.is_inverted = False
        self.signal = None

    def invert(self):
        self.is_inverted = not self.is_inverted

    def emit_signal(self):
        assert not self.signal
        self.signal = Signal(self.position, self.orientation, model)
        self.model.add_signal(signal)

class Signal():
    def __init__(self, position, orientation, node, model):
        self.start_position= position
        self.end_position = position
        self.orientation = orientation
        self.node = node
        self.model = model


    def extend(self):
        next_position = self.end_position + self.orientation
        if next_position in self.model.cell_dict.keys():
            cell = self.model.cell_dict[next_position]
        else:
            cell = Cell(next_position)
            self.model.cell_dict[next_position] = cell
        cell.signal_list.append(self)
        self.end_position = next_position

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
        pass

    def invert_nodes(self):
        for node in self.node_list:
            node.invert()

    def delete_nodes(self):
        self.node_list = list()

    def is_recieving_signal(self):
        for signal in self.signal_list:
            if signal.start_position!= self.position:
                return True
        return False

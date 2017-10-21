from utils import Vec

class Model():
    def __init__(self):
        self._cellar = Cellar()
        print("init model")

    def update(self, dt):
        print("len(cellar) == {}".format(len(self._cellar)))
        for signal in list(self._cellar.updating_signal_list):
            signal.update()

    def place_node(self, position, orientation):
        self._cellar.add_node(Node(position, orientation, self._cellar))
        print("place node (pos=({}), orient=({}))".format(position, orientation))

    def delete_nodes(self, position):
        self._cellar.delete_nodes(position)

    def invert_nodes(self, position):
        for node in self._cellar.get_nodes(position):
            node.invert()

    def items(self):
        return self._cellar.items()
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
        self.update()

    def update(self):
        signals = self.cellar.get_signals(self.position)
        signals = [s for s in signals if s.start_position != self.position]
        if signals:
            if self.is_inverted:
                self._decay_signal()
            else:
                self._emit()
        else:
            if self.is_inverted:
                self._emit()
            else:
                self._decay_signal()
        for signal in signals:
            if signal.end_position != self.position:
                signal.split(self.position)

    def _emit(self):
        if not self.signal:
            self.signal = Signal(self)
            self.signal.start_growing()


    def _decay_signal(self):
        if self.signal:
            self.signal.start_decaying()
            self.signal = None

    def kill(self):
        self._decay_signal()





class Signal():
    def __init__(self, node):
        self.start_position = node.position
        self.end_position = node.position
        self.orientation = node.orientation
        self.node = node
        node.signal = self
        self._cellar = node.cellar
        self._cellar.add_signal(self, self.start_position)
        self._is_growing = False
        self._is_decaying = False
        self._path_list = [self.start_position]


    def update(self):
        if self._is_growing:
            self._grow()
        if self._is_decaying:
            self._decay()
        if (not(self._is_growing or self._is_decaying)
        and self in self._cellar.updating_signal_list):
            self._cellar.updating_signal_list.remove(self)
        if (self.end_position.x > self._cellar.bounds.x
        or self.end_position.y > self._cellar.bounds.y
        or self.end_position.x < 0
        or self.end_position.y < 0):
            self.stop_growing()



    def _grow(self):
        self.end_position += self.orientation
        self._cellar.add_signal(self, self.end_position)
        self._path_list.append(self.end_position)
        nodes = self._cellar.get_nodes(self.end_position)
        if nodes:
            self.stop_growing()
            for node in nodes:
                node.update()

    def _decay(self):
        self._cellar.delete_signal(self, self.start_position)
        self._path_list.remove(self.start_position)
        for node in self._cellar.get_nodes(self.start_position):
            node.update()
        if self.start_position == self.end_position:
            self.die()
            self.stop_growing()
            self.stop_decaying()
        else:
            self.start_position += self.orientation

    def start_growing(self):
        self._is_growing = True
        self._cellar.add_to_updating_signals(self)

    def stop_growing(self):
        self._is_growing = False

    def stop_decaying(self):
        self._is_decaying = False

    def start_decaying(self):
        self.node = None
        self._is_decaying = True
        self._cellar.add_to_updating_signals(self)

    def die(self):
        self.stop_growing()
        self.stop_decaying()
        if self in self._cellar.updating_signal_list:
            self._cellar.updating_signal_list.remove(self)
        if self.node:
            self.node.signal = None

    def split(self, position):
        assert position in self._path_list
        if position not in self._path_list:
            return

        tail_signal = Signal(Node(position, self.orientation, self._cellar))
        split_index = self._path_list.index(position)
        tail_signal._path_list = self._path_list[split_index + 1:]
        self._path_list = self._path_list[:split_index + 1]
        self.end_position = position
        self.stop_growing()

        tail_signal.end_position = tail_signal._path_list[-1]

        for position in tail_signal._path_list:
            self._cellar.delete_signal(self, position)
            self._cellar.add_signal(tail_signal, position)

        tail_signal.start_decaying()




        # self.end_position = position
        #Signal()




class Cell():
    def __init__(self, position):
        self.node_list = list()
        self.signal_set = set()
        self.position = position

    def add_node(self, node):
        for other in self.node_list:
            if node.orientation == other.orientation:
                return
        self.node_list.append(node)
        node.update()

    def has_node_with_orientation(self, orientation):
        return any([orientation == other.orientation for other in self.node_list])

    def add_signal(self, signal):
        self.signal_set.add(signal)

    def invert_nodes(self):
        for node in self.node_list:
            node.invert()

    def delete_nodes(self):
        for node in self.node_list:
            node.kill()
        self.node_list.clear()

    def delete_signals(self):
        self.signal_set.clear()

    def delete_signal(self, signal):
        assert signal in self.signal_set
        self.signal_set.discard(signal)

    def is_recieving_signal(self):
        for signal in self.signal_set:
            if signal.start_position != self.position:
                return True
        return False

    def is_empty(self):
        return not (self.node_list or self.signal_set)

class Cellar():
    def __init__(self):
        self.updating_signal_list = list() # All signals that require a call to update on each tick.
        self.bounds = Vec(50, 50)
        self._cell_dict = dict()

    def add_node(self, node):
        cell = self._get_cell(node.position)
        cell.add_node(node)

    def delete_nodes(self, position):
        cell = self._get_cell(position)
        cell.delete_nodes()
        for signal in cell.signal_set:
            signal.start_growing()
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
        return list(cell.signal_set)

    def add_to_updating_signals(self, signal):
        if signal not in self.updating_signal_list:
            self.updating_signal_list.insert(0, signal)

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

    def __len__(self):
        return len(self._cell_dict)

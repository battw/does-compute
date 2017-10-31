from utils import Vec

class Model():
    def __init__(self):
        self._cellar = _Cellar()

    def update(self, dt):
        self._cellar.update()

    def place_node(self, position, orientation):
        self._cellar.add_node(position, orientation)

    def delete_nodes(self, position):
        self._cellar.delete_nodes(position)

    def invert_nodes(self, position):
        self._cellar.invert_nodes(position)

    def items(self):
        return self._cellar.items()


class _Cellar():
    class _Node():
        def __init__(self, position, orientation):
            self.position = position
            self.orientation = orientation
            self.is_inverted = False

        def output(self, cellar):
            '''Returns an output signal if approriate, None otherwise.'''
            if (self.position in cellar._signal_dict.keys() and not self.is_inverted
                or
                self.position not in cellar._signal_dict.keys() and self.is_inverted):
                return _Cellar._Signal(self.position + self.orientation, self.orientation)


    class _Signal():
        def __init__(self, position, orientation):
            self.position = position
            self.orientation = orientation

        def output(self, cellar):
            '''Returns a new Signal representing the forward movement of this
            Signal, or None if this signal terminates.'''
            if self.position not in cellar._node_dict.keys():
                return _Cellar._Signal(self.position + self.orientation, self.orientation)

    def __init__(self):
        self._signal_dict = dict()
        self._node_dict = dict()
        self._bounds = Vec(100, 100)

    def update(self):
        new_signal_dict = dict()
        for items in list(self._signal_dict.values()) + list(self._node_dict.values()):
            for item in items:
                output_signal = item.output(self)
                if output_signal and not self.is_out_of_bounds(output_signal.position):
                    if output_signal.position not in new_signal_dict.keys():
                        new_signal_dict[output_signal.position] = list()
                    new_signal_dict[output_signal.position].append(output_signal)

        self._signal_dict = new_signal_dict
        # print(len(self._signal_dict.keys()))

    def is_out_of_bounds(self, vec):
        return vec.x > self._bounds.x or vec.y > self._bounds.y or vec.x < 0 or vec.y < 0


    def add_node(self, position, orientation):
        '''Adds a node if there isn't currently one with the same position and
        orientation.'''
        node = _Cellar._Node(position, orientation)
        if position not in self._node_dict.keys():
            self._node_dict[position] = list()
        if self._have_different_orientations(node, self._node_dict[position]):
            self._node_dict[position].append(node)

    def delete_nodes(self, position):
        if position in self._node_dict.keys():
            del self._node_dict[position]

    def invert_nodes(self, position):
        if position in self._node_dict.keys():
            for node in self._node_dict[position]:
                node.is_inverted = not node.is_inverted

    def items(self):
        return list(self._signal_dict.items()) + list(self._node_dict.items())

    def _have_different_orientations(self, item, items):
        orientations = [i.orientation for i in items]
        return item.orientation not in orientations

from utils import Vec

class Model():
    def __init__(self):
        self._cellar = _Cellar()
        self._copied_nodes = None

    def update(self, dt):
        self._cellar.update()

    def place_node(self, position, orientation):
        orientation = orientation.normalise(1.4)
        self._cellar.add_node(position, orientation)

    def delete_nodes(self, a_position, b_position=None):
        """Deletes the nodes at a_position or if b_position is defined the nodes
        in the square defined by the two positions"""
        if b_position == None:
            self._cellar.delete_nodes(a_position)
        else:
            bottom_left_corner, top_right_corner = self._get_corners(a_position,
                                                                     b_position)
            for x in range(bottom_left_corner.x, top_right_corner.x + 1):
                for y in range(bottom_left_corner.y, top_right_corner.y + 1):
                    self._cellar.delete_nodes(Vec(x,y))


    def _get_corners(self, a_position, b_position):
        """Taking the square defined by the input positions, returns the
        bottom left corner and the top left corner as a tuple"""
        bottom_left_corner = Vec(min(a_position.x, b_position.x),
                                 min(a_position.y, b_position.y))
        top_right_corner = Vec(max(a_position.x, b_position.x),
                               max(a_position.y, b_position.y))
        return bottom_left_corner, top_right_corner

    def invert_nodes(self, position):
        self._cellar.invert_nodes(position)

    def items(self):
        return self._cellar.items()

    def clear_signals(self):
        self._cellar.clear_signals()

    def copy_nodes(self, corner1, corner2):
        bottom_left_corner, top_right_corner = self._get_corners(corner1,
                                                                 corner2)
        self._copied_nodes = self._cellar.copy_nodes(bottom_left_corner,
                                                     top_right_corner)

    def paste_nodes(self, bottom_left_position):
        self._cellar.paste_nodes(bottom_left_position, self._copied_nodes)

    def save_as(self, name):
        pass



class _Cellar():
    class _Node():
        def __init__(self, position, orientation, is_inverted=False):
            self.position = position
            self.orientation = orientation
            self.is_inverted = is_inverted

        def output(self, cellar):
            '''Returns an output signal if approriate, None otherwise.'''
            if (self.position in cellar._signal_dict.keys() and
                not self.is_inverted
                or
                self.position not in cellar._signal_dict.keys() and
                self.is_inverted):
                return _Cellar._Signal(self.position + self.orientation,
                                       self.orientation)

        def __str__(self):
            return "position = {}\norientation = {}".format(self.position,
                                                            self.orientation)


    class _Signal():
        def __init__(self, position, orientation):
            self.position = position
            self.orientation = orientation

        def output(self, cellar):
            '''Returns a new Signal representing the forward movement of this
            Signal, or None if this signal terminates.'''
            if self.position not in cellar._node_dict.keys():
                return _Cellar._Signal(self.position + self.orientation,
                                       self.orientation)

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


    def add_node(self, position, orientation, is_inverted=False):
        '''Adds a node if there isn't currently one with the same position and
        orientation.'''
        node = _Cellar._Node(position, orientation, is_inverted)
        if position not in self._node_dict.keys():
            self._node_dict[position] = list()
        if self._have_different_orientations(node, self._node_dict[position]):
            self._node_dict[position].append(node)

    def delete_nodes(self, position):
        if position in self._node_dict.keys():
            del self._node_dict[position]

    def copy_nodes(self, bottom_left_vec, top_right_vec):
        def is_included(position):
            (x,y) = position
            return (bottom_left_vec.x <= x <= top_right_vec.x
                    and bottom_left_vec.y <= y <= top_right_vec.y)
        filtered_items = filter(lambda item: is_included(item[0]), self._node_dict.items())
        translated_items = [(pos - bottom_left_vec, nodes) for (pos, nodes) in filtered_items]
        return dict(translated_items)

    def paste_nodes(self, bottom_left_position, node_dict):
        for (pos, node_list) in node_dict.items():
            for node in node_list:
                self.add_node(pos + bottom_left_position, node.orientation,
                              is_inverted=node.is_inverted)

    def invert_nodes(self, position):
        if position in self._node_dict.keys():
            for node in self._node_dict[position]:
                node.is_inverted = not node.is_inverted

    def items(self):
        return list(self._signal_dict.items()) + list(self._node_dict.items())

    def _have_different_orientations(self, item, items):
        orientations = [i.orientation for i in items]
        return item.orientation not in orientations

    def clear_signals(self):
        self._signal_dict = dict()

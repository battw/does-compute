import pyglet
from pyglet.gl import GL_POINTS, GL_TRIANGLES, GL_LINES
from math import sqrt
import itertools

class GameWindow(pyglet.window.Window):

    def __init__(self):
        super(GameWindow, self).__init__()
        self.cell_size = 20
        self.mouse_cell_index = Vec(-1,-1)
        self.noder = Noder()
        self.signaller = Signaller(self.noder)
        pyglet.clock.schedule_interval(self.update, 1)
        # self.set_mouse_visible(False)
        self.is_currently_placing_node = False

    def on_draw(self):
        self.clear()
        self.draw_mouse_cell()
        self.draw_nodes()
        self.draw_signals()
        if self.is_currently_placing_node:
            self.draw_triangle(self.ghost_node.index, self.ghost_node.facing)

    def cell_location(self, cell_index):
        return Vec(cell_index.x * self.cell_size + self.cell_size // 2
        , cell_index.y * self.cell_size + self.cell_size // 2)

    def draw_mouse_cell(self):
        # self.draw_triangle(self.mouse_cell_index, 0)
        self.draw_point(self.mouse_cell_index)

    def draw_point(self, cell_index):
        cell_location = self.cell_location(cell_index)
        pyglet.graphics.draw(1, GL_POINTS, ('v2i', cell_location.to_tuple()))

    def draw_triangle(self, cell_index, facing):
        position = self.cell_location(cell_index)
        length = self.cell_size // 2 - self.cell_size // 3
        width = self.cell_size // 2 - self.cell_size // 5
        len_vec = facing.normalise(length)
        wid_vec = Vec(facing.y, -facing.x).normalise(width)
        point = position + len_vec
        left_corner = position - len_vec - wid_vec
        right_corner = position - len_vec + wid_vec
        triangle_vertices = (*left_corner, *right_corner, *point)
        pyglet.graphics.draw(3, GL_TRIANGLES, ('v2i', triangle_vertices))

    def draw_nodes(self):
        for node in self.noder.get_all_nodes():
            self.draw_triangle(node.index, node.facing)

    def draw_signals(self):
        for signal in self.signaller.get_all_signals():
            start = self.cell_location(signal.start)
            end = self.cell_location(signal.head)
            pyglet.graphics.draw(2, GL_LINES, ('v2i', (*start, *end)))

    def point_ghost_node_towards_mouse(self):
        diff = self.mouse_cell_index - self.ghost_node.index
        if diff.magnitude() > 0:
            self.ghost_node.facing = diff.normalise()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_cell_index = Vec(x // self.cell_size, y // self.cell_size)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            self.ghost_node =  Noder.Node(self.mouse_cell_index)
            self.is_currently_placing_node = True
        elif button == 4:
            # self.signaller.add_signal(self.mouse_cell_index)
            self.noder.invert_nodes_at(self.mouse_cell_index)



    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse_cell_index = Vec(x // self.cell_size, y // self.cell_size)
        if self.is_currently_placing_node:
            self.point_ghost_node_towards_mouse()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == 1:
            self.is_currently_placing_node = False
            self.noder.add_node(self.ghost_node.index, self.ghost_node.facing)

    def update(self, dt):
        self.signaller.update()

class Vec():
    def __init__(self, x, y):
        self.x = int(round(x))
        self.y = int(round(y))

    def __str__(self):
        return "x={}, y={}".format(self.x, self.y)

    def __add__(self, vec):
        return Vec(self.x + vec.x, self.y + vec.y)

    def __sub__(self, vec):
        return Vec(self.x - vec.x, self.y - vec.y)

    def __mul__(self, val):
        return Vec(self.x * val, self.y * val)

    def magnitude(self):
        return sqrt(self.x**2 + self.y**2)

    def normalise(self, magnitude=1):
        assert self.magnitude != 0
        return Vec(self.x * magnitude / self.magnitude(), self.y * magnitude / self.magnitude())

    def to_tuple(self):
        return (self.x, self.y)

    def __iter__(self):
        self._iter_index = -1
        return self

    def __next__(self):
        self._iter_index += 1
        if self._iter_index == 0:
            return self.x
        elif self._iter_index == 1:
            return self.y
        raise StopIteration

    def __hash__(self):
        return self.to_tuple().__hash__()

    def __eq__(self, other):
        return self.to_tuple() == other.to_tuple()

class Noder():
    class Node():
        def __init__(self, index, facing=Vec(0,1) ):
            self.index = index
            self.facing = facing
            self.is_inverter = False

    def __init__(self):
        self.node_dict = dict()

    def add_node(self, index, facing=Vec(0,1)):
        if index not in self.node_dict.keys():
            self.node_dict[index] = [Noder.Node(index, facing)]
        else:
            self.node_dict[index].append(Noder.Node(index, facing))

    def get_all_nodes(self):
        #flatten the list of lists which is dict.values()
        return list(itertools.chain.from_iterable(self.node_dict.values()))

    def get_nodes_at(self, index):
        if index in self.node_dict.keys():
            return self.node_dict[index]
        return list()

    def has_node_at(self, index):
        return index in self.node_dict.keys()

    def invert_nodes_at(self, index):
        for node in self.get_nodes_at(index):
            node.is_inverter = not node.is_inverter


class Signaller():
    class Signal():
        def __init__(self, node):
            self.node = node
            self.start = node.position
            self.direction = node.facing
            self.head = start

        def extend(self):
            """Extends the signal by one cell in its direction.
            """
            self.head += self.direction


    def __init__(self, noder):
        self.signal_list = list()
        self.finished_signal_list = list()
        self.noder = noder
        self.signal_start_list = list()

    def update(self):
        for signal in self.signal_list:
            signal.extend()
        for signal in self.signal_list:
            if self.noder.has_node_at(signal.head) and signal.start != signal.head:
                self.signal_list.remove(signal)
                self.finished_signal_list.append(signal)
                self.add_signal(signal.head)

    def add_signal(self, index):
        if index in self.signal_start_list:
            return
        for node in self.noder.get_nodes_at(index):
            self.signal_list.append(Signaller.Signal(node))
        self.signal_start_list.append(index)

    def get_all_signals(self):
        return self.finished_signal_list + self.signal_list


if __name__ == '__main__':
    window = GameWindow()
    pyglet.app.run()

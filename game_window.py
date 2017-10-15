import pyglet
from pyglet.gl import GL_POINTS, GL_TRIANGLES, GL_LINES

from model import Model
from utils import Vec
class GameWindow(pyglet.window.Window):
    class GhostNode():
        def __init__(self, index, orientation):
            self.index = index
            self.orientation = orientation

    def __init__(self):
        super(GameWindow, self).__init__()
        self.cell_size = 40
        self.mouse_cell_index = Vec(-1,-1)
        self.model = Model()
        pyglet.clock.schedule_interval(self.model.update, 1)
        self.ghost_node = None
        self.right_click_timer = pyglet.clock.Clock()
        # self.set_mouse_visible(False)

    def on_draw(self):
        self.clear()
        self.draw_mouse_cell()
        if self.ghost_node:
            self.draw_triangle(self.ghost_node.index, self.ghost_node.orientation)
        for (cell_index, cell) in self.model.items():
            if cell.signal_list:
                self.draw_point(cell_index)
            for node in cell.node_list:
                self.draw_triangle(cell_index, node.orientation)


    def cell_location(self, cell_index):
        return Vec(cell_index.x * self.cell_size + self.cell_size // 2
        , cell_index.y * self.cell_size + self.cell_size // 2)

    def draw_mouse_cell(self):
        # self.draw_triangle(self.mouse_cell_index, 0)
        self.draw_point(self.mouse_cell_index)

    def draw_point(self, cell_index):
        cell_location = self.cell_location(cell_index)
        pyglet.graphics.draw(1, GL_POINTS, ('v2i', cell_location.to_tuple()))

    def draw_triangle(self, cell_index, orientation):
        position = self.cell_location(cell_index)
        length = self.cell_size // 2 - self.cell_size // 3
        width = self.cell_size // 2 - self.cell_size // 5
        len_vec = orientation.normalise(length)
        wid_vec = Vec(orientation.y, -orientation.x).normalise(width)
        point = position + len_vec
        left_corner = position - len_vec - wid_vec
        right_corner = position - len_vec + wid_vec
        triangle_vertices = (*left_corner, *right_corner, *point)
        pyglet.graphics.draw(3, GL_TRIANGLES, ('v2i', triangle_vertices))


    def point_ghost_node_towards_mouse(self):
        diff = self.mouse_cell_index - self.ghost_node.index
        if diff.magnitude() > 0:
            self.ghost_node.orientation = diff.normalise()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_cell_index = Vec(x // self.cell_size, y // self.cell_size)

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            self.ghost_node = GameWindow.GhostNode(self.mouse_cell_index, Vec(0,1))
        elif button == 4:
            self.right_click_timer.update_time()
            # self.model.nvert_nodes_at(self.mouse_cell_index)

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse_cell_index = Vec(x // self.cell_size, y // self.cell_size)
        if self.ghost_node:
            self.point_ghost_node_towards_mouse()

    def on_mouse_release(self, x, y, button, modifiers):
        if button == 1 and self.ghost_node:
            self.model.place_node(self.ghost_node.index, self.ghost_node.orientation)
            self.ghost_node = None
        elif button == 4:
            if self.right_click_timer.update_time() < 0.5:
                self.model.invert_nodes_at(self.mouse_cell_index)
            else:
                self.model.delete_nodes_at(self.mouse_cell_index)


if __name__ == '__main__':
    window = GameWindow()
    pyglet.app.run()

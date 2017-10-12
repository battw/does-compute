import pyglet
from pyglet.gl import GL_POINTS, GL_TRIANGLES, GL_LINES

from model import Model
from utils import Vec
class GameWindow(pyglet.window.Window):

    def __init__(self):
        super(GameWindow, self).__init__()
        self.cell_size = 20
        self.mouse_cell_index = Vec(-1,-1)
        self.model = Model()
        pyglet.clock.schedule_interval(self.model.update, 1)
        # self.set_mouse_visible(False)
        self.is_currently_placing_node = False

    def on_draw(self):
        self.clear()
        self.draw_mouse_cell()
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


    def point_ghost_node_towards_mouse(self):
        diff = self.mouse_cell_index - self.ghost_node.index
        if diff.magnitude() > 0:
            self.ghost_node.facing = diff.normalise()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_cell_index = Vec(x // self.cell_size, y // self.cell_size)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.button == 1:
            pass

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse_cell_index = Vec(x // self.cell_size, y // self.cell_size)
        if self.is_currently_placing_node:
            self.point_ghost_node_towards_mouse()

    def on_mouse_release(self, x, y, button, modifiers):
        pass



if __name__ == '__main__':
    window = GameWindow()
    pyglet.app.run()

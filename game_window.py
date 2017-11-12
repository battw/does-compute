import pyglet
from pyglet.gl import *

from model import Model, _Cellar
from utils import Vec
import imager


class GameWindow(pyglet.window.Window):
    class GhostNode():
        def __init__(self, index, orientation):
            self.index = index
            self.orientation = orientation

    def __init__(self):
        super(GameWindow, self).__init__(width=2000, height=1000)
        self.init_gl()
        # glClearColor(1,1,1,1)
        self.cell_size = 20
        self.mouse_cell_index = Vec(-1,-1)
        self.model = Model()
        pyglet.clock.schedule_interval(self.model.update, 0.01)
        self.ghost_node = None
        self.right_click_timer = pyglet.clock.Clock()
        self.drawer = _Drawer(self)
        # self.set_mouse_visible(False)

    def init_gl(self):
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pass

    def on_draw(self):
        # self.draw_mouse_cell()
        self.drawer.draw_model(self.model)
        # if self.ghost_node:
        #     self.draw_triangle(self.ghost_node.index, self.ghost_node.orientation)


    def cell_location(self, cell_index):
        return Vec(cell_index.x * self.cell_size + self.cell_size // 2
        , cell_index.y * self.cell_size + self.cell_size // 2)



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
                self.model.invert_nodes(self.mouse_cell_index)
            else:
                self.model.delete_nodes(self.mouse_cell_index)


class _Drawer():


    def __init__(self, game_window):
        self._game_window = game_window
        self._signal_sprite = self._get_signal_sprite()
        self._node_sprite = self._get_node_sprite()
        self._neg_node_sprite = self._get_neg_node_sprite()
        self._background_image = self._get_background_image_data()


    def draw_model(self, model):
        self._game_window.clear()
        self.draw_background()
        for (cell_index, items) in model.items():
            for item in items:
                if isinstance(item, _Cellar._Signal):
                    self.draw_signal(cell_index)
                if isinstance(item, _Cellar._Node):
                    self.draw_node(cell_index, item.orientation, inverted=item.is_inverted)

    def draw_background(self):
        self._background_image.blit(0,0)

    def draw_gui(self, input):
        pass
        #draw gui (currently the ghost node wotsit)
    def draw_mouse_cell(self):
        # self.draw_triangle(self.mouse_cell_index, 0)
        self.draw_point(self.mouse_cell_index)

    def draw_point(self, cell_index):
        cell_location = self._game_window.cell_location(cell_index)
        pyglet.graphics.draw(1, GL_POINTS, ('v2i', cell_location.to_tuple()))

    def draw_node(self, cell_index, orientation, inverted=False):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        cell_size_vec = Vec(self._game_window.cell_size / 2, self._game_window.cell_size / 2)
        position = self._game_window.cell_location(cell_index)
        sprite = self._node_sprite if not inverted else self._neg_node_sprite
        sprite.set_position(*position)
        sprite.rotation = -(orientation.angle() - 90)
        sprite.draw()

    def draw_signal(self, cell_index):
        #TODO create gl helper functions to do this stuff
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        cell_size_vec = Vec(self._game_window.cell_size / 2, self._game_window.cell_size / 2)
        position = self._game_window.cell_location(cell_index) - cell_size_vec
        self._signal_sprite.set_position(*position)
        self._signal_sprite.draw()

    def draw_circle(self, cell_index, orientation):
        pass

    def _get_signal_sprite(self):
        size = self._game_window.cell_size
        radius = size // 4
        image_data =  imager.CircleImageData(size, radius, (255,0,0))
        return pyglet.sprite.Sprite(image_data)

    def _get_node_sprite(self):
        length = self._game_window.cell_size
        width = self._game_window.cell_size
        image_data = imager.IsoTriangleImageData(length, width, (0,255,0))
        image_data.anchor_x = width // 2
        image_data.anchor_y = 0
        return pyglet.sprite.Sprite(image_data)

    def _get_neg_node_sprite(self):
        """The sprite for a negated node."""
        length = self._game_window.cell_size
        width = self._game_window.cell_size
        image_data = imager.IsoTriangleImageData(length, width, (0,0,0))
        image_data.anchor_x = width // 2
        image_data.anchor_y = 0
        return pyglet.sprite.Sprite(image_data)


    def _get_background_image_data(self):
        size_vec = Vec(self._game_window.width, self._game_window.height)
        cell_size = self._game_window.cell_size
        return imager.CheckeredBackgroundImageData(size_vec, cell_size, (240,240,240), (255,255,255))



if __name__ == '__main__':
    window = GameWindow()
    pyglet.app.run()

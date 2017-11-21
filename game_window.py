import pyglet
from pyglet.gl import *
from pyglet.window.key import *
import itertools
import time

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
        self.mouse_position = Vec(0,0)
        self.model = Model()
        pyglet.clock.schedule_interval(self.model.update, 0.1)
        self.ghost_node = None
        self.drawer = _Drawer(self)
        self.input_state_cycle = itertools.cycle(["DRAW", "COPY PASTE"])
        self.input_state = next(self.input_state_cycle)
        # self.set_mouse_visible(False)
        self.mouse_input = MouseInputHandler()
        self.mouse_input.register_callback(1, "CLICK", lambda: print("left click func"))
        self.mouse_input.register_callback(1, "HOLD", lambda: print("left hold func"))
        self.mouse_input.register_callback(1, "DRAG", lambda x: print("left drag func"))
        self.mouse_input.register_callback(4, "CLICK", lambda: print("right click func"))
        self.mouse_input.register_callback(4, "HOLD", lambda: print("right hold func"))
        self.mouse_input.register_callback(4, "DRAG", lambda x: print("right drag func"))

    def init_gl(self):
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pass

    def on_draw(self):
        # self.draw_mouse_cell()
        self.mouse_input.update(self.mouse_position)
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
        self.mouse_position = Vec(x,y)
        self.mouse_cell_index = Vec(x // self.cell_size, y // self.cell_size)

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_input.press(button, Vec(x,y))

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse_position = Vec(x,y)
        self.mouse_cell_index = Vec(x // self.cell_size, y // self.cell_size)

    def on_mouse_release(self, x, y, button, modifiers):
        self.mouse_input.release(button)

    def on_key_press(self, symbol, modifiers):
        super(GameWindow, self).on_key_press(symbol, modifiers)
        if symbol == SPACE:
            self.model.clear_signals()
        if symbol == X:
            self.input_state = next(self.input_state_cycle)



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
        image_data = imager.IsoTriangleImageData(length, width, (0,0,255))
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

class MouseInputHandler():

    def __init__(self, hold_time = 0.5):
        """hold_time is the minimum time a button needs to held before the
        the button is considered to be held rather than clicked."""
        self.min_hold_time = hold_time
        self.init_button_state()
        self._callback_dict = dict()

    def init_button_state(self):
        self.pressed_button = None
        self.pressed_button_state = None
        self.press_position = None
        self.press_time = None
        self.drag_vector = None

    def press(self, button, position):
        """Call this when a mouse button is pressed. """
        if self.pressed_button != None:
            self.init_button_state()
            return
        self.pressed_button = button
        self.pressed_button_state = "CLICK"
        self.press_position = position
        self.press_time = time.perf_counter()

    def release(self, button):
        """Call this when a mouse button is released.
        """
        if button == self.pressed_button:
            callback = self._callback_dict.get((button, self.pressed_button_state))
            if callback != None:
                if self.pressed_button_state == "DRAG":
                    callback(self.drag_vector)
                elif self.pressed_button_state in ["CLICK", "HOLD"]:
                    callback()

        self.init_button_state()

    def update(self, mouse_position):
        """Call this every frame."""
        if self.pressed_button == None:
            return

        current_time = time.perf_counter()
        if (mouse_position - self.press_position).magnitude() > 0:
            self.pressed_button_state = "DRAG"
            self.drag_vector = mouse_position - self.press_position
        elif current_time - self.press_time > self.min_hold_time:
            self.pressed_button_state = "HOLD"

    def register_callback(self, button, state, callback_func):
        self._callback_dict[(button, state)] = callback_func




if __name__ == '__main__':
    window = GameWindow()
    pyglet.app.run()

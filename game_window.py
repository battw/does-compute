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
        # self.ghost_node = None
        self.drawer = _Drawer(self)
        self.input_state_cycle = itertools.cycle(["DRAW", "COPY PASTE"])
        self.input_state = next(self.input_state_cycle)
        self.set_mouse_visible(False)
        self.mouse_input = MouseInputHandler()
        model_input_wrapper = ModelInputWrapper(self.model, self.position_to_cell_index)
        self.mouse_input.register_callback(1, "CLICK", model_input_wrapper.place_node)
        self.mouse_input.register_callback(1, "DRAG", model_input_wrapper.place_node)
        self.mouse_input.register_callback(4, "CLICK", model_input_wrapper.invert_nodes)
        self.mouse_input.register_callback(4, "HOLD", model_input_wrapper.delete_nodes)

    def init_gl(self):
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pass

    def on_draw(self):
        self.mouse_input.update(self.mouse_position)
        self.drawer.draw_model()
        self.drawer.draw_gui(self.mouse_position)




    def cell_location(self, cell_index):
        return Vec(cell_index.x * self.cell_size + self.cell_size // 2
        , cell_index.y * self.cell_size + self.cell_size // 2)

    def position_to_cell_index(self, position):
        return Vec(position.x // self.cell_size, position.y //self.cell_size)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_position = Vec(x,y)
        self.mouse_cell_index = self.position_to_cell_index(Vec(x,y))

    def on_mouse_press(self, x, y, button, modifiers):
        self.mouse_input.press(button, Vec(x,y))

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse_position = Vec(x,y)
        self.mouse_cell_index = self.position_to_cell_index(Vec(x,y))

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
        self._node_sprite = self._get_node_sprite((150, 150, 150, 255))
        self._neg_node_sprite = self._get_node_sprite((0, 0, 0, 255))
        self._ghost_node_sprite = self._get_node_sprite((150, 150, 150, 150))
        self._background_image = self._get_background_image_data()
        self._cursor_sprite = self._get_cursor_sprite((100, 100, 200, 100))
        self._held_cursor_sprite = self._get_cursor_sprite((0, 0, 0, 200))


    def draw_model(self):
        self._game_window.clear()
        self.draw_background()
        for (cell_index, items) in self._game_window.model.items():
            for item in items:
                if isinstance(item, _Cellar._Signal):
                    self.draw_signal(cell_index)
                if isinstance(item, _Cellar._Node):
                    sprite = (self._node_sprite if not item.is_inverted
                              else self._neg_node_sprite)
                    self.draw_node(cell_index, item.orientation, sprite)

    def draw_background(self):
        self._background_image.blit(0,0)

    def draw_gui(self, mouse_position):
        if self._game_window.mouse_input.pressed_button == 1:
            orientation = (Vec(0,1) if self._game_window.mouse_input.drag_vector == None
                                    else self._game_window.mouse_input.drag_vector)
            self.draw_ghost_node(self._game_window.mouse_input.press_position,
                                        orientation.normalise(1.4))
        elif (self._game_window.mouse_input.pressed_button == 4
        and self._game_window.mouse_input.pressed_button_state == "DRAG"
        and isinstance(self._game_window.mouse_input.drag_vector, Vec)):
            self.draw_select_box(self._game_window.mouse_input.press_position,
                                        self._game_window.mouse_input.drag_vector)
        elif (self._game_window.mouse_input.pressed_button == 4
        and self._game_window.mouse_input.pressed_button_state == "HOLD"):
            self.draw_cursor_cell(mouse_position, self._held_cursor_sprite)
        else:
            self.draw_cursor_cell(mouse_position, self._cursor_sprite)


    def draw_select_box(self, position, drag_vector):
        end_position = position + drag_vector
        bottom_left_corner = Vec(min(position.x, end_position.x),
                                 min(position.y, end_position.y))
        up_vec = Vec(0, abs(drag_vector.y))
        across_vec = Vec(abs(drag_vector.x), 0)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pyglet.graphics.draw(4, GL_POLYGON,
                             ('v2i',
                              (*bottom_left_corner,
                               *(bottom_left_corner + across_vec),
                               *(bottom_left_corner + across_vec + up_vec),
                               *(bottom_left_corner + up_vec)
                              )),
                             ('c4B', (0, 0, 255, 100) * 4))

    def draw_cursor_cell(self, cursor_position, sprite):
        half_cell_size = self._game_window.cell_size // 2
        cell_location = (self._game_window.cell_location(
            self._game_window.position_to_cell_index(cursor_position))
            - Vec(half_cell_size, half_cell_size))
        sprite.set_position(*cell_location)
        sprite.draw()

    def draw_node(self, cell_index, orientation, sprite):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        cell_size_vec = Vec(self._game_window.cell_size / 2, self._game_window.cell_size / 2)
        position = self._game_window.cell_location(cell_index)
        sprite.set_position(*position)
        sprite.rotation = -(orientation.angle() - 90)
        sprite.draw()

    def draw_ghost_node(self, position, orientation):
        self.draw_node(self._game_window.position_to_cell_index(position), orientation,
                           self._ghost_node_sprite)

    def draw_signal(self, cell_index):
        #TODO create gl helper functions to do this stuff
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        cell_size_vec = Vec(self._game_window.cell_size / 2, self._game_window.cell_size / 2)
        position = self._game_window.cell_location(cell_index) - cell_size_vec
        self._signal_sprite.set_position(*position)
        self._signal_sprite.draw()

    def _get_cursor_sprite(self, colour):
        size = self._game_window.cell_size
        image_data = imager.SquareImageData(size, colour)
        return pyglet.sprite.Sprite(image_data)

    def _get_signal_sprite(self):
        size = self._game_window.cell_size
        radius = size // 4
        image_data =  imager.CircleImageData(size, radius, (255,0,0))
        return pyglet.sprite.Sprite(image_data)

    def _get_node_sprite(self, rgba_colour):
        length = self._game_window.cell_size
        width = self._game_window.cell_size
        image_data = imager.IsoTriangleImageData(length, width, rgba_colour)
        image_data.anchor_x = width // 2
        image_data.anchor_y = 0
        return pyglet.sprite.Sprite(image_data)


    def _get_background_image_data(self):
        size_vec = Vec(self._game_window.width, self._game_window.height)
        cell_size = self._game_window.cell_size
        return imager.CheckeredBackgroundImageData(size_vec, cell_size, (240,240,240), (255,255,255))

class MouseInputHandler():

    def __init__(self, hold_time = 0.5, min_drag_movement = 10):
        """hold_time is the minimum time a button needs to held before the
        the button is considered to be held rather than clicked.
        min_drag_movement is the minimum amount the mouse needs to have moved
        in order to count as having dragged."""
        self.min_hold_time = hold_time
        self.min_drag_movement = min_drag_movement
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
                    callback(self.press_position, self.drag_vector)
                elif self.pressed_button_state in ["CLICK", "HOLD"]:
                    callback(self.press_position)

        self.init_button_state()

    def update(self, mouse_position):
        """Call this every frame."""
        if self.pressed_button == None:
            return

        current_time = time.perf_counter()
        if (mouse_position - self.press_position).magnitude() > self.min_drag_movement:
            self.pressed_button_state = "DRAG"
            self.drag_vector = mouse_position - self.press_position
        elif current_time - self.press_time > self.min_hold_time:
            self.pressed_button_state = "HOLD"

    def register_callback(self, button, state, callback_func):
        self._callback_dict[(button, state)] = callback_func


class ModelInputWrapper():
    def __init__(self, model, position_to_cell_func):
        """position_to_cell_func translates screen coordinates to
        cell indexes (as Vecs)."""
        self._model = model
        self._position_to_cell_func = position_to_cell_func

    def place_node(self, press_position, drag_vector=Vec(0,1)):
        self._model.place_node(self._position_to_cell_func(press_position), drag_vector)

    def copy_nodes(self, press_position, drag_vector):
        self._model.copy_nodes(press_position, press_position + drag_vector)

    def invert_nodes(self, press_position):
        self._model.invert_nodes(self._position_to_cell_func(press_position))

    def delete_nodes(self, press_position):
        self._model.delete_nodes(self._position_to_cell_func(press_position))


if __name__ == '__main__':
    window = GameWindow()
    pyglet.app.run()

import pyglet
from pyglet.gl import *
from pyglet.window.key import *
import itertools
import time
import pickle

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
        self.cell_size = 20
        self.mouse_cell_index = Vec(-1,-1)
        self.mouse_position = Vec(0,0)
        self.drawer = _Drawer(self)
        self.set_mouse_visible(False)

        self.load_model(Model())
        self.set_input_state("DEFAULT")

    def load_model(self, model):
        self.model = model
        pyglet.clock.schedule_interval(self.model.update, 0.1)
        model_input_wrapper = ModelInputWrapper(self.model, self)
        self.default_mouse_input = MouseInputHandler()
        self.default_mouse_input.register_callback(
            1, "CLICK", model_input_wrapper.place_node)
        self.default_mouse_input.register_callback(
            1, "HOLD", model_input_wrapper.place_node)
        self.default_mouse_input.register_callback(
            1, "DRAG", model_input_wrapper.place_node)
        self.default_mouse_input.register_callback(
            4, "CLICK", model_input_wrapper.invert_nodes)
        self.default_mouse_input.register_callback(
            4, "HOLD", model_input_wrapper.delete_nodes)
        self.default_mouse_input.register_callback(
            4, "DRAG", model_input_wrapper.copy_nodes)

        self.pasting_mouse_input = MouseInputHandler()
        self.pasting_mouse_input.register_callback(
            1, "CLICK", model_input_wrapper.paste_nodes)
        self.pasting_mouse_input.register_callback(
            1, "HOLD", model_input_wrapper.paste_nodes)
        self.pasting_mouse_input.register_callback(
            4, "CLICK", model_input_wrapper.change_to_default_input_state)
        self.pasting_mouse_input.register_callback(
            4, "HOLD", model_input_wrapper.change_to_default_input_state)
        self.pasting_mouse_input.register_callback(
            4, "DRAG", model_input_wrapper.change_to_default_input_state)

        self.deleting_mouse_input = MouseInputHandler()
        self.deleting_mouse_input.register_callback(
            1, "DRAG", model_input_wrapper.delete_nodes
        )
        self.deleting_mouse_input.register_callback(
            4, "CLICK", model_input_wrapper.change_to_default_input_state
        )
        self.deleting_mouse_input.register_callback(
            4, "HOLD", model_input_wrapper.change_to_default_input_state
        )
        self.deleting_mouse_input.register_callback(
            4, "DRAG", model_input_wrapper.change_to_default_input_state
        )

    def set_input_state(self, state):
        self._input_state = state
        if state == "DEFAULT":
            self.current_mouse_input = self.default_mouse_input
        elif state == "PASTING":
            self.current_mouse_input = self.pasting_mouse_input
        elif state == "DELETING":
            self.current_mouse_input = self.deleting_mouse_input
        else: raise Error("Tried to switch to an invalid state")

    def on_draw(self):
        self.current_mouse_input.update(self.mouse_position)
        self.drawer.draw_model()
        self.drawer.draw_gui(self.mouse_position)

    def cell_position(self, cell_index):
        return Vec(cell_index.x * self.cell_size + self.cell_size // 2
        , cell_index.y * self.cell_size + self.cell_size // 2)

    def cell_index(self, position):
        return Vec(position.x // self.cell_size, position.y //self.cell_size)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_position = Vec(x,y)
        self.mouse_cell_index = self.cell_index(Vec(x,y))

    def on_mouse_press(self, x, y, button, modifiers):
        self.current_mouse_input.press(button, Vec(x,y))

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.mouse_position = Vec(x,y)
        self.mouse_cell_index = self.cell_index(Vec(x,y))

    def on_mouse_release(self, x, y, button, modifiers):
        self.current_mouse_input.release(button)

    def on_key_press(self, symbol, modifiers):
        super(GameWindow, self).on_key_press(symbol, modifiers)
        if symbol == SPACE:
            self.model.clear_signals()
        elif symbol == S:
            self.save()
        elif symbol == L:
            self.load()
        elif symbol == D:
            self.set_input_state("DELETING")

    def save(self):
        with open("sav", "wb") as handle:
            pickle.dump(self.model, handle)

    def load(self):
        with open("sav", "rb") as handle:
            self.load_model(pickle.loads(handle.read()))
            self.set_input_state("DEFAULT")


class _Drawer():
    def __init__(self, game_window):
        self._game_window = game_window
        self._signal_sprite = self._get_signal_sprite()
        self._node_sprite = self._get_node_sprite((150, 150, 150, 255))
        self._neg_node_sprite = self._get_node_sprite((0, 0, 0, 255))
        self._ghost_node_sprite = self._get_node_sprite((150, 150, 150, 150))
        self._background_image = self._get_background_image_data()
        self._cursor_sprite = self._get_cursor_sprite((100, 100, 200, 100))
        self._pasting_cursor_sprite = self._get_cursor_sprite((100, 0, 0, 100))
        self._held_cursor_sprite = self._get_cursor_sprite((0, 0, 0, 200))
        self._deleting_cursor_sprite = self._get_cursor_sprite((0,0,0,100))


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
        if self._game_window._input_state == "DEFAULT":
            mouse_input = self._game_window.default_mouse_input
            if mouse_input.pressed_button == 1:
                orientation = (Vec(0,1) if mouse_input.drag_vector == None
                                        else mouse_input.drag_vector)
                self.draw_ghost_node(mouse_input.press_position,
                                            orientation.normalise(1.4))
            elif (mouse_input.pressed_button == 4
                and mouse_input.pressed_button_state == "DRAG"
                and isinstance(mouse_input.drag_vector, Vec)):
                self.draw_select_box(mouse_input.press_position,
                                            mouse_input.drag_vector)
            elif (mouse_input.pressed_button == 4
                  and mouse_input.pressed_button_state == "HOLD"):
                self.draw_cursor_cell(mouse_position, self._held_cursor_sprite)
            else:
                self.draw_cursor_cell(mouse_position, self._cursor_sprite)
        elif self._game_window._input_state == "PASTING":
            self.draw_cursor_cell(mouse_position, self._pasting_cursor_sprite)
        elif self._game_window._input_state == "DELETING":
            mouse_input = self._game_window.deleting_mouse_input
            if (mouse_input.pressed_button == 1
                and mouse_input.pressed_button_state == "DRAG"):
                self.draw_delete_box(mouse_input.press_position,
                                     mouse_input.drag_vector)
            else:
                self.draw_cursor_cell(mouse_position, self._deleting_cursor_sprite)




    def draw_box(self, position, drag_vector, colour):
        end_position = position + drag_vector
        bottom_left_corner = Vec(min(position.x, end_position.x),
                                 min(position.y, end_position.y))
        #snap to cell boundary
        #THERE MUST BE A SIMPLER WAY TO FIND THE CORNERS
        cell_size = self._game_window.cell_size
        mod_x = bottom_left_corner.x % cell_size
        mod_y = bottom_left_corner.y % cell_size
        bottom_left_corner = Vec(bottom_left_corner.x // cell_size * cell_size,
                                 bottom_left_corner.y // cell_size * cell_size)
        across_vec = Vec((abs(drag_vector.x) + mod_x + cell_size) // cell_size * cell_size, 0)
        up_vec = Vec(0, (abs(drag_vector.y) +  mod_y + cell_size) //  cell_size * cell_size)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pyglet.graphics.draw(4, GL_POLYGON,
                             ('v2i',
                              (*bottom_left_corner,
                               *(bottom_left_corner + across_vec),
                               *(bottom_left_corner + across_vec + up_vec),
                               *(bottom_left_corner + up_vec)
                              )),
                             ('c4B', colour * 4))

    def draw_select_box(self, start_position, drag_vector):
        self.draw_box(start_position, drag_vector, (0, 0, 255, 100))

    def draw_delete_box(self, start_position, drag_vector):
        self.draw_box(start_position, drag_vector, (0, 0, 0, 100))

    def draw_cursor_cell(self, cursor_position, sprite):
        half_cell_size = self._game_window.cell_size // 2
        cell_location = (self._game_window.cell_position(
            self._game_window.cell_index(cursor_position))
            - Vec(half_cell_size, half_cell_size))
        sprite.set_position(*cell_location)
        sprite.draw()

    def draw_node(self, cell_index, orientation, sprite):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        cell_size_vec = Vec(self._game_window.cell_size / 2, self._game_window.cell_size / 2)
        position = self._game_window.cell_position(cell_index)
        sprite.set_position(*position)
        sprite.rotation = -(orientation.angle() - 90)
        sprite.draw()

    def draw_ghost_node(self, position, orientation):
        self.draw_node(self._game_window.cell_index(position), orientation,
                           self._ghost_node_sprite)

    def draw_signal(self, cell_index):
        #TODO create gl helper functions to do this stuff
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        cell_size_vec = Vec(self._game_window.cell_size / 2, self._game_window.cell_size / 2)
        position = self._game_window.cell_position(cell_index) - cell_size_vec
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
    def __init__(self, model, game_window):
        """position_to_cell_func translates screen coordinates to
        cell indexes (as Vecs)."""
        self._model = model
        self._game_window = game_window
        self._position_to_cell_func = game_window.cell_index

    def place_node(self, press_position, drag_vector=Vec(0,1)):
        self._model.place_node(
            self._position_to_cell_func(press_position), drag_vector)

    def copy_nodes(self, press_position, drag_vector):
        self._model.copy_nodes(self._position_to_cell_func(press_position),
                               self._position_to_cell_func(press_position
                                                           + drag_vector))
        self._game_window.set_input_state("PASTING")

    def paste_nodes(self, press_position):
        self._model.paste_nodes(self._position_to_cell_func(press_position))

    def change_to_default_input_state(self, press_position):
        self._game_window.set_input_state("DEFAULT")

    def invert_nodes(self, press_position):
        self._model.invert_nodes(self._position_to_cell_func(press_position))

    def delete_nodes(self, press_position, drag_vector=None):
        self._model.delete_nodes(self._position_to_cell_func(press_position),
                                 self._position_to_cell_func(press_position
                                                             + drag_vector))


if __name__ == '__main__':
    window = GameWindow()
    pyglet.app.run()

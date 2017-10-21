from utils import Vec

class Model():
    def __init__(self):
        self._item_list = list()
        self._cellar = Cellar()

    def update(self, dt):
        pass

    def place_node(self, position, orientation):
        pass

    def delete_nodes(self, position):
        pass

    def invert_nodes(self, position):
        pass

    def items(self):
        pass


class _Cellar():
    pass

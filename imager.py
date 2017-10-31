from pyglet.image import ImageData
from utils import Vec

class CircleImageData(ImageData):
    def __init__(self, size, radius, colour):
        format = "RGBA"
        self.centre = size / 2
        self.size = size
        self.radius = radius
        self.colour = colour
        data = self._make_bytes()
        super(CircleImageData, self).__init__(size, size, format, data)

    def _dist_from_centre(self, x, y):
        diff = Vec(x, y) - Vec(self.centre, self.centre)
        return diff.magnitude()

    def _make_bytes(self):
        (r,g,b) = self.colour
        numbers = list()
        for x in range(self.size):
            for y in range(self.size):
                if self._dist_from_centre(x,y) > self.radius:
                    numbers += [r,g,b,0]
                else:
                    numbers += [r,g,b,255]
        return bytes(numbers)

class CheckeredBackgroundImageData(ImageData):
    def __init__(self, size_vec, cell_size, colour1, colour2):
        self.colour1 = colour1
        self.colour2 = colour2
        self.size_vec = size_vec
        self.cell_size = cell_size
        format = "RGB"
        data = self._make_bytes()
        super(CheckeredBackgroundImageData, self).__init__(size_vec.x, size_vec.y, format, data)

    def _make_bytes(self):
        def is_colour1(x, y):
            return (x % (2*self.cell_size) > self.cell_size and y % (2*self.cell_size) > self.cell_size
                or x % (2*self.cell_size) < self.cell_size and y % (2*self.cell_size) < self.cell_size)

        numbers = list()
        for y in range(self.size_vec.y):
            for x in range(self.size_vec.x):
                if is_colour1(x, y):
                    numbers.extend(self.colour1)
                else:
                    numbers.extend(self.colour2)

        return bytes(numbers)

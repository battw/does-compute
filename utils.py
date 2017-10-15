from math import sqrt

class Vec():
    def __init__(self, x, y):
        self.x = int(round(x))
        self.y = int(round(y))

    def __str__(self):
        return "Vec({}, {})".format(self.x, self.y)

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

from collections import namedtuple
import numbers
import math
import ode

from orthogonalspace import utils

Vector = namedtuple('Vector', ('x', 'y', 'z'))
class Vector:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def norm(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def normalize(self):
        norm = self.norm()
        return Vector(self.x / norm,
                      self.y / norm,
                      self.z / norm)

    def __add__(self, other):
        return Vector(self.x + other[0],
                      self.y + other[1],
                      self.z + other[2])

    def __neg__(self):
        return Vector(-self.x, -self.y, -self.z)

    def __abs__(self):
        return Vector(abs(self.x),
                      abs(self.y),
                      abs(self.z))

    def __sub__(self, other):
        return Vector(self.x + other[0],
                      self.y + other[1],
                      self.z + other[2])

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Vector(self.x * other,
                          self.y * other,
                          self.z * other)
        else:
            return Vector(self.x * other[0],
                          self.y * other[1],
                          self.z * other[2])

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return Vector(self.x / other,
                          self.y / other,
                          self.z / other)
        else:
            raise ValueError()

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __len__(self):
        return 3

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            raise IndexError()

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        elif key == 2:
            self.z = value
        else:
            raise KeyError()

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __str__(self):
        return '< {0.x:.4f}, {0.y:.4f}, {0.z:.4f} >'.format(self)

    def __getstate__(self):
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
        }


class Body:
    def __init__(self, universe, *args, **kwargs):
        self.universe = universe
        self.body = ode.Body(universe.world)

    def __getstate__(self):
        return utils.include_attrs(self, 'mass', 'position', 'velocity', 'force')

    @property
    def mass(self):
        return self.body.getMass()

    @mass.setter
    def mass(self, value):
        self.body.setMass(value)

    @property
    def position(self):
        return Vector(*self.body.getPosition())

    @position.setter
    def position(self, value):
        self.body.setPosition(value)

    @property
    def velocity(self):
        return Vector(*self.body.getLinearVel())

    @velocity.setter
    def velocity(self, value):
        self.body.setLinearVel(value)

    @property
    def force(self):
        return Vector(*self.body.getForce())

    @force.setter
    def force(self, value):
        self.body.setForce(value)

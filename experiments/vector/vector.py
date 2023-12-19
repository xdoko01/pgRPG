from collections import namedtuple
from dataclasses import dataclass
from pygame.math import Vector2
from math import sqrt

@dataclass(frozen=True)
class Vect:
    x: int|float
    y: int|float

    def __add__(self, other):
        return Vect(self.x+other.x, self.y+other.y)
    
    def __sub__(self, other):
        return Vect(self.x-other.x, self.y-other.y)

    def __mul__(self, const):
        return Vect(self.x*const, self.y*const)

    def length(self):
        return sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        return Vect(self.x/self.length(), self.y/self.length())

if __name__ == '__main__':
    a = (1,1)
    b = (2,2)
    print(a+b)

    p=Vect(x=-5, y=10)
    q=Vect(x=1, y=2)
    w=p+q
    print(w)
    print(f'{w=}, {w*2.1=}, {w.length()=}, {Vect(0,5).normalize()}, {w-p=}, {(w-p).x=}')
    o=w-p

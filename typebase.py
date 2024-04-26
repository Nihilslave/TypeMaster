import types
from typing import Union

from typechart import TYPECHART

class Type:
    TYPES = {}
    def __new__(cls, t: Union[str, 'Type']):
        if isinstance(t, Type):
            return t
        t = t.lower()
        if t not in cls.TYPES:
            cls.TYPES[t] = super().__new__(cls)
            cls.TYPES[t].ID = t
            cls.TYPES[t].chart = TYPECHART.get(t)
        return cls.TYPES[t]
    @staticmethod
    def typechart():
        pass # TODO: print typechart
    @staticmethod
    def toID(t: Union[str, 'Type']):
        if isinstance(t, Type):
            return t.ID
        return t.lower()
    def getcoeff(self, t: Union[str, 'Type']):
        return self.chart.get(Type.toID(t))
    def weakto(self, t: Union[str, 'Type']):
        return (self.getcoeff(t) == 1)
    def resists(self, t: Union[str, 'Type']):
        return (self.getcoeff(t) == -1)
    def immuneto(self, t: Union[str, 'Type']):
        return (self.getcoeff(t) == -64)
    def supeffto(self, t: Union[str, 'Type']):
        return Type(t).weakto(self)
    def resistedby(self, t: Union[str, 'Type']):
        return Type(t).resists(self)
    def ineffagainst(self, t: Union[str, 'Type']):
        return Type(t).immuneto(self)

BUG = Type('bug')
DARK = Type('dark')
DRAGON = Type('dragon')
ELECTRIC = Type('electric')
FAIRY = Type('fairy')
FIGHTING = Type('fighting')
FIRE = Type('fire')
FLYING = Type('flying')
GHOST = Type('ghost')
GRASS = Type('grass')
GROUND = Type('ground')
ICE = Type('ice')
NORMAL = Type('normal')
POISON = Type('poison')
PSYCHIC = Type('psychic')
ROCK = Type('rock')
STEEL = Type('steel')
WATER = Type('water')
TYPES = types.MappingProxyType(Type.TYPES)

class TypeComb:
    def __init__(self, typeComb: Union[str, list, Type, 'TypeComb']):
        if isinstance(typeComb, TypeComb):
            typeComb = typeComb.typelist
        elif isinstance(typeComb, str):
            typeComb = [t.strip() for t in typeComb.split(',')]
        elif isinstance(typeComb, Type):
            typeComb = [typeComb]
        self.typelist = list(set(Type(t) for t in typeComb))
        self.typelist.sort(key=lambda t: t.ID)
    @property
    def ID(self):
        return ','.join(t.ID for t in self.typelist)
    @property
    def chart(self):
        chart = {}
        for t in TYPES:
            chart[t.ID] = self.getcoeff(t)
        return chart
    @property
    def size(self):
        return len(self.typelist)
    def getcoeff(self, t: Union[str, Type, 'TypeComb']):
        if isinstance(t, TypeComb):
            return max(self.getcoeff(_) for _ in t.typelist)
        coeff = 0
        for _ in self.typelist:
            coeff += _.getcoeff(t)
        return coeff
    def weakto(self, t: Union[str, Type, 'TypeComb']):
        return (self.getcoeff(t) > 0)
    def resists(self, t: Union[str, Type, 'TypeComb']):
        return (self.getcoeff(t) < 0 and self.getcoeff(t) > -4)
    def immuneto(self, t: Union[str, Type, 'TypeComb']):
        return (self.getcoeff(t) <= -4)
    def supeffto(self, t: Union[str, Type, 'TypeComb']):
        return any(t.weakto(_) for _ in self.typelist)
    def resistedby(self, t: Union[str, Type, 'TypeComb']):
        return any(t.resists(_) for _ in self.typelist)
    def ineffagainst(self, t: Union[str, Type, 'TypeComb']):
        return any(t.immuneto(_) for _ in self.typelist)

if __name__ == '__main__':
    print(TypeComb([STEEL, FAIRY]).weakto(TypeComb([BUG, FIGHTING])))
    print(TypeComb([STEEL, FAIRY]).resists(TypeComb([BUG, FLYING])))
    print(TypeComb([STEEL, FAIRY]).resistedby(STEEL))

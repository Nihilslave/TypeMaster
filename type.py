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
        return (self.getcoeff(t) == 2)
    def immuneto(self, t: Union[str, 'Type']):
        return (self.getcoeff(t) == 3)
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
    def __init__(self, typeComb: Union[str, list, 'TypeComb']):
        if isinstance(typeComb, TypeComb):
            self.typelist = typeComb.typelist[:]
        elif isinstance(typeComb, list):
            self.typelist = [Type.toType(t) for t in typeComb]
        else:
            self.typelist = [Type.toType(t.strip()) for t in typeComb.split(',')]
        self.typelist.sort(key=lambda t: t.ID)
    @property
    def ID(self):
        return ','.join(t.ID for t in self.typelist)
    def weakto(self, t: Union[str, 'Type']): # TODO: support TypeComb
        coeff = 0
        for _ in self.typelist:
            _Coeff = _.getcoeff(t)
            if _Coeff == 3:
                return 0
            if _Coeff == 2:
                coeff -= 1
            if _Coeff == 1:
                coeff += 1
        return coeff
    def resists(self, t: Union[str, 'Type']):
        t = Type.toID(t)
        return (self.chart.get(t, -1) == 2)
    def immuneto(self, t: Union[str, 'Type']):
        t = Type.toID(t)
        return (self.chart.get(t, -1) == 3)
    def supeffto(self, t: Union[str, 'Type']):
        t = Type.toType(t)
        return t.weakto(self)
    def resistedby(self, t: Union[str, 'Type']):
        t = Type.toType(t)
        return t.resists(self)
    def ineffagainst(self, t: Union[str, 'Type']):
        t = Type.toType(t)
        return t.immuneto(self)

if __name__ == '__main__':
    print(FIRE.ID)
    print(FIRE.supeffto(STEEL))

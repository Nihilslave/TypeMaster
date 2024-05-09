import itertools
from math import inf
from types import MappingProxyType
from typing import Union
import time
import multiprocessing

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
        buf = 'def\\off\t' + '\t'.join(Type.TYPES.keys()).replace('electric', 'electrc').replace('fighting', 'fightng') + '\n'
        for t, T in Type.TYPES.items():
            buf += t.replace('electric', 'electrc').replace('fighting', 'fightng')
            for tt in Type.TYPES:
                buf += '\t' + str(T.chart.get(tt)).replace('inf', '')
            buf += '\n'
        print(buf)
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
        return (self.getcoeff(t) == -inf)
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
TYPES = MappingProxyType(Type.TYPES)
def TYPECOMBS(n):
    return itertools.combinations_with_replacement(TYPES, n)
def __timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time} seconds to run.")
        return result
    return wrapper
@__timer
def typecomb_looper(n, task, *args, multiProcessing=False):
    if multiProcessing:
        with multiprocessing.Pool() as pool:
            result = pool.starmap(task, itertools.product(TYPECOMBS(n), *map(lambda a: [a], args)))
    else:
        result = []
        for _ in TYPECOMBS(n):
            result.append(task(_, *args))
    return result

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
        return (self.getcoeff(t) < 0 and self.getcoeff(t) != -inf)
    def immuneto(self, t: Union[str, Type, 'TypeComb']):
        return (self.getcoeff(t) == -inf)
    def supeffto(self, t: Union[str, Type, 'TypeComb']):
        return any(TypeComb(t).weakto(_) for _ in self.typelist)
    def resistedby(self, t: Union[str, Type, 'TypeComb']):
        return all(TypeComb(t).resists(_) for _ in self.typelist)
    def ineffagainst(self, t: Union[str, Type, 'TypeComb']):
        return all(TypeComb(t).immuneto(_) for _ in self.typelist)
    def weaknesses(self):
        return [t for t in TYPES if self.weakto(t)]
    def resistances(self):
        return [t for t in TYPES if self.resists(t)]
    def immunities(self):
        return [t for t in TYPES if self.immuneto(t)]
    def coverage(self):
        return {
            'super effective to': ','.join(t for t in TYPES if self.supeffto(t)),
            'resisted by': ','.join(t for t in TYPES if self.resistedby(t)),
            'immuned by': ','.join(t for t in TYPES if self.ineffagainst(t)),
        }
    def defoutclassedby(self, t: Union[str, Type, 'TypeComb']):
        t = TypeComb(t)
        for _ in TYPES:
            if self.immuneto(_) and t.immuneto(_):
                continue
            if self.getcoeff(_) < t.getcoeff(_):
                return False
        return True
    def offoutclassedby(self, n, t: Union[str, Type, 'TypeComb']):
        t = TypeComb(t)
        for tc in TYPECOMBS(n):
            tc = TypeComb(tc)
            if tc.immuneto(self) and tc.immuneto(t):
                continue
            if tc.getcoeff(self) > tc.getcoeff(t):
                return False
        return True

class Team:
    def __init__(self):
        self.tclist: list[TypeComb] = []
    @property
    def ID(self):
        return ';'.join(sorted(map(lambda tc: tc.ID, self.tclist)))
    @property
    def size(self):
        return len(self.tclist)
    def add(self, typeComb: Union[str, list, Type, TypeComb]):
        self.tclist.append(TypeComb(typeComb))
        return self
    def getcoeff(self, t: Union[str, Type, TypeComb]):
        return min(tc.getcoeff(t) for tc in self.tclist)
    def getcoeffs(self, t: Union[str, Type, TypeComb]):
        return sorted(tc.getcoeff(t) for tc in self.tclist)
    def weakto(self, t: Union[str, Type, TypeComb]):
        return (self.getcoeff(t) > 0)
    def resists(self, t: Union[str, Type, TypeComb]):
        return (self.getcoeff(t) < 0 and self.getcoeff(t) != -inf)
    def immuneto(self, t: Union[str, Type, TypeComb]):
        return (self.getcoeff(t) == -inf)
    def supeffto(self, t: Union[str, Type, TypeComb]):
        return any(tc.supeffto(t) for tc in self.tclist)
    def resistedby(self, t: Union[str, Type, TypeComb]):
        return all(tc.resistedby(t) for tc in self.tclist)
    def ineffagainst(self, t: Union[str, Type, TypeComb]):
        return all(tc.ineffagainst(t) for tc in self.tclist)

def TEAMS(n, m):
    return itertools.combinations(TYPECOMBS(n), m)
@__timer
def team_looper(n, m, task, *args, multiProcessing=False):
    if multiProcessing:
        with multiprocessing.Pool() as pool:
            result = pool.starmap(task, itertools.product(TEAMS(n, m), *map(lambda a: [a], args)))
    else:
        result = []
        for _ in TEAMS(n, m):
            result.append(task(_, *args))
    return result

if __name__ == '__main__':
    Type.typechart()

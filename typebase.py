import types
import itertools
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
            result = pool.starmap(task, itertools.product(*map(lambda a: [a], args), TYPECOMBS(n)))
        return result
    else:
        result = []
        for _ in TYPECOMBS(n):
            result.append(task(*args, _))
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
        return (self.getcoeff(t) < 0 and self.getcoeff(t) > -4)
    def immuneto(self, t: Union[str, Type, 'TypeComb']):
        return (self.getcoeff(t) <= -4)
    def supeffto(self, t: Union[str, Type, 'TypeComb']):
        return any(t.weakto(_) for _ in self.typelist)
    def resistedby(self, t: Union[str, Type, 'TypeComb']):
        return all(t.resists(_) for _ in self.typelist)
    def ineffagainst(self, t: Union[str, Type, 'TypeComb']):
        return all(t.immuneto(_) for _ in self.typelist)
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
    def add(self, typeComb: Union[str, list, Type, TypeComb]):
        # if len(self.tclist) >= 6:
        #     raise IndexError('Already 6 or more Pokemon in this team!')
        self.tclist.append(TypeComb(typeComb))
        return self
    def getcoeff(self, t: Union[str, Type, TypeComb]):
        return min(tc.getcoeff(t) for tc in self.tclist)
    def weakto(self, t: Union[str, Type, TypeComb]):
        return (self.getcoeff(t) > 0)
    def resists(self, t: Union[str, Type, TypeComb]):
        return (self.getcoeff(t) < 0 and self.getcoeff(t) > -4)
    def immuneto(self, t: Union[str, Type, TypeComb]):
        return (self.getcoeff(t) <= -4)
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
            result = pool.starmap(task, itertools.product(*map(lambda a: [a], args), TEAMS(n, m)))
        return result
    else:
        result = []
        for _ in TEAMS(n, m):
            result.append(task(*args, _))
        return result

if __name__ == '__main__':
    teams = [
        Team().add([DARK, STEEL]).add([DRAGON, FAIRY]).add([FLYING, STEEL]),
        Team().add([DRAGON, FAIRY]).add([FIRE, FLYING]).add([NORMAL, STEEL]),
        Team().add([DRAGON, FAIRY]).add([GHOST, WATER]).add([NORMAL, STEEL]),
        Team().add([DRAGON, FAIRY]).add([ELECTRIC, STEEL]).add([FIRE, FLYING]),
        Team().add([DARK, STEEL]).add([DRAGON, GHOST]).add([FLYING, STEEL]),
        Team().add([DRAGON, GHOST]).add([FIRE, FLYING]).add([NORMAL, STEEL]),
        Team().add([DRAGON, FAIRY]).add([FLYING, WATER]).add([NORMAL, STEEL]),
        Team().add([DRAGON, FAIRY]).add([FLYING, STEEL]).add([NORMAL, STEEL]),
        Team().add([DRAGON, FAIRY]).add([ELECTRIC, STEEL]).add([GHOST, WATER]),
        Team().add([DARK, DRAGON]).add([FLYING, WATER]).add([GHOST, STEEL]),
    ]
    for i, team in enumerate(teams):
        print(f"{i + 1}. {team.ID} weakto:")
        for tc in TYPECOMBS(2):
            tc = TypeComb(tc)
            coeff = team.getcoeff(tc)
            if coeff > 0:
                print(f"{tc.ID}: {coeff}")

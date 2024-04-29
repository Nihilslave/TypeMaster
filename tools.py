from typebase import *

class Logger:
    def __init__(self):
        self.enabled = True
    def enable(self):
        self.enabled = True
    def disable(self):
        self.enabled = False
    def log(self, *args, **kwargs):
        if self.enabled is False:
            return
        print(*args, **kwargs)

LOGGER = Logger()

def printDict(d: dict, sortByValues=True, reverse=True, firstX=-1):
    if sortByValues:
        d = sorted(d.items(), key=lambda item: item[1], reverse=reverse)
    else:
        d = d.items()
    if firstX > 0:
        d = d[:firstX]
    for i, (key, value) in enumerate(d):
        print(f"{i + 1}. {key}: {value}")

def typechart(n, typeComb, hideDetailsAbove=None):
    typeComb = TypeComb(typeComb)
    res1 = {}
    res2: dict[tuple, list] = {}
    for tc in TYPECOMBS(n):
        tc = TypeComb(tc)
        coeff_def = typeComb.getcoeff(tc)
        coeff_def = -64 if coeff_def <= -4 else coeff_def
        res2_key_def = ('def', coeff_def, tc.size)
        if res2_key_def not in res2:
            res2[res2_key_def] = []
        res2[res2_key_def].append(tc.ID)
        coeff_off = tc.getcoeff(typeComb)
        coeff_off = -64 if coeff_off <= -4 else coeff_off
        res2_key_off = ('off', coeff_off, tc.size)
        if res2_key_off not in res2:
            res2[res2_key_off] = []
        res2[res2_key_off].append(tc.ID)
    return printTypechart(res2, hideDetailsAbove or (n - 1))

def printTypechart(typechart: dict[tuple, list], hideDetailsAbove=1):
    buf = {}
    for (category, coeff, size) in sorted(typechart.keys()):
        if coeff == 0:
            continue
        key = f"{category}_{coeff}_{size}"
        value = typechart[(category, coeff, size)]
        buf_key = (category, size)
        if buf_key not in buf:
            buf[buf_key] = 0
        if coeff > 0:
            buf[buf_key] += len(value)
        if coeff < 0:
            buf[buf_key] -= len(value)
        if size > hideDetailsAbove:
            value = f'{len(value)} type combinations'
        key = key.replace('def_-1', 'resistances2x')\
            .replace('def_-2', 'resistances4x')\
            .replace('def_-64', 'immunities')\
            .replace('def_1', 'weaknesses2x')\
            .replace('def_2', 'weaknesses4x')\
            .replace('off_-1', 'resisted2x')\
            .replace('off_-2', 'resisted4x')\
            .replace('off_-64', 'ineffective')\
            .replace('off_1', 'supereffective2x')\
            .replace('off_2', 'supereffective4x')
        LOGGER.log(f"{key}: {value}")
    for (category, size) in sorted(buf.keys()):
        if category == 'def':
            buf[(category, size)] *= -1
        LOGGER.log(f"{category}ensiveDelta_{size}: {buf[(category, size)]}")
    return typechart, buf

def findTypeComb(n, predicate):
    return list(filter(predicate, TYPECOMBS(n)))

if __name__ == '__main__':
    team = Team().add([DRAGON, FAIRY]).add([DRAGON, STEEL]).add([FLYING, STEEL])
    res = findTypeComb(2, lambda tc: team.getcoeff(TypeComb(tc)) > 0)
    for t in TYPES:
        print(t)
        for tc in res:
            if t in tc:
                print(tc)

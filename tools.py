import itertools

from typebase import *

DO_PRINT = True

def log(*args, **kwargs):
    if DO_PRINT is False:
        return
    print(*args, **kwargs)

def printDict(d):
    if isinstance(d, dict):
        d = d.items()
    for key, value in d:
        print(f"{key}: {value}")

def typechart(n, typeComb, hideDetailsAbove=None):
    typeComb = TypeComb(typeComb)
    res1 = {}
    res2: dict[tuple, list] = {}
    for tc in itertools.combinations_with_replacement(TYPES, n):
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
        log(f"{key}: {value}")
    for (category, size) in sorted(buf.keys()):
        if category == 'def':
            buf[(category, size)] *= -1
        log(f"{category}ensiveDelta_{size}: {buf[(category, size)]}")
    return typechart, buf

if __name__ == '__main__':
    DO_PRINT = False
    deltaSums = {}
    for typeComb in itertools.combinations_with_replacement(TYPES, 2):
        typeComb = TypeComb(typeComb)
        _, deltas = typechart(2, typeComb)
        deltaSum = sum(deltas.values())
        deltaSums[typeComb.ID] = deltaSum
    print(len(deltaSums))
    printDict(sorted(deltaSums.items(), key=lambda item: item[1], reverse=True))
    DO_PRINT = True
    typechart(2, [FIRE, GROUND])

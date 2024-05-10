import os
import json

from tools import *

def __cache(cacheName, cacheArgsMapper, saveOrdered=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs = {k: v for k, v in kwargs.items() if k != 'multiProcessing'}
            cacheArgs = cacheArgsMapper(*args, **kwargs)
            cache = f"results/{cacheName}_{cacheArgs}.json"
            cache_o = f"results/ordered/{cacheName}_{cacheArgs}.json"
            if os.path.isfile(cache):
                LOGGER.log("cache exists, loading data from cache...")
                with open(cache, 'r') as load:
                    return json.load(load)
            res: dict = func(*args, **kwargs)
            with open(cache, 'w') as save:
                json.dump(res, save, indent=4)
            if saveOrdered:
                res_o = dict(sorted(res.items(), key=lambda item: item[1], reverse=True))
                with open(cache_o, 'w') as save_o:
                    json.dump(res_o, save_o, indent=4)
            return res
        return wrapper
    return decorator

def task_BestTypeCombs(tc, weights0):
    tc1 = TypeComb(tc)
    weight = 0
    for tc2 in weights0:
        tc2 = TypeComb(tc2)
        id2 = tc2.ID
        coeff_def = tc1.getcoeff(tc2)
        if coeff_def < -2:
            weight += 4 * weights0[id2]
        if coeff_def == -2:
            weight += 3 * weights0[id2]
        if coeff_def == -1:
            weight += 2 * weights0[id2]
        if coeff_def == 1:
            weight -= 2 * weights0[id2]
        if coeff_def == 2:
            weight -= 4 * weights0[id2]
        coeff_off = tc2.getcoeff(tc1)
        if coeff_off < -2:
            weight -= 3 * weights0[id2]
        if coeff_off == -2:
            weight -= 2 * weights0[id2]
        if coeff_off == -1:
            weight -= 1.5 * weights0[id2]
        if coeff_off == 1:
            weight += 1.5 * weights0[id2]
        if coeff_off == 2:
            weight += 2 * weights0[id2]
    return tc1.ID, weight

@__cache('typecombrank', lambda n, *args, **kwargs: str(n))
def BestTypeCombs(n, normalizer=None, distancer=lambda weights0, weights1: sum(abs(w0 - w1) for w0, w1 in zip(weights0.values(), weights1.values())), multiProcessing=False):
    weights0 = {TypeComb(tc).ID: 1 for tc in TYPECOMBS(n)}
    for i in range(1000):
        weights1 = dict(typecomb_looper(n, task_BestTypeCombs, weights0, multiProcessing=multiProcessing))
        weights1_min = min(weights1.values())
        weights1 = {k: (v - weights1_min) for k, v in weights1.items()}
        weights1_mul = len(weights1) / sum(weights1.values())
        weights1 = {k: (v * weights1_mul) for k, v in weights1.items()}
        distance = distancer(weights0, weights1)
        LOGGER.log(f"iteration {i}, distance = {distance}")
        if distance < 0.01:
            return weights1
        weights0 = weights1.copy()

TYPECOMB_WEIGHTS = BestTypeCombs(2)

@__cache('typerank', lambda n, goodCombOnly=False: str(n) + ("_g" if goodCombOnly else ""))
def BestType(n, goodCombOnly=False):
    weights: dict[str, float] = BestTypeCombs(n)
    res = {}
    for t in TYPES:
        res[t] = 0
    for tc, w in weights.items():
        if goodCombOnly and w < 0.7:
            continue
        tt = tc.split(',')
        for t in tt:
            res[t] += w
    return res

def task_BestTeamTypeCombs1(tcs):
    team = Team()
    for tc in tcs:
        team.add(tc)
    res = 0
    for tc, weight in TYPECOMB_WEIGHTS.items():
        coeff = team.getcoeff(TypeComb(tc))
        if coeff < -2:
            res += 4 * weight
        if coeff == -2:
            res += 3 * weight
        if coeff == -1:
            res += 2 * weight
        if coeff == 1:
            res -= 2 * weight
        if coeff == 2:
            res -= 4 * weight
    return team.ID, res

def task_BestTeamTypeCombs2(tcs):
    team = Team()
    for tc in tcs:
        team.add(tc)
    res = 0
    for tc, weight in TYPECOMB_WEIGHTS.items():
        tc = TypeComb(tc)
        coeffs = sorted(teamtc.getcoeff(TypeComb(tc)) for teamtc in team.tclist)
        coeffs = [-64 if coeff < -2 else coeff for coeff in coeffs]
        weak4xcnt, weak2xcnt = coeffs.count(2), coeffs.count(1)
        weakcnt = weak4xcnt + weak2xcnt
        res2xcnt, res4xcnt = coeffs.count(-1), coeffs.count(-2)
        rescnt, immcnt = res2xcnt + res4xcnt, coeffs.count(-64)
        roicnt = rescnt + immcnt
        halfsize = team.size / 2

        res -= weak4xcnt * 2 * weight
        if weakcnt == 3:
            res -= 4 * weight
        if weakcnt == 2:
            res -= 2 * weight
        if roicnt == 0:
            res -= weight
        if roicnt == 1:
            res += 2 * weight
        if roicnt == 2:
            res += 3 * weight
        if roicnt == 3:
            res += 4 * weight
    return team.ID, res

@__cache('teamtypecombrank', lambda n, m, handler=task_BestTeamTypeCombs2: f"{n}_{m}_v{handler.__name__[-1]}")
def BestTeamTypeCombs(n, m, handler=task_BestTeamTypeCombs2, multiProcessing=True):
    return dict(team_looper(n, m, handler, multiProcessing=multiProcessing))

def BestTeamTypeCombs_f(n, m, predicate):
    table = BestTeamTypeCombs(n, m)
    table = {k: v for k, v in table.items() if predicate(k, v)}
    return table

@__cache('outclassedtable', lambda category, n: f"{category}_{n}", saveOrdered=False)
def task_OutclassedTable(category, n):
    res: dict[str, list] = {}
    for tc1 in TYPECOMBS(n):
        tc1 = TypeComb(tc1)
        res[tc1.ID] = []
        for tc2 in TYPECOMBS(n):
            tc2 = TypeComb(tc2)
            if tc2.ID == tc1.ID:
                continue
            if category == 'def':
                if tc1.defoutclassedby(tc2):
                    res[tc1.ID].append(tc2.ID)
            if category == 'off':
                if tc1.size == 1 and tc1.ID in tc2.ID.split(','):
                    continue
                if tc1.offoutclassedby(n, tc2):
                    res[tc1.ID].append(tc2.ID)
    res = {k: v for k, v in res.items() if v}
    return res

def task_TypeCombsThatResistsEverything(tcs):
    team = Team()
    for tc in tcs:
        team.add(tc)
    for t in TYPES:
        if team.getcoeff(t) >= 0:
            return team.ID, False
    return team.ID, True

def TypeCombsThatResistsEverything(n, m, multiProcessing=True):
    res = team_looper(n, m, task_TypeCombsThatResistsEverything, multiProcessing=multiProcessing)
    return [_[0] for _ in res if _[1]]

def gen_task_results():
    BestTypeCombs(2)
    BestType(2, goodCombOnly=False)
    BestType(2, goodCombOnly=True)
    BestTeamTypeCombs(2, 3)
    task_OutclassedTable('def', 2)
    task_OutclassedTable('off', 2)

if __name__ == '__main__':
    gen_task_results()
    printDict(BestTeamTypeCombs_f(2, 3, lambda k, v: 'dragon,steel' not in k and 'flying,steel' not in k), firstX=10)

import os
import json
from tools import *

TASK_BESTTYPECOMBS_CACHE = 'typecombrank'
TASK_OUTCLASSEDTABLE_CACHE = 'outclassedtable'

def task_BestTypeCombs(
        n,
        normalizer=None, # TODO: have something here
        distancer=lambda weights0, weights1: sum(abs(w0 - w1) for w0, w1 in zip(weights0.values(), weights1.values()))
        ):
    cache = f"{TASK_BESTTYPECOMBS_CACHE}_{n}.json"
    if os.path.isfile(cache):
        LOGGER.log("cache exists, loading data from cache...")
        with open(cache, 'r') as load:
            return json.load(load)
    weights0 = {}
    weights1 = {}
    # initialize weights
    for typeComb in TYPECOMBS(n):
        typeComb = TypeComb(typeComb)
        weights0[typeComb.ID] = 1
        weights1[typeComb.ID] = 0
    for i in range(1000):
        # calc new weight
        for typeComb1 in TYPECOMBS(n):
            typeComb1 = TypeComb(typeComb1)
            id1 = typeComb1.ID
            for typeComb2 in TYPECOMBS(n):
                typeComb2 = TypeComb(typeComb2)
                id2 = typeComb2.ID
                coeff_def = typeComb1.getcoeff(typeComb2)
                if coeff_def < -2:
                    weights1[id1] += 4 * weights0[id2]
                if coeff_def == -2:
                    weights1[id1] += 3 * weights0[id2]
                if coeff_def == -1:
                    weights1[id1] += 2 * weights0[id2]
                if coeff_def == 1:
                    weights1[id1] -= 2 * weights0[id2]
                if coeff_def == 2:
                    weights1[id1] -= 4 * weights0[id2]
                coeff_off = typeComb2.getcoeff(typeComb1)
                if coeff_off < -2:
                    weights1[id1] -= 3 * weights0[id2]
                if coeff_off == -2:
                    weights1[id1] -= 2 * weights0[id2]
                if coeff_off == -1:
                    weights1[id1] -= 1.5 * weights0[id2]
                if coeff_off == 1:
                    weights1[id1] += 1.5 * weights0[id2]
                if coeff_off == 2:
                    weights1[id1] += 2 * weights0[id2]
        # normalize new weight
        weights1_min = min(weights1.values())
        weights1 = {k: (v - weights1_min) for k, v in weights1.items()}
        weights1_mul = len(weights1) / sum(weights1.values())
        weights1 = {k: (v * weights1_mul) for k, v in weights1.items()}
        distance = distancer(weights0, weights1)
        LOGGER.log(f"iteration {i}, distance = {distance}")
        if distance < 0.01:
            with open(cache, 'w') as save:
                json.dump(weights1, save, indent=4)
            return weights1
        # prepare for the next iteration
        for key in weights0.keys():
            weights0[key] = weights1[key]
            weights1[key] = 0

TYPECOMB_WEIGHTS = task_BestTypeCombs(2)

def task_BestType(n, goodCombOnly=False):
    weights: dict[str, float] = task_BestTypeCombs(n)
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

def task_OutclassedTable(category, n):
    cache = f"{TASK_OUTCLASSEDTABLE_CACHE}_{category}_{n}.json"
    if os.path.isfile(cache):
        LOGGER.log("cache exists, loading data from cache...")
        with open(cache, 'r') as load:
            return json.load(load)
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
    with open(cache, 'w') as save:
        json.dump(res, save, indent=4)
    return res

def task_BestTeamTypeCombs(tcs):
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

def BestTeamTypeCombs(n, m, multiProcessing=False):
    return dict(team_looper(n, m, task_BestTeamTypeCombs, multiProcessing=multiProcessing))

def gen_task_results():
    task_BestTypeCombs(2)
    task_OutclassedTable('def', 2)
    task_OutclassedTable('off', 2)

if __name__ == '__main__':
    gen_task_results()
    printDict(BestTeamTypeCombs(2, 3, multiProcessing=True), firstX=100) # about 83 seconds

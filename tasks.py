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

def task_BestTeamTypeCombs(n, m):
    weights = task_BestTypeCombs(n)
    res = {}
    for tcs in itertools.combinations(TYPECOMBS(n), m):
        team = Team()
        for tc in tcs:
            team.add(tc)
        print(team.ID)
        res[team.ID] = 0
        for tc, weight in weights.items():
            coeff = team.getcoeff(TypeComb(tc))
            if coeff < -2:
                res[team.ID] += 4 * weight
            if coeff == -2:
                res[team.ID] += 3 * weight
            if coeff == -1:
                res[team.ID] += 2 * weight
            if coeff == 1:
                res[team.ID] -= 2 * weight
            if coeff == 2:
                res[team.ID] -= 4 * weight
    return res

if __name__ == '__main__':
    # printDict(task_OutclassedTable('def', 2))
    printDict(task_OutclassedTable('off', 2))

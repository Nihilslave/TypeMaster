from tools import *

def task_BestTypeCombs(
        n,
        normalizer=None, # TODO: have something here
        distancer=lambda weights0, weights1: sum(abs(w0 - w1) for w0, w1 in zip(weights0.values(), weights1.values()))
        ):
    weights0 = {}
    weights1 = {}
    # initial weights
    for typeComb in itertools.combinations_with_replacement(TYPES, n):
        typeComb = TypeComb(typeComb)
        weights0[typeComb.ID] = 1
        weights1[typeComb.ID] = 0
    for i in range(1000):
        # calc new weight
        for typeComb1 in itertools.combinations_with_replacement(TYPES, n):
            typeComb1 = TypeComb(typeComb1)
            id1 = typeComb1.ID
            for typeComb2 in itertools.combinations_with_replacement(TYPES, n):
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
        print(f"iteration {i}, distance = {distance}")
        if distance < 0.01:
            return weights1
        # prepare for the next iteration
        for key in weights0.keys():
            weights0[key] = weights1[key]
            weights1[key] = 0


if __name__ == '__main__':
    res = task_BestTypeCombs(2)
    printDict(sorted(res.items(), key=lambda item: item[1], reverse=True))

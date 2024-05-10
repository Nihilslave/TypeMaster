from typebase import *
from utils import *

class handlers:
    def handler_BestTypeCombs1(tc, weights0):
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
    def handler_BestTypeCombs2(tc, weights0):
        tc1 = TypeComb(tc)
        weight_def, weight_off = 0, 0
        for tc2 in weights0:
            tc2 = TypeComb(tc2)
            id2 = tc2.ID
            coeff_def = tc1.getcoeff(tc2)
            if coeff_def < -2:
                weight_def += 4 * weights0[id2][1]
            if coeff_def == -2:
                weight_def += 3 * weights0[id2][1]
            if coeff_def == -1:
                weight_def += 2 * weights0[id2][1]
            if coeff_def == 1:
                weight_def -= 2 * weights0[id2][1]
            if coeff_def == 2:
                weight_def -= 4 * weights0[id2][1]
            coeff_off = tc2.getcoeff(tc1)
            if coeff_off < -2:
                weight_off -= 3 * weights0[id2][0]
            if coeff_off == -2:
                weight_off -= 2 * weights0[id2][0]
            if coeff_off == -1:
                weight_off -= 1.5 * weights0[id2][0]
            if coeff_off == 1:
                weight_off += 1.5 * weights0[id2][0]
            if coeff_off == 2:
                weight_off += 2 * weights0[id2][0]
        return tc1.ID, (weight_def, weight_off)
    _handlers = [handler_BestTypeCombs1, handler_BestTypeCombs2]
    def get(version):
        return handlers._handlers[version - 1]
class normalizers:
    def normalizer1(weights: dict):
        weights_min = min(weights.values())
        weights = {k: (v - weights_min) for k, v in weights.items()}
        weights_mul = len(weights) / sum(weights.values())
        weights = {k: (v * weights_mul) for k, v in weights.items()}
        return weights
    def normalizer2(weights: dict):
        weights_min_def = min(v[0] for v in weights.values())
        weights_min_off = min(v[1] for v in weights.values())
        weights_max_def = max(v[0] for v in weights.values())
        weights_max_off = max(v[1] for v in weights.values())
        weights = {k: ((v[0] - weights_min_def) / (weights_max_def - weights_min_def), (v[1] - weights_min_off) / (weights_max_off - weights_min_off)) for k, v in weights.items()}
        return weights
    _normalizers = [normalizer1, normalizer2]
    def get(version):
        return normalizers._normalizers[version - 1]
class distancers:
    def distancer1(weights0: dict, weights1: dict):
        return sum(abs(w0 - w1) for w0, w1 in zip(weights0.values(), weights1.values()))
    def distancer2(weights0: dict, weights1: dict):
        return sum(abs(w0[0] - w1[0]) + abs(w0[1] - w1[1]) for w0, w1 in zip(weights0.values(), weights1.values()))
    _distancers = [distancer1, distancer2]
    def get(version):
        return distancers._distancers[version - 1]
class postprocessors:
    def postprocessor1(res):
        return res
    def postprocessor2(res):
        pass
    _postprocessors = [postprocessor1, postprocessor2]
    def get(version):
        return postprocessors._postprocessors[version - 1]


@cache('typecombrank', lambda n, version=2, **kwargs: f"{n}_v{version}")
def BestTypeCombs(n, version=2, multiProcessing=False):
    weights0 = {}
    if version == 1:
        weights0 = {TypeComb(tc).ID: 1 for tc in TYPECOMBS(n)}
    if version == 2:
        weights0 = {TypeComb(tc).ID: (1, 1) for tc in TYPECOMBS(n)}
    for i in range(1000):
        weights1 = dict(typecomb_looper(n, handlers.get(version), weights0, multiProcessing=multiProcessing))
        weights1 = normalizers.get(version)(weights1)
        distance = distancers.get(version)(weights0, weights1)
        LOGGER.log(f"iteration {i}, distance = {distance}")
        if distance < 0.01:
            return weights1
        weights0 = weights1.copy()

if __name__ == '__main__':
    printDict(BestTypeCombs(2))

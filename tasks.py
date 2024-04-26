import tools
from tools import *

def task_BestTypeCombs(n, evaluation=lambda chart, deltas: sum(deltas.values())):
    tools.DO_PRINT = False
    evaluations = {}
    for typeComb in itertools.combinations_with_replacement(TYPES, n):
        typeComb = TypeComb(typeComb)
        chart, deltas = typechart(2, typeComb)
        evaluated = evaluation(chart, deltas)
        evaluations[typeComb.ID] = evaluated
    printDict(sorted(evaluations.items(), key=lambda item: item[1], reverse=True))
    tools.DO_PRINT = True

if __name__ == '__main__':
    task_BestTypeCombs(2)

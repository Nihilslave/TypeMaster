from typebase import *
from utils import *

@cache('outclassedtable', lambda category, n: f"{category}_{n}", saveOrdered=False)
def OutclassedTable(category, n):
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

if __name__ == '__main__':
    printDict(OutclassedTable('off', 2))
    printDict(OutclassedTable('def', 2))

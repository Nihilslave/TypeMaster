import os
import json

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

def cache(cacheName, cacheArgsMapper, saveOrdered=True):
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

if __name__ == '__main__':
    pass

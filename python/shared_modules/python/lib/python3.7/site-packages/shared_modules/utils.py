import time


def timer(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        ms = (te - ts) * 1000
        print(method.__name__, "took", ms, "ms")
        return result

    return timed

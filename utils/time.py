import functools
import time

count = 0
total = 0

def run_time(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kw):
        start = time.time()
        res = fn(*args, **kw)
        time_cost = time.time() - start
        global count
        global total
        total += time_cost
        count += 1
        print('%s 运行了 %f 秒' % (fn.__name__, time_cost))
        print('%s 平均时间： %f 秒' % (fn.__name__, total/count))
        return res

    return wrapper

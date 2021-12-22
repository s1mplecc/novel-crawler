import time

from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f'Running {func.__name__} mode ...')
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'Time spent: {end - start}s')
        return result

    return wrapper

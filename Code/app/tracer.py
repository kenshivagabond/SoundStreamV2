import time , functools

def trace_layer(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            print(f"⏱️ {name} took {time.perf_counter() - start:.4f}s")
            return result
        return wrapper
    return decorator
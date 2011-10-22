from functools import wraps

def stream(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    wrapper.stream = True
    return wrapper
from functools import wraps

def stream(func):
    @wraps(func)
    def wrapped(manager, *args, **kwargs):
        offset, limit = kwargs.pop('_offset', None), kwargs.pop('_limit', None)
        return func(manager, *args, **kwargs)[offset:limit].fetch_generic_relations()
    return wrapped

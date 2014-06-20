from functools import wraps


def stream(func):
    """
    Stream decorator to be applied to methods of an ``ActionManager`` subclass

    Syntax::

        from actstream.decorators import stream
        from actstream.managers import ActionManager

        class MyManager(ActionManager):
            @stream
            def foobar(self, ...):
                ...

    """
    @wraps(func)
    def wrapped(manager, *args, **kwargs):
        offset, limit = kwargs.pop('_offset', None), kwargs.pop('_limit', None)
        qs = func(manager, *args, **kwargs)
        if isinstance(qs, dict):
            qs = manager.public(**qs)
        elif isinstance(qs, (list, tuple)):
            qs = manager.public(*qs)
        if offset or limit:
            qs = qs[offset:limit]
        return qs.fetch_generic_relations()
    return wrapped

"""
Defines a field to store a set of verbs. It is preferable to use a set of
verbs than a M2M field in Follow for performance reasons
"""

from django.db import models


class VerbsField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ';')
        kwargs['null'] = True
        super(VerbsField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return set()
        if hasattr(value, '__iter__'):  # iterable but not string
            return set(value)
        return set(value.split(self.token))

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if not value:
            return
        assert(isinstance(value, (list, tuple, set)))
        return self.token.join([unicode(s) for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


try:
    from south.modelsinspector import add_introspection_rules
except:
    pass
else:
    add_introspection_rules([
        (
            [VerbsField],  # Class(es) these apply to
            [],  # Positional arguments (not used)
            {  # Keyword argument
                "token": ["token", {"default": ","}],
            },
        ),
    ], ["^actstream\.fields\.VerbsField"])

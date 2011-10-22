from django.db.models.query import QuerySet, EmptyQuerySet
from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.conf import settings
from django.db import models, connection
from django.utils.encoding import smart_unicode
from time import time

class GFKManager(Manager):
    """
    A manager that returns a GFKQuerySet instead of a regular QuerySet.

    """
    def get_query_set(self):
        return GFKQuerySet(self.model)

    def none(self):
        return self.get_query_set().none()

class GFKQuerySet(QuerySet):
    """
    A QuerySet with a fetch_generic_relations() method to bulk fetch
    all generic related items.  Similar to select_related(), but for
    generic foreign keys.

    Based on http://www.djangosnippets.org/snippets/984/
    Firstly improved at http://www.djangosnippets.org/snippets/1079/

    """
    def fetch_generic_relations(self):
        qs = self._clone()

        connection.queries = []
        gfk_fields = [g for g in self.model._meta.virtual_fields if isinstance(g, GenericForeignKey)]

        ct_map = {}
        data_map = {}
        for item in qs:
            for gfk in gfk_fields:
                ct_id_field = self.model._meta.get_field(gfk.ct_field).column
                ct_map.setdefault(
                    getattr(item, ct_id_field), {}
                    )[getattr(item, gfk.fk_field)] = (gfk.name, item.pk)

        ctypes = ContentType.objects.in_bulk(ct_map.keys())

        for ct_id, items_ in ct_map.items():
            if ct_id:
                ct = ctypes[ct_id]
                model_class = ct.model_class()
                for o in model_class.objects.select_related().filter(pk__in=items_.keys()):
                    (gfk_name, item_id) = items_[smart_unicode(o.pk)]
                    data_map[(ct_id, smart_unicode(o.pk))] = o

        for item in qs:
            for gfk in gfk_fields:
                if (getattr(item, gfk.fk_field) != None):
                    ct_id_field = self.model._meta.get_field(gfk.ct_field).column
                    setattr(item, gfk.name, data_map[(getattr(item, ct_id_field), getattr(item, gfk.fk_field))])

        return qs

    def none(self):
        return self._clone(klass=EmptyGFKQuerySet)

class EmptyGFKQuerySet(GFKQuerySet, EmptyQuerySet):
    pass

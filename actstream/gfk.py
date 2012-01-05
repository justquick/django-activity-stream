from django.conf import settings
from django.db.models import Manager
from django.db.models.query import QuerySet, EmptyQuerySet
from django.utils.encoding import smart_unicode

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

USE_PREFETCH = getattr(settings, 'USE_PREFETCH', False)
FETCH_RELATIONS = getattr(settings, 'FETCH_RELATIONS', True)


class GFKManager(Manager):
    """
    A manager that returns a GFKQuerySet instead of a regular QuerySet.

    """
    def get_query_set(self):
        return GFKQuerySet(self.model, using=self.db)

    def none(self):
        return self.get_query_set().none()


class GFKQuerySet(QuerySet):
    """
    A QuerySet with a fetch_generic_relations() method to bulk fetch
    all generic related items.  Similar to select_related(), but for
    generic foreign keys.

    Based on http://www.djangosnippets.org/snippets/984/
    Firstly improved at http://www.djangosnippets.org/snippets/1079/

    Extended in django-activity-stream to allow for multi db, text primary keys
    and empty querysets.
    """
    def fetch_generic_relations(self, *args):
        qs = self._clone()

        if not FETCH_RELATIONS:
            return qs

        gfk_fields = [g for g in self.model._meta.virtual_fields
                      if isinstance(g, GenericForeignKey)]
        if args:
            gfk_fields = filter(lambda g: g.name in args, gfk_fields)

        if USE_PREFETCH and hasattr(self, 'prefetch_related'):
            return qs.prefetch_related(*[g.name for g in gfk_fields])

        ct_map, data_map = {}, {}

        for item in qs:
            for gfk in gfk_fields:
                ct_id_field = self.model._meta.get_field(gfk.ct_field).column
                ct_map.setdefault(getattr(item, ct_id_field), {}
                    )[smart_unicode(getattr(item, gfk.fk_field))] = (gfk.name,
                        item.pk)

        ctypes = ContentType.objects.using(self.db).in_bulk(ct_map.keys())

        for ct_id, items_ in ct_map.items():
            if ct_id:
                ct = ctypes[ct_id]
                model_class = ct.model_class()
                objects = model_class._default_manager.select_related()
                for o in objects.filter(pk__in=items_.keys()):
                    (gfk_name, item_id) = items_[smart_unicode(o.pk)]
                    data_map[(ct_id, smart_unicode(o.pk))] = o

        for item in qs:
            for gfk in gfk_fields:
                if getattr(item, gfk.fk_field) != None:
                    ct_id_field = self.model._meta.get_field(gfk.ct_field)\
                        .column
                    setattr(item, gfk.name,
                        data_map[(
                            getattr(item, ct_id_field),
                            smart_unicode(getattr(item, gfk.fk_field))
                        )])

        return qs

    def none(self):
        return self._clone(klass=EmptyGFKQuerySet)


class EmptyGFKQuerySet(GFKQuerySet, EmptyQuerySet):
    def fetch_generic_relations(self):
        return self

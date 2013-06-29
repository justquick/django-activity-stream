from django.db.models import Manager
from django.db.models.query import QuerySet, EmptyQuerySet

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

from actstream.compat import smart_text


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

    Extended in django-activity-stream to allow for multi db, text primary keys
    and empty querysets.
    """
    def fetch_generic_relations(self, *args):
        from actstream import settings as actstream_settings

        qs = self._clone()

        if not actstream_settings.FETCH_RELATIONS:
            return qs

        gfk_fields = [g for g in self.model._meta.virtual_fields
                      if isinstance(g, GenericForeignKey)]

        if args:
            gfk_fields = filter(lambda g: g.name in args, gfk_fields)

        if actstream_settings.USE_PREFETCH and hasattr(self, 'prefetch_related'):
            return qs.prefetch_related(*[g.name for g in gfk_fields])

        ct_map, data_map = {}, {}

        for item in qs:
            for gfk in gfk_fields:
                if getattr(item, gfk.fk_field) is None:
                    continue
                ct_id_field = self.model._meta.get_field(gfk.ct_field).column
                if getattr(item, ct_id_field) is None:
                    continue
                ct_map.setdefault(getattr(item, ct_id_field), {}
                    )[smart_text(getattr(item, gfk.fk_field))] = (gfk.name,
                        item.pk)

        ctypes = ContentType.objects.in_bulk(ct_map.keys())

        for ct_id, items_ in ct_map.items():
            if ct_id:
                ct = ctypes[ct_id]
                model_class = ct.model_class()
                objects = model_class._default_manager.select_related(
                    depth=actstream_settings.GFK_FETCH_DEPTH)
                for o in objects.filter(pk__in=items_.keys()):
                    (gfk_name, item_id) = items_[smart_text(o.pk)]
                    data_map[(ct_id, smart_text(o.pk))] = o

        for item in qs:
            for gfk in gfk_fields:
                try:
                    if getattr(item, gfk.fk_field) is not None:
                        ct_id_field = self.model._meta.get_field(gfk.ct_field)\
                            .column
                        setattr(item, gfk.name,
                            data_map[(
                                getattr(item, ct_id_field),
                                smart_text(getattr(item, gfk.fk_field))
                            )])
                except KeyError:
                    continue

        return qs

    def none(self):
        return self._clone(klass=EmptyGFKQuerySet)


class EmptyGFKQuerySet(GFKQuerySet, EmptyQuerySet):
    def fetch_generic_relations(self):
        return self

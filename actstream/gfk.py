from django.db.models import Manager
from django.db.models.query import QuerySet, EmptyQuerySet
from django import VERSION as DJANGO_VERSION
try:
    from django.contrib.contenttypes.fields import GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericForeignKey

from actstream import settings


class GFKManager(Manager):
    """
    A manager that returns a GFKQuerySet instead of a regular QuerySet.

    """
    def get_query_set(self):
        return GFKQuerySet(self.model)
    get_queryset = get_query_set

    def none(self):
        return self.get_queryset().none()


class GFKQuerySet(QuerySet):
    """
    A QuerySet with a fetch_generic_relations() method to bulk fetch
    all generic related items.  Similar to select_related(), but for
    generic foreign keys. This wraps QuerySet.prefetch_related.
    """
    def fetch_generic_relations(self, *args):
        qs = self._clone()

        if not settings.FETCH_RELATIONS:
            return qs

        # Backward compatibility patch for
        # Django versions lower than 1.11.x
        if DJANGO_VERSION >= (1, 11):
            private_fields = self.model._meta.private_fields
        else:
            private_fields = self.model._meta.virtual_fields

        gfk_fields = [g for g in private_fields if isinstance(g, GenericForeignKey)]

        if args:
            gfk_fields = [g for g in gfk_fields if g.name in args]

        return qs.prefetch_related(*[g.name for g in gfk_fields])

    def none(self):
        clone = self._clone(klass=EmptyGFKQuerySet)
        if hasattr(clone.query, 'set_empty'):
            clone.query.set_empty()
        return clone


class EmptyGFKQuerySet(GFKQuerySet, EmptyQuerySet):
    def fetch_generic_relations(self, *args):
        return self

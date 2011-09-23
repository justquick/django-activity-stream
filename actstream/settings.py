from django.conf import settings
from django.db.models import get_model

MODELS = getattr(settings, 'ACTSTREAM_ACTION_MODELS', ('auth.User',))
MODELS = [get_model(*m.split('.')) for m in MODELS]
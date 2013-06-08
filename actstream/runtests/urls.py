import os
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), 'media')}),
    (r'auth/', include('django.contrib.auth.urls')),
    (r'', include('actstream.urls')),
)


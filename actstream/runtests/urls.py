import os
from django.contrib import admin
try:
    from django.conf.urls import patterns, include
except ImportError:
    from django.conf.urls.defaults import patterns, include

admin.autodiscover()


urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), 'media')}),
    (r'auth/', include('django.contrib.auth.urls')),
    (r'testapp/', include('testapp.urls')),
    (r'', include('actstream.urls')),
)

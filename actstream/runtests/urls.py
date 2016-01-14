import os

import django
from django.contrib import admin
from django.views.static import serve
try:
    from django.conf.urls import patterns, include, url
except ImportError:
    from django.conf.urls.defaults import patterns, include, url

admin.autodiscover()


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': os.path.join(os.path.dirname(__file__), 'media')}),
    url(r'auth/', include('django.contrib.auth.urls')),
    url(r'testapp/', include('testapp.urls')),
    url(r'', include('actstream.urls')),
]

if django.VERSION[:2] < (1, 9):
    urlpatterns = patterns('', *urlpatterns)

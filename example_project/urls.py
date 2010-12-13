import os
from django.conf.urls.defaults import *
from django.contrib import admin
from testapp import views

admin.autodiscover()

urlpatterns = patterns('',
    (r'^stories/$', views.stories, {}, 'testapp_stories'),
    (r'^story/(?P<story_id>\d+)$', views.story, {}, 'testapp_story'),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': os.path.join(os.path.dirname(__file__), 'media')}),
    (r'', include('actstream.urls')),
)


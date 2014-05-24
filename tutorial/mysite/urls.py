from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url('^activity/', include('actstream.urls')),
    url(r'^comments/', include('django_comments.urls')),
    url(r'^polls/', include('polls.urls', namespace='polls')),
    url(r'^admin/', include(admin.site.urls)),
]

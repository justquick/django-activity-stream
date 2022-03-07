import os
from django.contrib import admin
from django.views.static import serve
from django.urls import include, re_path, path
from django.conf import settings


urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve,
            {'document_root': os.path.join(os.path.dirname(__file__), 'media')}),
    re_path(r'auth/', include('django.contrib.auth.urls')),
    re_path(r'testapp/', include('testapp.urls')),
    re_path(r'', include('actstream.urls')),
]

if settings.DRF:
    from actstream.drf.urls import router
    if 'drf_spectacular' in settings.INSTALLED_APPS:
        from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
        urlpatterns += [
            # YOUR PATTERNS
            path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
            # Optional UI:
            path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
            path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        ]
    urlpatterns += [
        path('api/', include(router.urls)),
        path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]


if 'debug_toolbar' in settings.INSTALLED_APPS:
    urlpatterns.insert(0, re_path('__debug__/', include('debug_toolbar.urls')))

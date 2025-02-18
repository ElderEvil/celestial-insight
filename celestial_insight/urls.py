from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from celestial_insight.api import api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("_allauth/", include("allauth.headless.urls")),
    path("api/", api.urls),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

urlpatterns += [path("i18n/", include("django.conf.urls.i18n"))]

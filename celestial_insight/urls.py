from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from celestial_insight.api import api
from tarot import views as tarot_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.account.urls")),
    path("accounts/", include("allauth.socialaccount.urls")),
    path("accounts/", include("allauth.socialaccount.providers.github.urls")),
    path("accounts/", include("allauth.socialaccount.providers.google.urls")),
    path("api/", api.urls),
    path("dashboard/", tarot_views.dashboard, name="dashboard"),
    path("read/", tarot_views.create_reading_view, name="create_reading"),
    path("logout/", tarot_views.HTMXLogoutView.as_view(), name="htmx_logout"),
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

urlpatterns += [path("i18n/", include("django.conf.urls.i18n"))]

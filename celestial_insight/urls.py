from django.contrib import admin
from django.urls import path, include
from celestial_insight.api import api


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/', api.urls),
]

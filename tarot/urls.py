from django.urls import path

from tarot import views

app_name = "tarot"

urlpatterns = [
    path("", views.reading_journey, name="journey"),
    path("readings/claim/", views.claim_readings, name="claim-readings"),
    path("readings/<int:reading_id>/", views.reading_detail, name="reading-detail"),
    path("readings/<int:reading_id>/interpret/", views.reading_interpret, name="reading-interpret"),
    path("readings/<int:reading_id>/retry/", views.reading_retry, name="reading-retry"),
]

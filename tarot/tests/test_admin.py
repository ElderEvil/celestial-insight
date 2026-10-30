import pytest
from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from mentors.models import Mentor
from tarot.admin import ReadingAdmin
from tarot.models import Reading


@pytest.fixture
def mentors(db):
    active = Mentor.objects.create(name="Active Mentor", mystical_level=5, is_active=True)
    inactive = Mentor.objects.create(name="Inactive Mentor", mystical_level=5, is_active=False)
    return active, inactive


@pytest.mark.django_db
def test_assign_random_mentor_filters_on_is_active(monkeypatch, mentors):
    active, inactive = mentors
    reading = Reading.objects.create(question="What does the future hold?")
    model_admin = ReadingAdmin(Reading, AdminSite())

    recorded_messages = []
    monkeypatch.setattr(
        model_admin,
        "message_user",
        lambda request, message, level=None: recorded_messages.append((message, level)),
    )

    request = RequestFactory().post("/admin/tarot/reading/")
    model_admin.assign_random_mentor(request, Reading.objects.filter(pk=reading.pk))

    reading.refresh_from_db()
    assert reading.mentor_id == active.pk
    assert reading.mentor_id != inactive.pk
    assert len(recorded_messages) == 1

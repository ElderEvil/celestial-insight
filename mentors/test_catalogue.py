import json
from http import HTTPStatus
from pathlib import Path

import pytest
from django.core.management import call_command

from mentors.models import Mentor

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "mentor_data.json"
MANAGED_IMAGE_ROOT = Path(__file__).resolve().parents[1] / "tarot" / "static"


def test_launch_fixture_has_complete_bilingual_product_owned_content():
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    assert fixture
    for item in fixture:
        fields = item["fields"]
        assert fields["is_active"]
        assert fields["biography_en"]
        assert fields["biography_uk"]
        assert fields["style_instruction"]
        assert fields["managed_image_path"].startswith("mentors/")
        assert (MANAGED_IMAGE_ROOT / fields["managed_image_path"]).is_file()
        assert fields["content_source"].startswith("celestial-neutral/")
        assert fields["avatar_url"] == ""


@pytest.mark.django_db
def test_seed_demo_loads_curated_mentor_catalogue_idempotently():
    expected_mentor_count = 3
    call_command("seed_demo", verbosity=0)
    first_count = Mentor.objects.filter(is_active=True).count()
    call_command("seed_demo", verbosity=0)

    assert first_count == expected_mentor_count
    assert Mentor.objects.filter(is_active=True).count() == first_count
    assert not Mentor.objects.filter(is_active=True, avatar_url__startswith="http").exists()


@pytest.mark.django_db
def test_mentor_api_serializes_localized_managed_content(client):
    call_command("seed_demo", verbosity=0)

    response = client.get("/api/mentors/")

    assert response.status_code == HTTPStatus.OK
    for mentor in response.json():
        assert mentor["biography_en"]
        assert mentor["biography_uk"]
        assert mentor["style_instruction"]
        assert mentor["managed_image_path"].startswith("mentors/")
        assert mentor["avatar_url"] == ""

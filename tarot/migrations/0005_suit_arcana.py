# Generated by Django 5.1.4 on 2025-01-03 22:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tarot", "0004_reading_celestial_insight"),
    ]

    operations = [
        migrations.AddField(
            model_name="suit",
            name="arcana",
            field=models.CharField(choices=[("major", "Major"), ("minor", "Minor")], default="minor", max_length=10),
        ),
    ]
